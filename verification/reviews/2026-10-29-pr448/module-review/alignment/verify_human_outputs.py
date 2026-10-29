"""Read-only exact comparisons of the retained human peak files, independent of summary flags."""
import importlib.util,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parent/'human-macs'
spec=importlib.util.spec_from_file_location('retained_macs_comparison',ROOT/'compare.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def main():
 execution=json.loads((ROOT/'execution.json').read_text());result={}
 assert all(v['exit_code']==0 and not v['timed_out'] and v['stderr_io_exception_absent'] for v in execution.values())
 for label,left,right in [('old_vs_new','3.0.1','3.0.4'),('new_vs_archived_cloud','3.0.4','archived-published')]:
  pair={}
  for suffix in ('broadPeak','gappedPeak','xls'):
   a=m.rows(ROOT/left/(m.PREFIX+'.'+suffix));b=m.rows(ROOT/right/(m.PREFIX+'.'+suffix))
   if suffix=='xls':assert a[0]==b[0];a=a[1:];b=b[1:]
   assert len(a)==len(b)==30438
   if label=='old_vs_new' and suffix=='gappedPeak':
    assert all(x[:6]+x[8:]==y[:6]+y[8:] and y[6:8]==['0','0'] for x,y in zip(a,b));pair[suffix]='ONLY_FIELDS_7_8_CHANGE'
   else:assert a==b;pair[suffix]='ALL_EMITTED_FIELDS_EXACT'
  result[label]=pair
 for version in ('3.0.1','3.0.4'):
  assert int(re.search(r'total fragments in treatment:\s*(\d+)',(ROOT/version/'stderr.txt').read_text())[1])==2569317
 invalid=json.loads((ROOT/'attempt-64MiB/INVALID.json').read_text());assert invalid['valid_for_scientific_comparison'] is False
 print(json.dumps({'state':'PASS','rows_per_file':30438,'comparisons':result,'invalid_attempt_excluded':True,'scientific_tools_executed':False},sort_keys=True))
if __name__=='__main__':main()
