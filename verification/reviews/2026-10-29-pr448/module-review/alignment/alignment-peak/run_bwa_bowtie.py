"""Bounded paired-read mapper controls; no Nextflow or cloud execution."""
from pathlib import Path
import concurrent.futures
import gzip
import hashlib
import json
import subprocess

ROOT=Path(__file__).resolve().parent/'bwa-bowtie-same-reads'
SOURCE=Path('REVIEW_ROOT/real-samples')
IMAGES={
 'bwa_0.7.17':'quay.io/biocontainers/mulled-v2-fe8faa35dbf6dc65a0f7f5d4ea12e31a79f73e40:a34558545ae1413d94bde4578787ebef08027945-0',
 'bwa_0.7.19':'community.wave.seqera.io/library/bwa_htslib_samtools:83b50ff84ead50d0',
 'bowtie_2.5.2':'quay.io/biocontainers/mulled-v2-ac74a7f02cebcfcc07d8e8d1d750af9c83b4d45a:f70b31a2db15c023d641c32f433fb02cd04df5a6-0',
 'bowtie_2.5.4':'community.wave.seqera.io/library/bowtie2_htslib_samtools_pigz:edeb13799090a2a6',
 'bowtie_build_2.4.4':'quay.io/biocontainers/bowtie2:2.4.4--py39hbb4e92a_0',
}


def run(name,image,arguments,index=None,sam=False):
 folder=ROOT/name;folder.mkdir(parents=True,exist_ok=True)
 cmd=['docker','--context','colima','run','--rm','--network','none','--platform','linux/amd64','--cpus','2','--memory','4g',
      '-v',str(SOURCE/'reference')+':/reference:ro','-v',str(ROOT/'reads')+':/reads:ro','-v',str(folder)+':/output','-w','/output']
 if index:cmd+=['-v',str(ROOT/index)+':/index:ro']
 cmd += [IMAGES[image],*arguments]
 with (folder/('alignments.sam' if sam else 'stdout.txt')).open('w') as output:
  result=subprocess.run(cmd,text=True,stdout=output,stderr=subprocess.PIPE)
 (folder/'stderr.txt').write_text(result.stderr)
 record={'case':name,'image':IMAGES[image],'command':cmd,'exit_code':result.returncode}
 (folder/'command.json').write_text(json.dumps(record,indent=2)+'\n')
 if result.returncode:raise RuntimeError(name+' failed')
 return record


def main():
 ROOT.mkdir(parents=True,exist_ok=True);reads=ROOT/'reads';reads.mkdir(exist_ok=True)
 work=next((SOURCE/'full-core/cases/fixed/work/f4').glob('76dec3*'))
 names=[];records=[]
 for mate in (1,2):
  src=work/f'D28P_REP1_T2_{mate}_val_{mate}.fq.gz';target=reads/f'R{mate}.fq.gz';ids=[]
  with gzip.open(src,'rb') as incoming,target.open('wb') as raw:
   with gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0) as output:
    for _ in range(5000):
     record=[incoming.readline() for i in range(4)]
     assert all(record)
     ids.append(record[0].split()[0]);output.writelines(record)
  names.append(ids);records.append({'mate':mate,'pairs':5000,'selected_from':'fixed actual TrimGalore output, first5000paired records','sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'bytes':target.stat().st_size})
 assert names[0]==names[1] and len(set(names[0]))==5000
 (ROOT/'input-provenance.json').write_text(json.dumps(records,indent=2)+'\n')
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
  indices=list(pool.map(lambda v:run(*v),[
   ('bwa_index_0.7.19','bwa_0.7.19',['bwa','index','-p','/output/genome','/reference/sacCer3.fa']),
   ('bowtie_index_2.4.4','bowtie_build_2.4.4',['bowtie2-build','--threads','2','/reference/sacCer3.fa','/output/genome']),
   ('bowtie_index_2.5.4','bowtie_2.5.4',['bowtie2-build','--threads','2','/reference/sacCer3.fa','/output/genome'])]))
 rg='@RG\\tID:D28P_REP1_T2\\tSM:D28P_REP1\\tPL:ILLUMINA\\tLB:D28P_REP1'
 cases=[]
 for version in ['0.7.17','0.7.19']:
  cases.append((f'bwa_{version}',f'bwa_{version}',['bwa','mem','-M','-R',rg,'-t','2','/index/genome','/reads/R1.fq.gz','/reads/R2.fq.gz'],'bwa_index_0.7.19',True))
 for version in ['2.5.2','2.5.4']:
  for index in ['2.4.4','2.5.4']:
   arguments=['bowtie2','-x','/index/genome','-1','/reads/R1.fq.gz','-2','/reads/R2.fq.gz','--threads','2',
              '--rg-id','D28P_REP1_T2','--rg','SM:D28P_REP1','--rg','PL:ILLUMINA','--rg','LB:D28P_REP1_T2','--rg','PU:1']
   cases.append((f'bowtie_{version}_index_{index}',f'bowtie_{version}',arguments,'bowtie_index_'+index,True))
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:aligned=list(pool.map(lambda args:run(*args),cases))
 (ROOT/'run-results.json').write_text(json.dumps({'index':indices,'align':aligned},indent=2)+'\n')
 metadata={}
 for name,image in IMAGES.items():
  metadata[name]=json.loads(subprocess.check_output(['docker','--context','colima','image','inspect',image],text=True))[0]
 (ROOT/'images.json').write_text(json.dumps({k:{f:v.get(f) for f in ['Id','RepoDigests','Architecture','Size']} for k,v in metadata.items()},indent=2)+'\n')
 print(json.dumps({'index_cases':len(indices),'alignment_cases':len(aligned),'real_pairs':5000,'all_exit_zero':True}))


if __name__=='__main__':main()
