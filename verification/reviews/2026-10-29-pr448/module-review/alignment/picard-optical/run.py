#!/usr/bin/env python3
"""Check the optical-coordinate boundary in actual old and selected Picard."""
from pathlib import Path
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parent
IMAGES={'pre448':'quay.io/biocontainers/picard:3.1.1--hdfd78af_0','selected':'community.wave.seqera.io/library/picard:3.4.0--e9963040df0a9bf6'}
SAMTOOLS='community.wave.seqera.io/library/htslib_samtools:1.24--d697cfb9dce007cd'
def docker(image,*args,mount=True):
 cmd=['/usr/local/bin/docker','--context','colima','run','--rm','--network','none','--platform','linux/amd64','--memory','1g']
 if mount:cmd+=['-v',str(ROOT)+':/case']
 return subprocess.run(cmd+[image,*args],stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=120,check=True)
def main():
 lines=['@HD\tVN:1.6\tSO:coordinate','@SQ\tSN:chr1\tLN:10000','@RG\tID:run\tSM:library\tLB:library\tPL:ILLUMINA\tPU:flow']
 for pos,flag,mpos,tlen in [(1000,99,1200,250),(1200,147,1000,-250)]:
  for x in [32760,32770]:
   lines.append('\t'.join(map(str,['INST:1:FLOW:1:1101:'+str(x)+':36800',flag,'chr1',pos,60,'50M','=',mpos,tlen,'A'*50,'I'*50,'RG:Z:run','NM:i:0'])))
 fixture=ROOT/'boundary.sam';fixture.write_text('\n'.join(lines)+'\n')
 results={}
 for case,image in IMAGES.items():
  folder=ROOT/case
  if folder.exists():raise ValueError('Refusing existing case')
  folder.mkdir();prefix='/case/'+case
  proc=docker(image,'picard','-Xmx512M','MarkDuplicates','--INPUT','/case/boundary.sam','--OUTPUT',prefix+'/marked.bam','--METRICS_FILE',prefix+'/metrics.txt','--ASSUME_SORTED','true','--REMOVE_DUPLICATES','false','--VALIDATION_STRINGENCY','LENIENT','--TMP_DIR',prefix+'/tmp')
  (folder/'stdout.txt').write_bytes(proc.stdout);(folder/'stderr.txt').write_bytes(proc.stderr)
  metrics=(folder/'metrics.txt').read_text().splitlines();header=next(i for i,line in enumerate(metrics) if line.startswith('LIBRARY\t'));values=dict(zip(metrics[header].split('\t'),metrics[header+1].split('\t')))
  viewed=docker(SAMTOOLS,'samtools','view',prefix+'/marked.bam').stdout.decode()
  (folder/'marked.sam').write_text(viewed)
  records=[line.split('\t') for line in viewed.splitlines()]
  results[case]={'image':image,'metrics':values,'duplicate_flags':[[r[0],int(r[1])] for r in records],'bam_sha256':hashlib.sha256((folder/'marked.bam').read_bytes()).hexdigest()}
 out={'results':results,'same_duplicate_flags':results['pre448']['duplicate_flags']==results['selected']['duplicate_flags'],'fixture_sha256':hashlib.sha256(fixture.read_bytes()).hexdigest(),'expected_optical_pairs':1,'scope':'Two duplicate pairs ten pixels apart straddling32767; actual default optical distance100; actual tool binaries'}
 (ROOT/'result.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'same_duplicate_flags':out['same_duplicate_flags'],'optical_pairs':{case:value['metrics']['READ_PAIR_OPTICAL_DUPLICATES'] for case,value in results.items()},'expected_optical_pairs':1,'result':str(ROOT/'result.json')}))
if __name__=='__main__':main()
