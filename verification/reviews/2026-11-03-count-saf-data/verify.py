#!/usr/bin/env python3
"""Verify the exact selected count/SAF data inventory and hashes."""
import hashlib,json
from pathlib import Path

def main():
    root=Path(__file__).resolve().parent
    manifest=json.loads((root/'MANIFEST.json').read_text())
    expected=set();total=0
    for member in manifest['files']:
        name=member['path']
        assert name.startswith('files/') and all(p not in ('','.','..')for p in name.split('/')) and '\\'not in name and ':'not in name
        assert name not in expected
        expected.add(name);path=root/name
        assert path.is_file() and not path.is_symlink() and path.stat().st_size==member['published_bytes'],name
        data=path.read_bytes()
        assert hashlib.sha256(data).hexdigest()==member['published_sha256'],name
        scientific=b''.join(line for line in data.splitlines(keepends=True)if not line.startswith(b'#'))
        assert hashlib.sha256(scientific).hexdigest()==member['noncomment_sha256'],name
        total+=len(data)
    actual=set()
    for path in(root/'files').rglob('*'):
        assert not path.is_symlink()
        if path.is_file():actual.add(path.relative_to(root).as_posix())
        else:assert path.is_dir()
    assert actual==expected and len(expected)==manifest['file_count']and total==manifest['published_bytes']
    print(json.dumps({'files':len(expected),'published_bytes':total,'integrity':'PASS','noncomment_byte_hashes':'PASS'}))

if __name__=='__main__':main()
