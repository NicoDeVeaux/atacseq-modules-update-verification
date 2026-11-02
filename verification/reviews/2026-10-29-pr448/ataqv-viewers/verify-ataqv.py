#!/usr/bin/env python3
"""Verify ataqv resource archive bytes and members without extraction or execution."""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import tarfile
import tempfile


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def safe_path(name):
    if (not isinstance(name, str) or not name.startswith('files/')
            or any(part in ('', '.', '..') for part in name.split('/'))
            or '\\' in name or ':' in name or re.search(r'%[0-9a-fA-F]{2}', name)
            or any(ord(c) < 32 or ord(c) == 127 for c in name)):
        raise ValueError('unsafe member path')
    return name


def verify(root, archive_file=None, manifest_sha256=None):
    root = Path(root)
    metadata = root / 'ataqv-viewer-manifest.json'
    if metadata.is_symlink() or not metadata.is_file():
        raise ValueError('missing or nonregular manifest')
    if manifest_sha256 is not None and digest(metadata) != manifest_sha256:
        raise ValueError('manifest SHA-256 mismatch')
    manifest = json.loads(metadata.read_text())
    if manifest['schema'] != 'pr448/ataqv-viewer-resources/v1':
        raise ValueError('unknown manifest schema')
    for license_record in manifest.get('license_files', []):
        if license_record['path'] != 'ATAQV-LICENSE.txt':
            raise ValueError('unexpected license path')
        license_path = root / license_record['path']
        if (license_path.is_symlink() or not license_path.is_file()
                or license_path.stat().st_size != license_record['bytes']
                or digest(license_path) != license_record['sha256']):
            raise ValueError('license file size/hash mismatch')
    archive = Path(archive_file) if archive_file is not None else root / 'ataqv-viewer-resources.tar.gz'
    if archive.is_symlink() or not archive.is_file():
        raise ValueError('missing or nonregular archive')
    if archive.stat().st_size != manifest['archive']['bytes'] or digest(archive) != manifest['archive']['sha256']:
        raise ValueError('compressed archive size/hash mismatch')
    expected = {}
    for record in manifest['members']:
        name = safe_path(record['path'])
        if name in expected:
            raise ValueError('duplicate manifest member')
        if type(record['published_bytes']) is not int or record['published_bytes'] < 0:
            raise ValueError('invalid member size')
        if not re.fullmatch('[0-9a-f]{64}', record['published_sha256']):
            raise ValueError('invalid member hash')
        expected[name] = record
    seen = set()
    size = 0
    with archive.open('rb') as source:
        with tarfile.open(fileobj=source, mode='r|gz') as tar:
            for member in tar:
                name = safe_path(member.name)
                if (not member.isfile() or member.mode != 0o644 or member.uid != 0 or member.gid != 0
                        or member.mtime != 0 or member.uname or member.gname):
                    raise ValueError('nonregular or nonnormalized TAR member')
                if name not in expected or name in seen:
                    raise ValueError('unexpected or duplicate archive member')
                record = expected[name]
                if member.size != record['published_bytes']:
                    raise ValueError('member size mismatch')
                value = hashlib.sha256()
                with tar.extractfile(member) as stream:
                    for block in iter(lambda: stream.read(1024 * 1024), b''):
                        value.update(block)
                if value.hexdigest() != record['published_sha256']:
                    raise ValueError('member SHA-256 mismatch')
                seen.add(name)
                size += member.size
    if seen != set(expected) or len(seen) != manifest['member_count'] or size != manifest['published_bytes']:
        raise ValueError('member inventory or totals mismatch')
    return {'members': len(seen), 'published_bytes': size, 'archive_bytes': archive.stat().st_size,
            'verified_license_files': len(manifest.get('license_files', [])),
            'archive_sha256': manifest['archive']['sha256'], 'manifest_sha256': digest(metadata)}


def self_test():
    with tempfile.TemporaryDirectory(prefix='pr448-ataqv-verifier-') as temporary:
        root = Path(temporary)
        name = 'files/case/report.txt'
        payload = b'actual data\n'
        member = {'path': name, 'published_bytes': len(payload), 'published_sha256': hashlib.sha256(payload).hexdigest()}

        def build(items):
            archive = root / 'ataqv-viewer-resources.tar.gz'
            with archive.open('wb') as output:
                with gzip.GzipFile(fileobj=output, filename='', mode='wb', mtime=0) as zipped:
                    with tarfile.open(fileobj=zipped, mode='w|', format=tarfile.USTAR_FORMAT) as tar:
                        for path, data in items:
                            info = tarfile.TarInfo(path)
                            info.mode = 0o644
                            if data is None:
                                info.type = tarfile.SYMTYPE
                                info.linkname = 'report.txt'
                                tar.addfile(info)
                            else:
                                info.size = len(data)
                                tar.addfile(info, io.BytesIO(data))
            metadata = {'schema': 'pr448/ataqv-viewer-resources/v1', 'archive': {'bytes': archive.stat().st_size, 'sha256': digest(archive)},
                        'member_count': 1, 'published_bytes': len(payload), 'members': [member]}
            (root / 'ataqv-viewer-manifest.json').write_text(json.dumps(metadata))

        controls = []

        def rejects(label):
            try:
                verify(root)
            except ValueError:
                controls.append(label)
            else:
                raise AssertionError('accepted invalid fixture: ' + label)

        build([(name, payload)])
        verify(root)
        archive = root / 'ataqv-viewer-resources.tar.gz'
        data = archive.read_bytes()
        archive.write_bytes(b'X' + data[1:])
        rejects('compressed same-size corruption')
        build([(name, b'X' + payload[1:])])
        rejects('member same-size corruption')
        build([])
        rejects('missing member')
        build([(name, payload), ('files/case/extra.txt', b'extra')])
        rejects('extra member')
        build([(name, payload), (name, payload)])
        rejects('duplicate member')
        build([(name, None)])
        rejects('TAR symlink')
        build([('../escape', payload)])
        rejects('parent traversal')
        build([(name, payload)])
        license_path = root / 'ATAQV-LICENSE.txt'
        license_path.write_bytes(b'license text')
        metadata_path = root / 'ataqv-viewer-manifest.json'
        metadata = json.loads(metadata_path.read_text())
        metadata['license_files'] = [{'path': license_path.name, 'bytes': license_path.stat().st_size, 'sha256': digest(license_path)}]
        metadata_path.write_text(json.dumps(metadata))
        verify(root)
        license_path.write_bytes(b'Xicense text')
        rejects('license same-size corruption')
        license_path.write_bytes(b'license text')
        try:
            verify(root, manifest_sha256='0' * 64)
        except ValueError:
            controls.append('wrong manifest pin')
        else:
            raise AssertionError('accepted wrong manifest pin')
        return {'positive_fixture': 'PASS', 'negative_controls_rejected': controls}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument('--archive-file', type=Path)
    parser.add_argument('--manifest-sha256')
    parser.add_argument('--self-test', action='store_true')
    options = parser.parse_args()
    try:
        result = self_test() if options.self_test else verify(options.root, options.archive_file, options.manifest_sha256)
    except (ValueError, KeyError, OSError, TypeError, tarfile.TarError) as error:
        parser.exit(1, str(error) + '\n')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
