#!/usr/bin/env python3
"""Plan or explicitly run new four-arm comparisons without Platform APIs."""
import argparse,csv,hashlib,json,os,re,shutil,subprocess,sys,tarfile
from datetime import datetime,timezone
from pathlib import Path
from urllib.request import urlopen
BUNDLE=Path(__file__).resolve().parent
CASES=('bwa-unfixed','bwa-fixed','chromap-unfixed','chromap-fixed')
def load(p):return json.loads(p.read_text())
def dump(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2)+'\n')
def digest(p,algorithm='sha256'):
 h=hashlib.new(algorithm)
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def sources():
 result={}
 for arm,record in load(BUNDLE/'sources/manifest.json')['sources'].items():
  archive=BUNDLE/record['archive']
  if digest(archive)!=record['sha256']:raise ValueError('Source archive hash mismatch')
  dest=BUNDLE/'sources/extracted'/arm
  if not dest.exists():
   dest.mkdir(parents=True)
   with tarfile.open(archive) as tar:
    for m in tar.getmembers():
     if m.issym() or m.islnk() or not (dest/m.name).resolve().is_relative_to(dest.resolve()):raise ValueError('Unsafe archive entry')
    tar.extractall(dest)
  with tarfile.open(archive) as tar:
   expected=set()
   for m in tar.getmembers():
    if m.isfile():
     expected.add(m.name);path=dest/m.name
     if path.is_symlink() or not path.is_file() or hashlib.sha256(tar.extractfile(m).read()).hexdigest()!=digest(path):raise ValueError('Extracted source changed: '+m.name)
   if {str(p.relative_to(dest)) for p in dest.rglob('*') if p.is_file()}!=expected:raise ValueError('Unexpected files in immutable source extraction')
  result[arm]=dest
 return result
def join(root,name):return root.rstrip('/')+'/'+name
def runtime(args):
 return f"params.custom_config_base = ''\nprocess.executor = '{args.executor}'\nexecutor.queueSize = {args.queue_size}\nprocess.resourceLimits = [cpus: {args.max_cpus}, memory: '{args.max_memory}', time: '{args.max_time}']\n"
def plan(args,selected=None):
 src=sources();root=args.run_root.resolve();pins=load(BUNDLE/'sources/manifest.json')['sources'];cases=load(root/'campaign.json')['cases'].copy() if (root/'campaign.json').exists() else {}
 overrides=load(args.references) if args.references else {}
 if set(overrides)-{'fasta','gtf','bwa_index'}:raise ValueError('Only fasta/gtf/bwa_index overrides supported')
 for name in selected or CASES:
  aligner,arm=name.split('-');folder=root/'cases'/name;params=load(BUNDLE/'params'/f'{name}.json')
  if prior_artifacts(folder):raise ValueError('Plan refuses to overwrite an existing attempt; explicit launch --resume archives it first')
  if len(params)!=41:raise ValueError('Expected 41 scientific parameters')
  params.update(input=str(args.samplesheet.resolve()) if args.samplesheet else str(BUNDLE/'inputs/hiv.csv'),outdir=join(args.output_root,name) if args.output_root else str(folder/'results'),blacklist=str(BUNDLE/'references/hg38-blacklist.v3.bed'),**overrides)
  params['custom_config_base']='';pp=folder/'params.json';cfg=folder/'runtime.config';dump(pp,params);cfg.write_text(runtime(args))
  cmd=[args.nextflow,'-log',str(folder/'nextflow.log'),'run',str(src[arm]/'main.nf'),'-profile',args.profile,'-params-file',str(pp),'-work-dir',join(args.work_root,name) if args.work_root else str(folder/'work'),'-c',str(cfg),'-with-trace',str(folder/'trace.tsv'),'-with-report',str(folder/'report.html')]
  if args.config:cmd+=['-c',str(args.config.resolve())]
  if args.resume:cmd+=['-resume']
  cases[name]={'aligner':aligner,'arm':arm,'source_commit':pins[arm]['commit'],'cwd':str(folder),'outdir':params['outdir'],'command':cmd,'params_sha256':digest(pp),'runtime_config_sha256':digest(cfg),'user_config_sha256':digest(args.config.resolve()) if args.config else None,'scientific_parameter_count':41,'runtime_only_extra_parameter':'custom_config_base','reference_overrides':overrides}
 record={'schema':'pr448/new-execution-plan/v1','prepared_at':datetime.now(timezone.utc).isoformat(),'nextflow_version':'26.04.6','scope':'New user-configured execution, distinct from historical AWS Batch/Fusion','cases':cases,'expected_libraries':['HIV_CD86HI_48H_REP1','HIV_CD86HI_48H_REP2','MOCK_48H_REP1','MOCK_48H_REP2']}
 dump(root/'campaign.json',record);return record
def prior_artifacts(folder):
 patterns=('execution.json','run*.out','nextflow.log*','.nextflow.log*','trace*.tsv','report*.html','timeline*.html')
 return sorted({path for pattern in patterns for path in folder.glob(pattern) if path.is_file()})
def archive_attempt(folder):
 prior=prior_artifacts(folder)
 if not prior:
  saved=sorted((folder/'attempts').glob('*/attempt.json'))
  return str(saved[-1].parent.relative_to(folder)) if saved else None
 stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');archive=folder/'attempts'/stamp;archive.mkdir(parents=True)
 files={}
 for path in sorted(set(prior)|{p for p in (folder/'params.json',folder/'runtime.config') if p.is_file()}):
  files[path.name]={'sha256':digest(path),'bytes':path.stat().st_size,'preservation':'moved'}
  shutil.move(str(path),str(archive/path.name))
 history=folder/'.nextflow/history'
 if history.is_file():
  shutil.copy2(history,archive/'nextflow-history.tsv');files['nextflow-history.tsv']={'sha256':digest(history),'bytes':history.stat().st_size,'preservation':'copied; live session history retained for resume'}
 dump(archive/'attempt.json',{'archived_at':datetime.now(timezone.utc).isoformat(),'reason':'Explicit same-arm resume','files':files})
 return str(archive.relative_to(folder))
def launch(args):
 if not args.execute:raise ValueError('No work launched: inspect plan, then add --execute explicitly')
 selected=CASES if args.case=='all' else [args.case]
 for name in selected:
  folder=args.run_root.resolve()/'cases'/name
  if (prior_artifacts(folder) or (folder/'attempts').exists() or (folder/'.nextflow/history').exists()) and not args.resume:raise ValueError('Prior execution exists; inspect before explicit --resume')
 sources();env={**os.environ,'NXF_VER':'26.04.6','NXF_DISABLE_CHECK_LATEST':'true'}
 version=subprocess.check_output([args.nextflow,'-version'],env=env,text=True)
 if not re.search(r'\b26\.04\.6\b',version):raise ValueError('Nextflow 26.04.6 required')
 archives={name:archive_attempt(args.run_root.resolve()/'cases'/name) for name in selected} if args.resume else {}
 record=plan(args,selected)
 code=0
 for name in selected:
  case=record['cases'][name];folder=Path(case['cwd']);receipt=folder/'execution.json'
  value={'case':name,'source_commit':case['source_commit'],'started_at':datetime.now(timezone.utc).isoformat(),'state':'RUNNING','prior_attempt':archives.get(name)};dump(receipt,value)
  with (folder/'run.out').open('w') as output:r=subprocess.run(case['command'],cwd=folder,env=env,stdout=output,stderr=subprocess.STDOUT)
  value.update(finished_at=datetime.now(timezone.utc).isoformat(),exit_code=r.returncode,state='EXITED');dump(receipt,value);code=max(code,0 if r.returncode==0 else 1)
 return code
def fetch(args):
 if not args.execute:raise ValueError('Downloads require --execute (about 7.2 GB compressed)')
 dest=args.input_dir.resolve();dest.mkdir(parents=True,exist_ok=True);mapping={}
 for file in load(BUNDLE/'inputs/ena.json')['files']:
  path=dest/Path(file['url']).name
  if not path.exists():
   temp=path.with_suffix(path.suffix+'.partial')
   with urlopen(file['url']) as response,temp.open('wb') as output:
    for block in iter(lambda:response.read(1048576),b''):output.write(block)
   temp.replace(path)
  if path.stat().st_size!=file['bytes'] or digest(path,'md5')!=file['md5']:raise ValueError('Input size/MD5 mismatch: '+path.name)
  mapping[file['url']]=str(path)
 with (BUNDLE/'inputs/hiv.csv').open() as f:rows=list(csv.DictReader(f))
 with (dest/'hiv.local.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader()
  for row in rows:row.update(fastq_1=mapping[row['fastq_1']],fastq_2=mapping[row['fastq_2']]);w.writerow(row)
 return 0
def validate():
 src=sources();ena=load(BUNDLE/'inputs/ena.json');files=ena['files']
 if len(files)!=8 or len({f['url'] for f in files})!=8 or any(not re.fullmatch(r'[0-9a-f]{32}',f['md5']) or f['bytes']<=0 for f in files):raise ValueError('Invalid public input metadata')
 if sum(f['pairs_per_library'] for f in files if f['mate']==1)!=87089251:raise ValueError('Wrong cohort size')
 for record in load(BUNDLE/'params/transformations.json')['transformations']:
  p=BUNDLE/'params'/(record['case']+'.json')
  if len(load(p))!=41 or digest(p)!=record['normalized_parameter_sha256']:raise ValueError('Normalized parameter hash mismatch')
 refs=load(BUNDLE/'references/manifest.json')
 if digest(BUNDLE/refs['blacklist']['file'])!=refs['blacklist']['sha256']:raise ValueError('Blacklisted reference bytes changed')
 env={k:v for k,v in os.environ.items() if k not in ('GIT_DIR','GIT_WORK_TREE')}
 for patch in ('full-proposal.patch','scientific-fix.patch'):subprocess.run(['git','apply','--check',str(BUNDLE/'sources'/patch)],cwd=src['unfixed'],env=env,check=True,capture_output=True)
 return {'source_archives':2,'patches_applicable':2,'scientific_parameter_cases':4,'public_fastqs':8,'total_pairs':87089251,'blacklist_sha256':refs['blacklist']['sha256'],'science_launched':False}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=('validate','plan','launch','fetch-inputs'))
 p.add_argument('--run-root',type=Path,default=Path('hiv-reproduction'));p.add_argument('--output-root');p.add_argument('--work-root')
 p.add_argument('--case',choices=('all',*CASES),default='all');p.add_argument('--execute',action='store_true');p.add_argument('--resume',action='store_true')
 p.add_argument('--nextflow',default='nextflow');p.add_argument('--profile',choices=('docker','singularity','apptainer'),default='docker')
 p.add_argument('--executor',choices=('local','awsbatch','slurm'),default='local');p.add_argument('--config',type=Path)
 p.add_argument('--references',type=Path);p.add_argument('--samplesheet',type=Path);p.add_argument('--input-dir',type=Path,default=Path('hiv-inputs'))
 p.add_argument('--queue-size',type=int,default=1);p.add_argument('--max-cpus',type=int,default=12);p.add_argument('--max-memory',default='200.GB');p.add_argument('--max-time',default='48.h')
 a=p.parse_args()
 try:
  if a.queue_size<1 or a.max_cpus<1 or not re.fullmatch(r'\d+(?:\.\d+)?\.(?:GB|MB)',a.max_memory) or not re.fullmatch(r'\d+(?:\.\d+)?\.(?:h|d|m)',a.max_time):raise ValueError('Invalid resource limits')
  if a.executor!='local' and not a.config:raise ValueError('Non-local executor requires your own --config with queue/storage/credentials settings')
  if a.action=='validate':print(json.dumps(validate(),indent=2));return 0
  if a.action=='plan':print(json.dumps(plan(a),indent=2));return 0
  return launch(a) if a.action=='launch' else fetch(a)
 except (OSError,ValueError,subprocess.CalledProcessError) as error:print(str(error),file=sys.stderr);return 2
if __name__=='__main__':sys.exit(main())
