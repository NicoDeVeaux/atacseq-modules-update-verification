#!/usr/bin/env python3
"""Verify ordered public archive parts and every member without extracting a copy."""
import hashlib
import json
from pathlib import Path
import re
import sys
import tarfile

ROOT = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


class JoinedParts:
    def __init__(self, paths):
        self.paths = iter(paths)
        self.stream = None

    def read(self, size):
        require(size >= 0, 'Unbounded read is not supported')
        pieces = []
        remaining = size
        while remaining:
            if self.stream is None:
                try:
                    self.stream = next(self.paths).open('rb')
                except StopIteration:
                    break
            data = self.stream.read(remaining)
            if not data:
                self.stream.close()
                self.stream = None
                continue
            pieces.append(data)
            remaining -= len(data)
        return b''.join(pieces)

    def close(self):
        if self.stream is not None:
            self.stream.close()


def main():
    manifest = json.loads((ROOT/'parts-manifest.json').read_text())
    index_path = ROOT/manifest['member_index']
    require(hashlib.sha256(index_path.read_bytes()).hexdigest()==manifest['member_index_sha256'],
            'Member index checksum differs')
    rows = [json.loads(line) for line in index_path.read_text().splitlines()]
    expected = {row['member']:row for row in rows}
    require(len(expected)==len(rows)==manifest['total_members'], 'Member index cardinality differs')
    require(sum(row['type']=='file' for row in rows)==manifest['source_files']==4565,
            'Source file count differs')
    root = manifest['archive_prefix']
    for name in expected:
        require(name==root or name.startswith(root+'/'), 'Member outside archive root')
        require(not Path(name).is_absolute() and '..' not in Path(name).parts, 'Unsafe member path')
    source_manifest = expected.get(root+'/ARTIFACTS.jsonl',{})
    require(source_manifest.get('sha256')==manifest['source_ARTIFACTS_sha256'], 'Source package identity differs')
    parts, joined_sha, joined_bytes = [], hashlib.sha256(), 0
    require(manifest['parts'], 'No parts')
    for position,row in enumerate(manifest['parts'],1):
        expected_name = 'parts/'+manifest['archive_name']+'.part-'+str(position).zfill(4)
        require(row['path']==expected_name, 'Part sequence/name differs')
        require(0<row['bytes']<=manifest['part_size_limit_bytes']<=43*1024**2, 'Part size exceeds43MiB')
        if position<len(manifest['parts']):
            require(row['bytes']==manifest['part_size_limit_bytes'], 'Nonfinal part is short')
        path = ROOT/row['path']
        require(path.is_file() and not path.is_symlink(), 'Part missing or symlinked')
        part_sha, part_bytes = hashlib.sha256(),0
        with path.open('rb') as stream:
            for block in iter(lambda:stream.read(4*1024*1024),b''):
                part_sha.update(block)
                joined_sha.update(block)
                part_bytes += len(block)
        require(part_bytes==row['bytes'] and part_sha.hexdigest()==row['sha256'], 'Part checksum/size differs')
        joined_bytes += part_bytes
        parts.append(path)
    actual = {str(p.relative_to(ROOT)) for p in (ROOT/'parts').iterdir()}
    require(actual=={row['path'] for row in manifest['parts']}, 'Unexpected/missing part files')
    require(joined_bytes==manifest['archive_bytes'] and joined_sha.hexdigest()==manifest['archive_sha256'],
            'Concatenated full archive checksum/size differs')
    seen, files, unpacked = set(),0,0
    joined = JoinedParts(parts)
    try:
        with tarfile.open(fileobj=joined,mode='r|gz') as archive:
            for member in archive:
                name = member.name.rstrip('/') if member.isdir() else member.name
                require(name in expected and name not in seen, 'Unexpected/duplicate tar member')
                seen.add(name)
                row = expected[name]
                require(member.uid==member.gid==member.mtime==0 and member.mode==int(row['mode'],8),
                        'Tar metadata was not normalized')
                require(not member.uname and not member.gname, 'Tar owner name was not normalized')
                if row['type']=='directory':
                    require(member.isdir(), 'Member type differs')
                else:
                    require(member.isfile() and member.size==row['bytes'], 'Member type/size differs')
                    digest = hashlib.sha256()
                    with archive.extractfile(member) as stream:
                        for block in iter(lambda:stream.read(4*1024*1024),b''):
                            digest.update(block)
                    require(digest.hexdigest()==row['sha256'], 'Member content checksum differs')
                    files += 1
                    unpacked += member.size
    finally:
        joined.close()
    require(seen==expected.keys(), 'Missing archive members')
    record = {'verified_parts':len(parts),'verified_regular_files':files,'verified_total_members':len(seen),
              'joined_archive_bytes':joined_bytes,'joined_archive_sha256':joined_sha.hexdigest(),
              'unpacked_file_bytes':unpacked,'source_ARTIFACTS_sha256':manifest['source_ARTIFACTS_sha256'],
              'all_member_hashes_match':True,'normalized_safe_tar_metadata':True,
              'verification':'streamed ordered parts; no second archive or extracted copy','scientific_runs':0}
    (ROOT/'verification.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(record,indent=2))


if __name__=='__main__':
    try:
        main()
    except Exception as exc:
        print('Verification failed: '+str(exc),file=sys.stderr)
        raise SystemExit(1)
