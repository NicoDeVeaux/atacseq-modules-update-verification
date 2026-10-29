#!/usr/bin/env python3
"""Verify public byte integrity and the exported audit/test coverage offline."""
import hashlib,json,re,stat,xml.etree.ElementTree as ET
from pathlib import Path,PurePosixPath
ROOT=Path(__file__).resolve().parent
MANIFEST=ROOT/'PUBLIC-MANIFEST.json'
def sha(data):return hashlib.sha256(data).hexdigest()
def load(path):return json.loads((ROOT/path).read_text())
def verify():
 manifest=load('PUBLIC-MANIFEST.json');files=manifest['files'];assert isinstance(files,dict) and 'PUBLIC-MANIFEST.json' not in files
 actual={str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file()};assert actual==set(files)|{'PUBLIC-MANIFEST.json'},'Unexpected or missing package file'
 total=0
 for name,row in files.items():
  rel=PurePosixPath(name);assert not rel.is_absolute() and '..' not in rel.parts
  p=ROOT/name;assert not p.is_symlink() and stat.S_ISREG(p.lstat().st_mode)
  raw=p.read_bytes();assert len(raw)==row['bytes'] and sha(raw)==row['sha256'],name
  assert len(raw)<=43*1024**2;raw.decode('utf-8');total+=len(raw)
  assert not re.search(rb'/(?:Users|home)/[^/\s"\'<>]+|/(?:private/)?tmp/[^/\s"\'<>]+|\x1b|arn:(?:aws|aws-cn|aws-us-gov):',raw),name
  assert (b's3:'+b'//') not in raw,name
  assert not re.search(rb'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b|\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b|\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b',raw),name
 assert total==manifest['total_listed_bytes'] and total<=100*1024**2
 inventory=load('module-version-audit/inventory.json');coverage=load('module-version-audit/coverage.json');history=load('module-version-audit/nfcore-history.json');sub=load('module-version-audit/nfcore-subworkflow-history.json')
 changed={x for r in inventory['records'] for x in r['changed_files']};assert len(changed)==267 and len(inventory['records'])==70
 assert len(coverage['changed_dependencies'])==16 and len(history['modules'])==36 and len(sub['subworkflows'])==7
 for row in coverage['evidence']:
  public=files['module-version-audit/'+row['path']];assert public['original_sha256']==row['sha256'] and public['original_bytes']==row['bytes']
 expected={'PUBLIC-SUMMARY.md','gffread_safe_smoke.py','safe-smoke/input.gff3','safe-smoke/output.gtf','safe-smoke/smoke.json','safe-smoke/environment.yml'}
 assert {x.removeprefix('annotation-matrix/') for x in files if x.startswith('annotation-matrix/')}==expected
 suite=ET.parse(ROOT/'gffread-suite/final.xml').getroot().find('testsuite');assert suite is not None and suite.attrib['tests']=='9' and suite.attrib['failures']=='0' and suite.attrib['skipped']=='0'
 assert len(suite.findall('testcase'))==9
 result=load('gffread-suite/result.json');assert result['tests']==9 and result['failed']==0 and result['skipped']==0 and result['strict_ci_without_snapshot_update'] is True
 raw=load('gffread-suite/candidate/main.nf.test.snap');fork=load('source-fork/modules/nf-core/gffread/tests/main.nf.test.snap');assert raw==fork
 assert (ROOT/'gffread-suite/module/main.nf').read_bytes()==(ROOT/'source-fork/modules/nf-core/gffread/main.nf').read_bytes()
 assert 'nft-utils@0.0.9' in (ROOT/'gffread-suite/nf-test.config').read_text() and 'nft-utils@0.0.3' in (ROOT/'source-fork/nf-test.config').read_text()
 inputs=load('gffread-suite/input-provenance.json')
 for row in inputs['test_inputs']:
  p=ROOT/'gffread-suite/data/genomics/sarscov2/genome'/row['url'].rsplit('/',1)[-1];assert p.stat().st_size==row['bytes'] and sha(p.read_bytes())==row['sha256']
 source=load('SOURCE-MAP.json')
 for name,row in source['files'].items():assert row==files[name]
 print(json.dumps({'state':'PUBLIC_PACKAGE_VERIFIED','files':len(files),'bytes':total,'changed_files':267,'components':70,'changed_dependencies':16,'module_histories':36,'subworkflow_histories':7,'gffread_tests':9,'snapshot_json_equal':True,'scientific_execution':False},indent=2))
if __name__=='__main__':verify()
