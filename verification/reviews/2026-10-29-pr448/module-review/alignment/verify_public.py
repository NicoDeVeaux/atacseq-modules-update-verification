#!/usr/bin/env python3
"""Verify the explicit public allowlist and bounded decoded privacy checks offline."""
import hashlib,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
import privacy
ROOT=Path(__file__).resolve().parent
def main():
 manifest=json.loads((ROOT/'PUBLIC-MANIFEST.json').read_text());expected=manifest['files'];paths=list(ROOT.rglob('*'))
 if any(p.is_symlink() for p in paths):raise ValueError('PUBLIC_SYMLINK_REFUSED')
 actual={str(p.relative_to(ROOT)) for p in paths if p.is_file()}
 if actual!=set(expected)|{'PUBLIC-MANIFEST.json'}:raise ValueError('PUBLIC_ALLOWLIST_MISMATCH')
 total=0;layers=0
 for name,record in expected.items():
  if not privacy.path_ok(name):raise ValueError('UNSAFE_PUBLIC_PATH')
  path=ROOT/name
  if path.is_symlink() or not path.is_file():raise ValueError('UNSAFE_PUBLIC_FILE')
  raw=path.read_bytes()
  if len(raw)!=record['bytes'] or hashlib.sha256(raw).hexdigest()!=record['sha256']:raise ValueError('PUBLIC_HASH_MISMATCH:'+name)
  if len(raw)>43*1024**2:raise ValueError('PUBLIC_FILE_EXCEEDS_43MIB')
  layers+=len(privacy.audit(raw,name));total+=len(raw)
 if total>150*1024**2:raise ValueError('PUBLIC_PACKAGE_EXCEEDS_150MIB')
 privacy.audit((ROOT/'PUBLIC-MANIFEST.json').read_bytes(),'PUBLIC-MANIFEST.json')
 print(json.dumps({'state':'PASS','files':len(expected),'published_bytes':total,'decoded_archive_layers_checked':layers,'privacy_matches':0,'scientific_tools_executed':False},sort_keys=True))
if __name__=='__main__':main()
