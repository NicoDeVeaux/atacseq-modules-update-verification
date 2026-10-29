#!/usr/bin/env python3
"""Run a public synthetic GFF→GTF check in the exact resolved fixed container."""
import argparse,hashlib,json,pathlib,re,subprocess,tempfile
IMAGE='quay.io/biocontainers/gffread:0.12.9--hf426362_0@sha256:c63259461255a7ec818697ccb6960fc120917b036281a7044aac0796d43fad4c'
TEXT='##gff-version 3\nchr1\tfixture\tmRNA\t101\t300\t0.125\t+\t.\tID=tx1;gene_id=gene1;Note=public_synthetic_control\nchr1\tfixture\texon\t101\t150\t.\t+\t.\tParent=tx1\nchr1\tfixture\texon\t201\t300\t.\t+\t.\tParent=tx1\n'
def oracle(text):
 rows=[]
 for line in text.splitlines():
  if not line or line.startswith('#'):continue
  cells=line.split('\t');assert len(cells)==9
  attrs=dict(re.findall(r'(\w+)\s+"([^"]*)"',cells[8]));assert attrs['transcript_id']=='tx1' and attrs['gene_id']=='gene1'
  rows.append((cells[0],cells[2],int(cells[3]),int(cells[4]),cells[6]))
 assert sorted(rows)==sorted([('chr1','transcript',101,300,'+'),('chr1','exon',101,150,'+'),('chr1','exon',201,300,'+')])
 return {'transcripts':1,'exons':2,'exonic_bases':150,'coordinate_and_identity_oracle_passed':True}
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--out',type=pathlib.Path,required=True);parser.add_argument('--context',default='colima');args=parser.parse_args();args.out.mkdir(parents=True,exist_ok=True)
 (args.out/'input.gff3').write_text(TEXT)
 common=['docker','--context',args.context,'run','--rm','--pull=never','--platform=linux/amd64','--network=none','--read-only','--cap-drop=ALL','--security-opt=no-new-privileges','--ulimit','core=0','-v',str(args.out.resolve())+':/work','-w','/work',IMAGE]
 v=subprocess.run(common+['gffread','--version'],capture_output=True,text=True,timeout=15);assert v.returncode==0 and (v.stdout+v.stderr).strip()=='0.12.9'
 p=subprocess.run(common+['gffread','input.gff3','--keep-exon-attrs','-F','-T','-o','output.gtf'],capture_output=True,text=True,timeout=15)
 assert p.returncode==0,p.stderr
 data=(args.out/'output.gtf').read_bytes();result={'image':IMAGE,'version':'0.12.9','argv':['gffread','input.gff3','--keep-exon-attrs','-F','-T','-o','output.gtf'],'exit_code':p.returncode,'input_sha256':hashlib.sha256(TEXT.encode()).hexdigest(),'output_sha256':hashlib.sha256(data).hexdigest(),**oracle(data.decode())}
 (args.out/'smoke.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
