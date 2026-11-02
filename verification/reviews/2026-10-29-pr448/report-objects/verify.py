#!/usr/bin/env python3
"""Stream and verify the exact supplement inventory without extracting artifacts."""
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
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def safe_path(name, prefix):
    if (not isinstance(name, str) or not name.startswith(prefix + '/')
            or any(part in ('', '.', '..') for part in name.split('/'))
            or '\\' in name or ':' in name or re.search(r'%[0-9a-fA-F]{2}', name)
            or any(ord(c) < 32 or ord(c) == 127 for c in name)):
        raise ValueError('unsafe archive path')
    return name


class PartsReader(io.RawIOBase):
    def __init__(self, paths):
        self.paths = iter(paths)
        self.current = None

    def readable(self):
        return True

    def readinto(self, buffer):
        count = 0
        while count < len(buffer):
            if self.current is None:
                try:
                    self.current = next(self.paths).open('rb')
                except StopIteration:
                    break
            chunk = self.current.read(len(buffer) - count)
            if not chunk:
                self.current.close()
                self.current = None
                continue
            buffer[count:count + len(chunk)] = chunk
            count += len(chunk)
        return count

    def close(self):
        if self.current is not None:
            self.current.close()
        super().close()


def verify(root, archive_sha256=None, archive_file=None):
    root = Path(root)
    if archive_file is None and (root / 'parts').is_symlink():
        raise ValueError('symlink parts directory')
    archive_path = root / 'archive.json'
    if archive_sha256 is not None and digest(archive_path) != archive_sha256:
        raise ValueError('archive manifest SHA-256 mismatch')
    archive = json.loads(archive_path.read_text())
    manifest = json.loads((root / 'manifest.json').read_text())
    if (archive['schema'] != 'pr448/public-decoded-report-archive/v1'
            or manifest['schema'] != 'pr448/public-decoded-report-supplement/v1'):
        raise ValueError('unknown manifest schema')
    if digest(root / 'manifest.json') != archive['member_manifest_sha256']:
        raise ValueError('member manifest SHA-256 mismatch')
    expected = {}
    for record in manifest['members']:
        name = safe_path(record['path'], 'files')
        if name in expected:
            raise ValueError('duplicate manifest member')
        if type(record['published_bytes']) is not int or record['published_bytes'] < 0:
            raise ValueError('invalid member size')
        if not re.fullmatch('[0-9a-f]{64}', record['published_sha256']):
            raise ValueError('invalid member hash')
        expected[name] = record
    if archive_file is not None:
        target = Path(archive_file)
        if target.is_symlink() or not target.is_file():
            raise ValueError('missing or nonregular complete archive')
        full_size = target.stat().st_size
        full_digest = digest(target)
        paths = [target]
    else:
        paths = []
        full_hash = hashlib.sha256()
        full_size = 0
        part_names = set()
        for record in archive['parts']:
            name = safe_path(record['path'], 'parts')
            if name in part_names or len(name.split('/')) != 2:
                raise ValueError('invalid or duplicate part path')
            part_names.add(name)
            target = root / name
            if target.is_symlink() or not target.is_file():
                raise ValueError('missing or nonregular part')
            if not 0 < record['bytes'] <= archive['maximum_part_bytes']:
                raise ValueError('invalid part size')
            if target.stat().st_size != record['bytes']:
                raise ValueError('part size mismatch')
            part_hash = hashlib.sha256()
            with target.open('rb') as stream:
                for block in iter(lambda: stream.read(1024 * 1024), b''):
                    part_hash.update(block)
                    full_hash.update(block)
                    full_size += len(block)
            if part_hash.hexdigest() != record['sha256']:
                raise ValueError('part SHA-256 mismatch')
            paths.append(target)
        actual_parts = set()
        for target in (root / 'parts').rglob('*'):
            if target.is_symlink() or not target.is_file():
                raise ValueError('nonregular or nested part entry')
            actual_parts.add(target.relative_to(root).as_posix())
        if actual_parts != part_names:
            raise ValueError('part inventory mismatch')
        full_digest = full_hash.hexdigest()
    if full_size != archive['archive_bytes'] or full_digest != archive['archive_sha256']:
        raise ValueError('concatenated archive mismatch')
    seen = set()
    total = 0
    with io.BufferedReader(PartsReader(paths)) as stream:
        with tarfile.open(fileobj=stream, mode='r|gz') as tar:
            for member in tar:
                name = safe_path(member.name, 'files')
                if (not member.isfile() or member.mode != 0o644 or member.uid != 0 or member.gid != 0
                        or member.mtime != 0 or member.uname or member.gname):
                    raise ValueError('nonregular or nonnormalized TAR member')
                if name in seen or name not in expected:
                    raise ValueError('unexpected or duplicate archive member')
                seen.add(name)
                record = expected[name]
                if member.size != record['published_bytes']:
                    raise ValueError('member size mismatch: ' + name)
                value = hashlib.sha256()
                with tar.extractfile(member) as payload:
                    for block in iter(lambda: payload.read(1024 * 1024), b''):
                        value.update(block)
                if value.hexdigest() != record['published_sha256']:
                    raise ValueError('member SHA-256 mismatch: ' + name)
                total += member.size
    if seen != set(expected):
        raise ValueError('archive member inventory mismatch')
    if len(seen) != manifest['member_count'] or total != manifest['published_bytes']:
        raise ValueError('manifest totals mismatch')
    return {'members': len(seen), 'published_bytes': total, 'archive_bytes': full_size,
            'archive_input': 'single_file' if archive_file is not None else 'split_parts',
            'archive_manifest_sha256': digest(archive_path), 'member_manifest_sha256': digest(root / 'manifest.json')}


def self_test():
    with tempfile.TemporaryDirectory(prefix='pr448-supplement-verifier-') as temporary:
        root = Path(temporary)
        (root / 'parts').mkdir()
        data = b'valid report\n'
        name = 'files/case/report.txt'
        manifest = {'schema': 'pr448/public-decoded-report-supplement/v1', 'member_count': 1,
                    'published_bytes': len(data), 'members': [{'path': name, 'published_bytes': len(data),
                    'published_sha256': hashlib.sha256(data).hexdigest()}]}
        (root / 'manifest.json').write_text(json.dumps(manifest))

        def archive_with(items):
            raw = io.BytesIO()
            with gzip.GzipFile(fileobj=raw, mode='wb', mtime=0, filename='') as zipped:
                with tarfile.open(fileobj=zipped, mode='w|', format=tarfile.USTAR_FORMAT) as tar:
                    for path, payload in items:
                        info = tarfile.TarInfo(path)
                        info.mode = 0o644
                        if payload is None:
                            info.type = tarfile.SYMTYPE
                            info.linkname = 'report.txt'
                            tar.addfile(info)
                        else:
                            info.size = len(payload)
                            tar.addfile(info, io.BytesIO(payload))
            part = root / 'parts/test.part'
            part.write_bytes(raw.getvalue())
            description = {'schema': 'pr448/public-decoded-report-archive/v1', 'member_manifest_sha256': digest(root / 'manifest.json'),
                           'maximum_part_bytes': 45088768, 'archive_bytes': part.stat().st_size,
                           'archive_sha256': digest(part), 'parts': [{'path': 'parts/test.part', 'bytes': part.stat().st_size, 'sha256': digest(part)}]}
            (root / 'archive.json').write_text(json.dumps(description))

        controls = []

        def rejects(label):
            try:
                verify(root)
            except ValueError:
                controls.append(label)
            else:
                raise AssertionError('accepted invalid fixture: ' + label)

        archive_with([(name, data)])
        verify(root)
        part = root / 'parts/test.part'
        blob = part.read_bytes()
        whole = root / 'whole.tar.gz'
        whole.write_bytes(blob)
        verify(root, archive_file=whole)
        whole.write_bytes(b'X' + blob[1:])
        try:
            verify(root, archive_file=whole)
        except ValueError:
            controls.append('complete archive same-size corruption')
        else:
            raise AssertionError('accepted corrupt complete archive')
        part.write_bytes(b'X' + blob[1:])
        rejects('compressed same-size corruption')
        archive_with([(name, b'X' + data[1:])])
        rejects('member same-size corruption')
        archive_with([])
        rejects('missing archive member')
        archive_with([(name, data), ('files/case/extra.txt', b'extra')])
        rejects('unexpected archive member')
        archive_with([(name, data), (name, data)])
        rejects('duplicate archive member')
        archive_with([(name, None)])
        rejects('TAR symlink')
        archive_with([(name, data)])
        (root / 'parts/extra.part').write_bytes(b'extra')
        rejects('unexpected part')
        (root / 'parts/extra.part').unlink()
        try:
            verify(root, '0' * 64)
        except ValueError:
            controls.append('wrong archive-manifest pin')
        else:
            raise AssertionError('accepted wrong archive-manifest pin')
        return {'positive_fixture': 'PASS', 'single_file_positive_fixture': 'PASS', 'negative_controls_rejected': controls}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument('--archive-manifest-sha256')
    parser.add_argument('--archive-file', type=Path, help='Verify the complete gzip file instead of split parts')
    parser.add_argument('--self-test', action='store_true')
    options = parser.parse_args()
    try:
        result = self_test() if options.self_test else verify(options.root, options.archive_manifest_sha256, options.archive_file)
    except (ValueError, KeyError, OSError, TypeError, tarfile.TarError) as error:
        parser.exit(1, str(error) + '\n')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
