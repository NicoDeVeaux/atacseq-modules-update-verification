#!/usr/bin/env python3
"""Verify the distributed PR448 bytes and optional cloud archive contents."""
import argparse,hashlib,io,json,os,re,stat,tarfile
from pathlib import Path,PurePosixPath
ROOT=Path(__file__).resolve().parent
def digest(path):
    h=hashlib.sha256()
    with path.open('rb')as stream:
        for block in iter(lambda:stream.read(1048576),b''):h.update(block)
    return h.hexdigest()
def verify(root,deep=False):
    root=root.resolve()
    manifest=json.loads((root/'PUBLIC-MANIFEST.json').read_text())
    if not isinstance(manifest.get('files'),dict)or not manifest['files']:
        raise ValueError('Missing artifact manifest')
    actual=set()
    for parent,dirs,names in os.walk(root,followlinks=False):
        for name in dirs:
            if (Path(parent)/name).is_symlink():raise ValueError('Symlink directory in bundle')
        dirs[:]=[name for name in dirs if name!='__pycache__']
        for name in names:
            path=Path(parent)/name
            if path.is_symlink()or not stat.S_ISREG(path.lstat().st_mode):raise ValueError('Nonregular bundle file')
            relative=path.relative_to(root).as_posix()
            if relative!='PUBLIC-MANIFEST.json':actual.add(relative)
    if actual!=set(manifest['files']):raise ValueError('Bundle file inventory differs from manifest')
    for name,row in manifest['files'].items():
        parts=PurePosixPath(name)
        if parts.is_absolute()or'..'in parts.parts or'\\'in name or name!=parts.as_posix():raise ValueError('Unsafe artifact path')
        if type(row.get('bytes'))is not int or not 0<=row['bytes']<=50*1024**2 or not re.fullmatch('[0-9a-f]{64}',row.get('sha256','')):raise ValueError('Invalid artifact metadata')
        path=root/name
        if path.is_symlink()or not path.resolve().is_relative_to(root)or path.stat().st_size!=row['bytes']or digest(path)!=row['sha256']:
            raise ValueError('Artifact mismatch: '+name)
    total=0
    if deep:
        for record in json.loads((root/'hiv/CLOUD-ARCHIVES.json').read_text())['archives']:
            paths=[p['path']for p in record['parts']]
            if not paths or len(paths)!=len(set(paths))or any(p not in manifest['files']for p in paths):raise ValueError('Invalid cloud part list')
            raw=b''.join((root/name).read_bytes()for name in paths)
            if hashlib.sha256(raw).hexdigest()!=record['sha256']:raise ValueError('Joined cloud archive differs')
            if record['member_manifest']not in manifest['files']:raise ValueError('Unlisted cloud member manifest')
            listed=json.loads((root/record['member_manifest']).read_text())['members']
            expected={r['path']:r for r in listed};seen=set()
            if len(expected)!=len(listed):raise ValueError('Duplicate cloud manifest member')
            with tarfile.open(fileobj=io.BytesIO(raw),mode='r:gz')as archive:
                for member in archive:
                    path=PurePosixPath(member.name)
                    if not member.isfile()or member.name in seen or path.is_absolute()or'..'in path.parts or member.name not in expected or member.size!=expected[member.name]['bytes']or member.size>50000000:
                        raise ValueError('Invalid cloud archive member')
                    seen.add(member.name)
                    body=archive.extractfile(member).read()
                    if hashlib.sha256(body).hexdigest()!=expected[member.name]['sha256']:raise ValueError('Cloud member differs')
                    total+=1
            if seen!=set(expected):raise ValueError('Missing cloud archive members')
    return {'public_files_verified':len(manifest['files']),'cloud_members_verified':total,'mismatches':0}
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--deep',action='store_true');args=parser.parse_args()
    print(json.dumps(verify(ROOT,args.deep)))
if __name__=='__main__':main()
