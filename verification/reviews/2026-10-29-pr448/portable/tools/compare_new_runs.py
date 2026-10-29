#!/usr/bin/env python3
"""Compare new local/mirrored outputs; never invent historical Platform identities."""
import argparse,csv,importlib.util,json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent/'observed'))
import compare_campaign_outputs as helper
from generate_report import raw_fastqc
BUNDLE=Path(__file__).resolve().parents[1]
def load(p,default=None):return json.loads(p.read_text()) if p.exists() else default
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run-root',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--collected-root',type=Path);a=p.parse_args()
 plan=load(a.run_root/'campaign.json',{});ref=helper.reference();expected=plan.get('expected_libraries',[]);pins=load(BUNDLE/'sources/manifest.json')['sources']
 ena=load(BUNDLE/'inputs/ena.json');pairs={f['library']:f['pairs_per_library'] for f in ena['files']};cases={}
 for name,case in plan.get('cases',{}).items():
  issues=[];receipt=load(Path(case['cwd'])/'execution.json',{});files={}
  if case['source_commit']!=pins[case['arm']]['commit']:issues.append('Plan source differs from bundled immutable source')
  if receipt.get('case')!=name or receipt.get('source_commit')!=case['source_commit'] or receipt.get('state')!='EXITED' or receipt.get('exit_code')!=0:issues.append('Exact-source execution has not exited successfully')
  trace=Path(case['cwd'])/'trace.tsv';tasks=[]
  if trace.exists():
   with trace.open() as f:tasks=list(csv.DictReader(f,delimiter='\t'))
  if not tasks or any(t.get('status') not in ('COMPLETED','CACHED') for t in tasks) or not any('MULTIQC' in t.get('name','') for t in tasks):issues.append('Actual full execution trace incomplete')
  if a.collected_root:directory=a.collected_root/name/'results'
  elif '://' in case['outdir']:directory=None;issues.append('Remote results require --collected-root mirror')
  else:directory=Path(case['outdir'])
  if directory:
   for path in directory.rglob('*'):
    if path.is_file() and helper.category(path):
     key=helper.canonical(path.relative_to(directory))
     if key in files:issues.append('Ambiguous artifact '+key)
     else:files[key]=path
   mq=list(directory.glob('multiqc/**/multiqc_data.json'))
   try:
    if len(mq)!=1:raise ValueError('Missing/ambiguous MultiQC')
    raw=load(mq[0]);actual={lib:raw_fastqc(raw,lib,pairs[lib]) for lib in expected}
   except (ValueError,KeyError) as error:issues.append(str(error));actual={}
  else:actual={}
  present={helper.category(path) for path in files.values() if 'merged_library' in path.parts or helper.category(path)=='versions'}
  for kind in helper.REQUIRED-present:issues.append('Missing required category '+kind)
  for kind in helper.LIBRARY_KINDS:
   covered={path.name.split('.mLb.')[0] for path in files.values() if helper.category(path)==kind and 'merged_library' in path.parts}
   if set(expected)-covered:issues.append('Missing '+kind+' libraries: '+','.join(sorted(set(expected)-covered)))
  cases[name]={'source_commit':case['source_commit'],'aligner':case['aligner'],'arm':case['arm'],'issues':issues,'files':files,'raw_reads_per_mate':actual}
 comparisons={}
 for aligner in ('bwa','chromap'):
  arms={c['arm']:c for c in cases.values() if c['aligner']==aligner};left,right=arms.get('unfixed',{}),arms.get('fixed',{});items=[];gaps=[issue for c in arms.values() for issue in c['issues']]
  for key in sorted(left.get('files',{}).keys()|right.get('files',{}).keys()):
   kind=helper.category(Path(key));item={'path':key,'kind':kind}
   try:
    x,y=left['files'][key],right['files'][key]
    if kind=='counts':
     item['comparison']=helper.compare_counts(x,y,ref)
     if '.mLb.' in key and set(item['comparison']['shared_samples'])!=set(expected):raise ValueError('Count library identities differ from the planned four libraries')
    elif kind=='bed':item['comparison']=helper.compare_bed(x,y)
    else:
     u,v=helper.parsed(x,kind),helper.parsed(y,kind);item.update(unfixed=u,fixed=v,differences=helper.differences(u,v))
   except (ValueError,KeyError,OSError,IndexError) as error:item['error']=str(error);gaps.append(key+': '+str(error))
   items.append(item)
  if set(arms)!={'unfixed','fixed'} or not items:gaps.append('Missing paired outputs')
  comparisons[aligner]={'coverage_complete':not gaps,'gaps':gaps,'artifacts':items}
 complete=len(cases)==4 and all(v['coverage_complete'] for v in comparisons.values())
 result=helper.clean_json({'scope':'New execution only; completeness is not scientific PASS','complete':complete,'cases':{k:{i:v for i,v in c.items() if i!='files'} for k,c in cases.items()},'pairs':comparisons})
 a.out.mkdir(parents=True,exist_ok=True);(a.out/'comparison.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');print(json.dumps({'complete':complete,'output':str(a.out)}));return 0
if __name__=='__main__':sys.exit(main())
