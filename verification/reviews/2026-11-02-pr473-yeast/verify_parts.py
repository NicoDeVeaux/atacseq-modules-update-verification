#!/usr/bin/env python3
"""Verify public bytes and every archive member offline without extraction."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import sys
import tarfile

LIMIT = 43 * 1024**2


def require(ok, message):
    if not ok:
        raise ValueError(message)


def safe_name(value):
    p = PurePosixPath(value)
    require(isinstance(value, str) and value and '\\' not in value and
            not any(ord(c) < 32 for c in value),
            'Invalid public path')
    require(not p.is_absolute() and '..' not in p.parts and '.' not in p.parts,
            'Unsafe public path')
    require(str(p) == value and not value.endswith('/'), 'Noncanonical public path')
    return value


def digest_file(path):
    h, size = hashlib.sha256(), 0
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024**2), b''):
            h.update(block)
            size += len(block)
    return size, h.hexdigest()


class JoinedParts:
    def __init__(self, paths):
        self.paths, self.stream = iter(paths), None

    def read(self, size):
        require(size >= 0, 'Unbounded joined read')
        pieces, remaining = [], size
        while remaining:
            if self.stream is None:
                try:
                    self.stream = next(self.paths).open('rb')
                except StopIteration:
                    break
            block = self.stream.read(remaining)
            if not block:
                self.stream.close()
                self.stream = None
                continue
            pieces.append(block)
            remaining -= len(block)
        return b''.join(pieces)

    def close(self):
        if self.stream is not None:
            self.stream.close()


def verify(root):
    root = Path(root).resolve()
    public = json.loads((root / 'PUBLIC-MANIFEST.json').read_text())
    require(public['schema'] == 'pr473-public-files/v1', 'Unknown public schema')
    public_rows = public['files']
    names = [safe_name(row['path']) for row in public_rows]
    require(len(names) == len(set(names)), 'Duplicate public inventory path')
    actual = set()
    for path in root.rglob('*'):
        require(not path.is_symlink(), 'Public symlink')
        if path.is_file():
            actual.add(path.relative_to(root).as_posix())
    require(actual == set(names) | {'PUBLIC-MANIFEST.json'}, 'Public file inventory differs')
    for row in public_rows:
        require(digest_file(root / row['path']) == (row['bytes'], row['sha256']),
                'Public file checksum/size differs: ' + row['path'])

    manifest = json.loads((root / 'parts-manifest.json').read_text())
    require(manifest['schema'] == 'pr473-yeast-distribution/v1', 'Unknown archive schema')
    prefix = safe_name(manifest['archive_prefix'])
    require('/' not in prefix, 'Archive prefix must be one component')
    index_name = safe_name(manifest['member_index'])
    index_path = root / index_name
    require(digest_file(index_path)[1] == manifest['member_index_sha256'],
            'Member index checksum differs')
    rows = [json.loads(line) for line in index_path.read_text().splitlines()]
    expected = {}
    for row in rows:
        name = safe_name(row['member'])
        require(name == prefix or name.startswith(prefix + '/'), 'Member outside archive root')
        require(name not in expected, 'Duplicate indexed member')
        require(row['type'] in ('file', 'directory'), 'Unsupported indexed member type')
        expected[name] = row
    require(len(rows) == manifest['total_members'], 'Member index cardinality differs')
    require(sum(row['type'] == 'file' for row in rows) == manifest['source_files'],
            'Source file count differs')
    source_record = expected.get(prefix + '/ARTIFACTS.jsonl', {})
    require(source_record.get('sha256') == manifest['source_ARTIFACTS_sha256'],
            'Source artifact index identity differs')
    require(0 < manifest['part_size_limit_bytes'] <= LIMIT, 'Unsafe part limit')
    require(manifest['parts'], 'No archive parts')
    parts, joined_sha, joined_bytes = [], hashlib.sha256(), 0
    for number, row in enumerate(manifest['parts'], 1):
        name = 'parts/' + manifest['archive_name'] + '.part-' + str(number).zfill(4)
        require(row['path'] == name, 'Part sequence/name differs')
        require(0 < row['bytes'] <= manifest['part_size_limit_bytes'], 'Invalid part size')
        if number < len(manifest['parts']):
            require(row['bytes'] == manifest['part_size_limit_bytes'], 'Nonfinal part is short')
        path = root / safe_name(name)
        require(path.is_file() and not path.is_symlink(), 'Part missing or symlinked')
        part_sha, size = hashlib.sha256(), 0
        with path.open('rb') as stream:
            for block in iter(lambda: stream.read(4 * 1024**2), b''):
                part_sha.update(block)
                joined_sha.update(block)
                size += len(block)
        require(size == row['bytes'] and part_sha.hexdigest() == row['sha256'],
                'Part checksum/size differs')
        joined_bytes += size
        parts.append(path)
    require({x.relative_to(root).as_posix() for x in (root / 'parts').iterdir()} ==
            {row['path'] for row in manifest['parts']}, 'Unexpected/missing part')
    require(joined_bytes == manifest['archive_bytes'] and
            joined_sha.hexdigest() == manifest['archive_sha256'], 'Joined archive identity differs')

    joined, seen, files, unpacked = JoinedParts(parts), set(), 0, 0
    artifact_bytes = None
    try:
        with tarfile.open(fileobj=joined, mode='r|gz') as archive:
            for member in archive:
                name = member.name.rstrip('/') if member.isdir() else member.name
                require(name in expected and name not in seen, 'Unexpected/duplicate archive member')
                seen.add(name)
                row = expected[name]
                require(member.uid == member.gid == member.mtime == 0 and
                        not member.uname and not member.gname and not member.pax_headers,
                        'Tar metadata is not normalized')
                require(member.mode == int(row['mode'], 8), 'Tar mode differs')
                if row['type'] == 'directory':
                    require(member.isdir(), 'Member type differs')
                else:
                    require(member.isfile() and member.size == row['bytes'], 'Member type/size differs')
                    h, captured = hashlib.sha256(), bytearray()
                    with archive.extractfile(member) as stream:
                        for block in iter(lambda: stream.read(4 * 1024**2), b''):
                            h.update(block)
                            if name == prefix + '/ARTIFACTS.jsonl':
                                require(len(captured) + len(block) <= 64 * 1024**2,
                                        'Artifact index unexpectedly large')
                                captured.extend(block)
                    require(h.hexdigest() == row['sha256'], 'Member content differs: ' + name)
                    if name == prefix + '/ARTIFACTS.jsonl':
                        artifact_bytes = bytes(captured)
                    files += 1
                    unpacked += member.size
    finally:
        joined.close()
    require(seen == expected.keys(), 'Missing archive members')
    require(artifact_bytes is not None, 'Missing source artifact index')
    artifacts = [json.loads(line) for line in artifact_bytes.decode().splitlines()]
    payload = {x['member']: x for x in artifacts if x['disposition'] != 'exclude'}
    require(len(payload) == sum(x['disposition'] != 'exclude' for x in artifacts),
            'Duplicate source artifact member')
    require(set(payload) == {name for name, row in expected.items()
                             if row['type'] == 'file' and name != prefix + '/ARTIFACTS.jsonl'},
            'Artifact index does not cover payload exactly')
    for name, row in payload.items():
        require(row['public_sha256'] == expected[name]['sha256'] and
                row['public_bytes'] == expected[name]['bytes'], 'Artifact public identity differs')
        if row['kind'] == 'scientific':
            require(row['disposition'] == 'exact' and row['source_sha256'] == row['public_sha256'] and
                    row['source_bytes'] == row['public_bytes'], 'Scientific bytes were changed')
    return {'verified_parts': len(parts), 'verified_regular_files': files,
            'verified_total_members': len(seen), 'joined_archive_bytes': joined_bytes,
            'joined_archive_sha256': joined_sha.hexdigest(), 'unpacked_file_bytes': unpacked,
            'all_member_hashes_match': True, 'all_public_file_hashes_match': True,
            'scientific_byte_preservation_checked': True,
            'meaning': 'Integrity/inventory verification only; no scientific result was validated',
            'scientific_runs': 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument('--receipt', type=Path, help='Optional new receipt outside the public bundle')
    args = parser.parse_args()
    record = verify(args.root)
    if args.receipt:
        require(not args.receipt.exists(), 'Refusing to overwrite receipt')
        require(not args.receipt.resolve().is_relative_to(args.root.resolve()),
                'Receipt must not mutate the sealed bundle')
        with args.receipt.open('x') as stream:
            json.dump(record, stream, indent=2)
            stream.write('\n')
    print(json.dumps(record, indent=2))


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print('Verification failed: ' + str(exc), file=sys.stderr)
        raise SystemExit(1)
