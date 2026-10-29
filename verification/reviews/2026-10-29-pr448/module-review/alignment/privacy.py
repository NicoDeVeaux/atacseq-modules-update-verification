"""Static privacy checks, including bounded compressed members; never execute artifacts."""
import gzip,io,ipaddress,re,tarfile,zipfile
MAX_DECODED=50*1024**2
SECRET=[('aws_key',re.compile(rb'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b')),('jwt',re.compile(rb'\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b')),('github_token',re.compile(rb'\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b')),('bearer',re.compile(rb'(?i)\bBearer\s+(?!\[REDACTED)[A-Za-z0-9_./+=-]{12,}')),('signed_url',re.compile(rb'https?://[^\s"<>]*[?&](?:X-Amz-(?:Signature|Credential|Security-Token)|AWSAccessKeyId|Signature)=[^\s"<>]*',re.I))]
SECRET.append(('credential_assignment',re.compile(rb'(?im)\b(?:AWS_SECRET_ACCESS_KEY|AWS_SESSION_TOKEN|SEQERA_ACCESS_TOKEN|TOWER_ACCESS_TOKEN|OP_SERVICE_ACCOUNT_TOKEN|OPENAI_API_KEY|ANTHROPIC_API_KEY)["\']?\s*[:=]\s*["\']?(?!\[REDACTED)[^\s"\'<>;]{8,}')))
HOME=re.compile(rb'(?<![A-Za-z0-9])/(?:Use[r]s|home)/[A-Za-z0-9_.-]+(?=/|[\s"\'<>:]|$)')
TMP=re.compile(rb'/(?:private/)?(?:tmp|var/folders)/[A-Za-z0-9_.-]+')
ARN=re.compile(rb'arn:(?:aws|aws-cn|aws-us-gov):[^\s"\'<>]+')
# These public reference/test URIs are preserved in pinned nf-core source.
S3=re.compile(rb's3://(?!(?:REDACTED-BUCKET|ngi-igenomes|nf-core-awsmegatests)(?:/|$))[a-z0-9][a-z0-9._-]*/',re.I)
IP=re.compile(rb'(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])')
IP6=re.compile(rb'(?<![0-9a-f:])(?:f[cd][0-9a-f]{2}:[0-9a-f:]+|fe80:[0-9a-f:]+|::[1])(?![0-9a-f:])',re.I)
def private_ip(raw):
 try:
  a=ipaddress.IPv4Address(raw.decode());n=int(a);return a.is_loopback or a.is_link_local or n>>24==10 or n>>20==0xac1 or n>>16==0xc0a8 or n==0
 except ValueError:return False
def matches(data):
 result=[label for label,p in SECRET if p.search(data)]
 for label,p in [('local_home',HOME),('local_tmp',TMP),('aws_arn',ARN),('private_bucket_uri',S3)]:
  if p.search(data):result.append(label)
 if any(private_ip(m[0]) for m in IP.finditer(data)):result.append('private_ipv4')
 if IP6.search(data):result.append('private_ipv6')
 return sorted(set(result))
def path_ok(name):return isinstance(name,str) and name and not name.startswith('/') and '\\' not in name and ':' not in name and all(x not in ('','.','..') for x in name.rstrip('/').split('/'))
def audit(data,name,depth=0):
 if depth>4:raise ValueError('ARCHIVE_NESTING_LIMIT')
 found=matches(data)
 if found:raise ValueError('PRIVATE_PATTERN:'+','.join(found))
 reports=[]
 if data.startswith(b'\x1f\x8b'):
  with gzip.GzipFile(fileobj=io.BytesIO(data)) as stream:decoded=stream.read(MAX_DECODED+1)
  if len(decoded)>MAX_DECODED:raise ValueError('GZIP_DECODE_LIMIT')
  reports.append({'codec':'gzip/BGZF','decoded_bytes':len(decoded)});reports+=audit(decoded,name.removesuffix('.gz'),depth+1)
 elif data.startswith(b'PK\x03\x04'):
  with zipfile.ZipFile(io.BytesIO(data)) as z:
   total=0
   if len(z.infolist())>1000:raise ValueError('ZIP_MEMBER_LIMIT')
   for item in z.infolist():
    if not path_ok(item.filename) or item.flag_bits&1 or ((item.external_attr>>16)&0o170000)==0o120000:raise ValueError('ZIP_PATH_OR_LINK_REFUSED')
    total+=item.file_size
    if total>MAX_DECODED:raise ValueError('ZIP_EXPANDED_LIMIT')
    raw=z.read(item)
    if len(raw)!=item.file_size:raise ValueError('ZIP_SIZE_MISMATCH')
    if not item.is_dir():reports+=audit(raw,item.filename,depth+1)
   reports.append({'codec':'ZIP all members/CRC','members':len(z.infolist()),'expanded_bytes':total})
 elif len(data)>262 and data[257:262]==b'ustar':
  with tarfile.open(fileobj=io.BytesIO(data),mode='r:') as t:
   total=0;members=0
   for item in t:
    members+=1
    if members>1000 or not path_ok(item.name) or not (item.isfile() or item.isdir()):raise ValueError('TAR_PATH_OR_LINK_REFUSED')
    total+=item.size
    if total>MAX_DECODED:raise ValueError('TAR_EXPANDED_LIMIT')
    if item.isfile():reports+=audit(t.extractfile(item).read(),item.name,depth+1)
   reports.append({'codec':'TAR all regular members','members':members,'expanded_bytes':total})
 return reports
