#!/usr/bin/env python3
"""Compare cached old/selected SAMtools on upstream regression fixtures."""
from pathlib import Path
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parent
IMAGES={'pre448':'quay.io/biocontainers/samtools:1.19.2--h50ea8bc_0','selected':'community.wave.seqera.io/library/htslib_samtools:1.24--d697cfb9dce007cd'}
def main():
 results={}
 for case,image in IMAGES.items():
  version=subprocess.check_output(['/usr/local/bin/docker','--context','colima','run','--rm','--network','none','--platform','linux/amd64',image,'samtools','--version'],stderr=subprocess.STDOUT).decode().splitlines()
  per={}
  for fixture in ('22_dup_supp.sam','23_isize_zero.sam'):
   cmd=['/usr/local/bin/docker','--context','colima','run','--rm','--network','none','--platform','linux/amd64','--memory','512m','-v',str(ROOT)+':/case:ro',image,'samtools','stats','/case/'+fixture]
   proc=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=60,check=True)
   (ROOT/(case+'-'+fixture+'.stats')).write_bytes(proc.stdout)
   (ROOT/(case+'-'+fixture+'.stderr')).write_bytes(proc.stderr)
   sn={}
   for line in proc.stdout.decode().splitlines():
    fields=line.split('\t')
    if fields[0]=='SN':sn[fields[1]]=fields[2]
   per[fixture]={'summary':sn,'fixture_sha256':hashlib.sha256((ROOT/fixture).read_bytes()).hexdigest(),'stats_sha256':hashlib.sha256(proc.stdout).hexdigest()}
  results[case]={'image':image,'runtime_version':version,'fixtures':per}
 differences={}
 for fixture in ('22_dup_supp.sam','23_isize_zero.sam'):
  old=results['pre448']['fixtures'][fixture]['summary'];new=results['selected']['fixtures'][fixture]['summary']
  differences[fixture]={key:{'old':old.get(key),'selected':new.get(key)} for key in old.keys()|new.keys() if old.get(key)!=new.get(key)}
 out={'results':results,'summary_differences':differences,'scope':'Real cached SAMtools binaries, upstream synthetic fixtures; no pipeline/cloud execution'}
 (ROOT/'result.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'summary_differences':differences,'duplicate_counts':{case:results[case]['fixtures']['22_dup_supp.sam']['summary'].get('reads duplicated:') for case in IMAGES},'result':str(ROOT/'result.json')}))
if __name__=='__main__':main()
