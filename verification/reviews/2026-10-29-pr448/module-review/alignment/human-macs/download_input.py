#!/usr/bin/env python3
import hashlib,json,os,pathlib,sys,time
ROOT=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,'LOCAL_TMP')
import archive as a
CASE='pr448-hiv-bwa-fixed-a9b588'
PATH='bwa/merged_library/HIV_CD86HI_48H_REP1.mLb.clN.sorted.bam'
def main():
 c=a.collector();rows,meta=a.inventories(c);row=next(x for x in rows if x['case']==CASE and x['relative_path']==PATH)
 assert row['bytes']<=800*1024**2 and row['source_workflow_id']=='BVYqNpYNcUhEN' and row['source_commit']=='a9b588235e4a1ceb3c8838acad430628c5737c86'
 source=a.CloudSource(c,meta);source.connect();reader=source.reader(row);out=ROOT/'input.bam';temp=ROOT/'input.bam.partial'
 assert not out.exists() and not temp.exists();fd=os.open(temp,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600);size=0;started=time.monotonic()
 with os.fdopen(fd,'wb') as f:
  while True:
   data=reader.read(a.BLOCK)
   if not data:break
   f.write(data);size+=len(data)
   if size>row['bytes']:raise RuntimeError('SIZE_CAP')
  f.flush();os.fsync(f.fileno())
 assert size==row['bytes'];digest=reader.digest();temp.rename(out)
 receipt={'case':CASE,'source_workflow_id':row['source_workflow_id'],'source_commit':row['source_commit'],'source_relative_path':PATH,'source_inventory_sha256':hashlib.sha256((a.CLOUD/'private/published-inventories'/f'{CASE}.json').read_bytes()).hexdigest(),'bytes':size,'source_etag':reader.etag,'sha256':digest,'all_ranges_content_range_content_length_etag_verified':True,'range_requests':reader.requests,'finished_source_live_identity_status_verified':'SUCCEEDED','signed_url_persisted':False,'elapsed_seconds':time.monotonic()-started}
 p=ROOT/'input-provenance.json';p.write_text(json.dumps(receipt,indent=2)+'\n');p.chmod(0o600);print(json.dumps({k:receipt[k] for k in ('case','source_workflow_id','bytes','sha256','range_requests','elapsed_seconds')}))
if __name__=='__main__':
 try:main()
 except Exception as e:print(json.dumps({'state':'FAILED','error_type':type(e).__name__}),file=sys.stderr);sys.exit(2)
