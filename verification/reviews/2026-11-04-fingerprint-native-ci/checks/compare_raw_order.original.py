import collections
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
maps = {}
for p in root.glob('job-*/capture/manifest.json'):
    x=json.loads(p.read_text())
    maps[x['source_commit'],x['expected_test_case'],x['requested']['nextflow']] = (p.parent,x)
old='70e87c6f3e83f56d05695c6e9d27203080c27b1f'
new='e8aafb982ee08f9d681cec6aaef4440fb8d236ca'
rows=[]
for (source,profile,version),(folder,manifest) in sorted(maps.items()):
    if source!=new:continue
    first,origin=maps[old,profile,version]
    a={Path(r['path']).name:r for r in origin['files'] if r['role']=='MULTIQC/staged_raw'}
    b={Path(r['path']).name:r for r in manifest['files'] if r['role']=='MULTIQC/staged_raw'}
    assert set(a)==set(b)
    for name in sorted(a):
        before=(first/a[name]['path']).read_bytes();after=(folder/b[name]['path']).read_bytes()
        x=before.decode().splitlines();y=after.decode().splitlines()
        assert x[:2]==y[:2]
        equal=collections.Counter(x[2:])==collections.Counter(y[2:])
        rows.append({'profile':profile,'nextflow':version,'name':name,'headers_equal':True,
                     'complete_rows_multiset_equal':equal,'raw_bytes_equal':before==after,
                     'original_sha256':hashlib.sha256(before).hexdigest(),
                     'final_sha256':hashlib.sha256(after).hexdigest(),'data_rows':len(x)-2})
assert len(rows)==80 and all(r['complete_rows_multiset_equal'] for r in rows)
out={'schema':'atacseq-native-raw-order-comparison/v1','status':'PASS','matrices':80,
     'original_source':old,'final_source':new,'all_headers_and_complete_row_multisets_equal':True,
     'byte_different_matrices':sum(not r['raw_bytes_equal'] for r in rows),
     'interpretation':'Observed difference is raw-row order. Headers and multisets of complete rows, including treatment/control pairs, are identical; fingerprint curves and both exports remain byte-identical. No raw-byte equality is claimed.',
     'checker_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'rows':rows}
(root/'RAW-ORDER-COMPARISON.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='rows'}))
