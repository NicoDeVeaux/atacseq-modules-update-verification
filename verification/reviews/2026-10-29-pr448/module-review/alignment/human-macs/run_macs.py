#!/usr/bin/env python3
import hashlib,json,pathlib,re,shlex,subprocess,time,uuid
ROOT=pathlib.Path(__file__).resolve().parent
IMAGES={'3.0.1':'quay.io/biocontainers/macs3:3.0.1--py311h0152c62_3','3.0.4':'community.wave.seqera.io/library/macs3:3.0.4--e0346d811b8b428e'}
BAM='HIV_CD86HI_48H_REP1.mLb.clN.sorted.bam'
def main():
 provenance=json.loads((ROOT/'input-provenance.json').read_text());assert provenance['finished_source_live_identity_status_verified']=='SUCCEEDED'
 assert hashlib.sha256((ROOT/'input.bam').read_bytes()).hexdigest()==provenance['sha256']
 raw=(ROOT/'archived.command.sh').read_text();body=raw.split('# capture process environment',1)[0];lines=body.splitlines();body='\n'.join(x for x in lines if not x.startswith('#!')).replace('\\\n',' ');args=shlex.split(body)
 expected=['macs3','callpeak','--keep-dup','all','--nomodel','--broad','--broad-cutoff','0.1','--gsize','2701262066','--format','BAMPE','--name','HIV_CD86HI_48H_REP1.mLb.clN','--treatment',BAM]
 assert args==expected,(args,expected)
 results={}
 for version,image in IMAGES.items():
  out=ROOT/version;out.mkdir(exist_ok=False);name='pr448-human-macs-'+version.replace('.','')+'-'+uuid.uuid4().hex[:8]
  common=['docker','--context','colima','run','--rm','--name',name,'--pull=never','--platform=linux/amd64','--network=none','--cpus=2','--memory=4g','--memory-swap=4g','--read-only','--cap-drop=ALL','--security-opt=no-new-privileges','--ulimit','core=0','--tmpfs','/tmp:rw,size=512m','-v',str(out)+':/work','-v',str(ROOT/'input.bam')+':/work/'+BAM+':ro','-w','/work',image]
  v=subprocess.run(common[:-1]+[image,'macs3','--version'],capture_output=True,timeout=30)
  assert v.returncode==0 and version in v.stdout.decode(),v.stderr
  # The version check container is removed before reuse of the name.
  started=time.monotonic();p=subprocess.Popen(common+args,stdout=(out/'stdout.txt').open('wb'),stderr=(out/'stderr.txt').open('wb'))
  try:code=p.wait(timeout=300)
  except subprocess.TimeoutExpired:
   subprocess.run(['docker','--context','colima','kill',name],capture_output=True,timeout=15);code=p.wait(timeout=15)
   results[version]={'exit_code':code,'timed_out':True};(ROOT/'execution.json').write_text(json.dumps(results,indent=2)+'\n');raise RuntimeError('FIVE_MINUTE_CASE_CAP')
  identity=json.loads(subprocess.check_output(['docker','--context','colima','image','inspect',image]))[0]
  results[version]={'image':image,'identity':{k:identity.get(k) for k in ('Id','RepoDigests','Architecture','Os','Size')},'version_stdout':v.stdout.decode().strip(),'argv':args,'exit_code':code,'elapsed_seconds':time.monotonic()-started,'timed_out':False,'memory_limit_bytes':4*1024**3,'cpu_limit':2,'network_disabled':True,'tmpfs_limit_bytes':512*1024**2,'stderr_io_exception_absent':not bool(re.search(r'Traceback \(most recent call last\)|OSError:|No space left on device|Exception ignored',(out/'stderr.txt').read_text()))}
  (ROOT/'execution.json').write_text(json.dumps(results,indent=2)+'\n')
  if code!=0 or not results[version]['stderr_io_exception_absent']:raise RuntimeError('MACS_FAILED_OR_IO_DIAGNOSTIC_'+version)
  print(json.dumps({'version':version,'exit_code':code,'elapsed_seconds':results[version]['elapsed_seconds']}),flush=True)
if __name__=='__main__':main()
