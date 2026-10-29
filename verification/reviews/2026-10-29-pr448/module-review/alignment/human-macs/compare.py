#!/usr/bin/env python3
import collections,csv,hashlib,json,pathlib,re
ROOT=pathlib.Path(__file__).resolve().parent
PREFIX='HIV_CD86HI_48H_REP1.mLb.clN_peaks'

def rows(path):
 return [line.rstrip('\r\n').split('\t') for line in path.read_text().splitlines() if line.strip() and not line.startswith(('#','track','browser'))]

def compare_rows(left,right,ignore=()):
 def keyed(data):
  result={}
  for row in data:
   key=tuple(row[:3])
   if key in result:raise ValueError('DUPLICATE_COORDINATE_KEY')
   result[key]=row
  return result
 a,b=keyed(left),keyed(right);shared=sorted(a.keys()&b.keys());changes=[];columns=collections.Counter();kept_changes=0
 for key in shared:
  if len(a[key])!=len(b[key]):raise ValueError('ROW_COLUMN_COUNT_MISMATCH')
  changed=[i+1 for i,(x,y) in enumerate(zip(a[key],b[key])) if x!=y]
  if changed:
   changes.append({'coordinate':list(key),'changed_columns':changed,'left':a[key],'right':b[key]});columns.update(changed)
   if any(i not in ignore for i in changed):kept_changes+=1
 return {'left_rows':len(left),'right_rows':len(right),'ordered_rows_exact':left==right,'coordinate_sets_exact':a.keys()==b.keys(),'left_only':[a[x] for x in sorted(a.keys()-b.keys())],'right_only':[b[x] for x in sorted(b.keys()-a.keys())],'shared_coordinate_rows':len(shared),'changed_shared_rows':len(changes),'changed_cells_by_column':dict(sorted(columns.items())),'changed_shared_rows_excluding_selected_columns':kept_changes,'excluded_columns':list(ignore),'all_fields_exact':not changes and a.keys()==b.keys(),'all_nonexcluded_fields_exact':not kept_changes and a.keys()==b.keys(),'changes':changes}

def main():
 execution=json.loads((ROOT/'execution.json').read_text())
 assert set(execution)=={'3.0.1','3.0.4'} and all(v['exit_code']==0 and not v['timed_out'] and v['stderr_io_exception_absent'] for v in execution.values())
 results={};diffroot=ROOT/'differences';diffroot.mkdir(exist_ok=True)
 for label,left,right in [('old_vs_new',ROOT/'3.0.1',ROOT/'3.0.4'),('new_vs_archived_cloud',ROOT/'3.0.4',ROOT/'archived-published')]:
  pair={}
  for ext,width,ignore in [('broadPeak',9,()),('gappedPeak',15,(7,8))]:
   a=rows(left/(PREFIX+'.'+ext));b=rows(right/(PREFIX+'.'+ext));assert all(len(x)==width for x in a+b)
   value=compare_rows(a,b,ignore)
   details=diffroot/(label+'-'+ext+'.json');details.write_text(json.dumps({'left_only':value.pop('left_only'),'right_only':value.pop('right_only'),'changes':value.pop('changes')},indent=2)+'\n')
   detail=json.loads(details.read_text());value['left_only_rows']=len(detail['left_only']);value['right_only_rows']=len(detail['right_only']);value['complete_differences_file']=str(details.relative_to(ROOT));pair[ext]=value
  a=rows(left/(PREFIX+'.xls'));b=rows(right/(PREFIX+'.xls'));assert a[0]==b[0]
  value=compare_rows(a[1:],b[1:]);detail=diffroot/(label+'-xls.json');detail.write_text(json.dumps({'left_only':value.pop('left_only'),'right_only':value.pop('right_only'),'changes':value.pop('changes')},indent=2)+'\n');d=json.loads(detail.read_text());value.update(header=a[0],left_only_rows=len(d['left_only']),right_only_rows=len(d['right_only']),complete_differences_file=str(detail.relative_to(ROOT)),all_noncomment_rows_exact=a==b);pair['xls']=value
  results[label]=pair
 input_prov=json.loads((ROOT/'input-provenance.json').read_text());fragments={}
 for version in execution:
  text=(ROOT/version/'stderr.txt').read_text();m=re.search(r'total fragments in treatment:\s*(\d+)',text);assert m;fragments[version]=int(m[1])
 archive=(ROOT/'archived-published'/'HIV_CD86HI_48H_REP1.mLb.clN.sorted.bam.flagstat').read_text();total=int(archive.split()[0]);properly_paired=int(re.search(r'^(\d+) \+ \d+ properly paired',archive,re.M)[1]);assert properly_paired==2*fragments['3.0.1']==2*fragments['3.0.4']
 summary={'schema':'nf-verify/pr448-human-macs-same-input/v1','source':input_prov,'archived_source':json.loads((ROOT/'archived-source-provenance.json').read_text()),'emitted_input_fragments':fragments,'archived_clean_bam_flagstat_total_records':total,'archived_clean_bam_flagstat_properly_paired_records':properly_paired,'same_scientific_argv':execution['3.0.1']['argv']==execution['3.0.4']['argv'],'comparisons':results,'invalid_first_attempt_excluded':'attempt-64MiB/INVALID.json','scope_limits':['One full cleaned paired-end human library, default broad mode, no control.','Equality refers to emitted fields; internal floating-point values below output precision were not inspected.','No narrow, single-end, control, parameter sweep, biological equivalence or full-pipeline rerun claim.','Inputs are fixed-BWAa9b588 results, not a pre448 pipeline execution.']}
 (ROOT/'comparison.json').write_text(json.dumps(summary,indent=2)+'\n')
 print(json.dumps({'fragments':fragments,'flagstat_total':total,'comparisons':results},indent=2))
if __name__=='__main__':main()
