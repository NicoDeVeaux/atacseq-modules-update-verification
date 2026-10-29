#!/usr/bin/env python3
"""Check public artifact bytes; this does not repeat private provenance checks."""
import argparse,hashlib,json
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--bundle',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--manifest',default='observed/PUBLIC-MANIFEST.json');a=p.parse_args();root=a.bundle.resolve()
manifest=json.loads((root/a.manifest).read_text());errors=[]
for rel,record in manifest['files'].items():
 path=root/rel
 if not path.resolve().is_relative_to(root) or path.is_symlink() or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=record['sha256']:errors.append(rel)
print(json.dumps({'verified_public_files':len(manifest['files'])-len(errors),'errors':errors,'scope':'Public bytes, separate from original private launch/Platform audit'}));raise SystemExit(bool(errors))
