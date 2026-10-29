import argparse,copy,importlib.util,json,shutil,tempfile,unittest
from pathlib import Path
import reproduce as r
from types import SimpleNamespace
from unittest.mock import patch

class ReproductionTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.original=r.BUNDLE;self.bundle=self.root/'bundle';self.bundle.mkdir()
  for folder in ('sources','inputs','references','params'):
   shutil.copytree(r.BUNDLE/folder,self.bundle/folder,ignore=shutil.ignore_patterns('extracted'))
  r.BUNDLE=self.bundle
 def tearDown(self):r.BUNDLE=self.original;self.tmp.cleanup()
 def args(self):
  return argparse.Namespace(run_root=self.root/'run',output_root=None,work_root=None,references=None,samplesheet=None,nextflow='DO_NOT_EXECUTE_NEXTFLOW',profile='docker',executor='local',config=None,resume=False,execute=False,queue_size=1,max_cpus=12,max_memory='200.GB',max_time='48.h',case='all')
 def test_four_case_plan_keeps_science_and_separates_work(self):
  x=r.plan(self.args());self.assertEqual(set(x['cases']),set(r.CASES));works=set();outputs=set()
  for name,case in x['cases'].items():
   p=r.load(Path(case['cwd'])/'params.json');self.assertEqual(len(p),42);self.assertEqual(p['read_length'],50);self.assertEqual(p['macs_gsize'],2701262066);self.assertFalse(p['keep_dups']);self.assertEqual(p['custom_config_base'],'');self.assertEqual(case['scientific_parameter_count'],41)
   works.add(case['command'][case['command'].index('-work-dir')+1]);outputs.add(case['outdir'])
  self.assertEqual(len(works),4);self.assertEqual(len(outputs),4)
 def test_archive_and_extracted_source_tampering_are_rejected(self):
  sources=r.sources();p=sources['fixed']/'main.nf';p.write_text(p.read_text()+'\n//changed\n')
  with self.assertRaisesRegex(ValueError,'Extracted source changed'):r.sources()
 def test_cloud_paths_remain_arm_specific(self):
  a=self.args();a.output_root='s3://example/results';a.work_root='s3://example/work';a.executor='awsbatch';x=r.plan(a)
  self.assertTrue(all(c['outdir']=='s3://example/results/'+n for n,c in x['cases'].items()))
 def test_launch_and_download_need_explicit_execution(self):
  with self.assertRaisesRegex(ValueError,'--execute'):r.launch(self.args())
  with self.assertRaisesRegex(ValueError,'--execute'):r.fetch(self.args())
 def test_invalid_reference_override_is_not_silently_applied(self):
  a=self.args();a.references=self.root/'refs.json';a.references.write_text(json.dumps({'macs_gsize':1}))
  with self.assertRaisesRegex(ValueError,'Only fasta'):r.plan(a)
 def test_static_validation_covers_real_patch_and_pins(self):
  x=r.validate();self.assertEqual(x['patches_applicable'],2);self.assertEqual(x['public_fastqs'],8);self.assertFalse(x['science_launched'])
 def test_failed_attempt_requires_resume_and_preserves_all_evidence(self):
  a=self.args();r.plan(a);a.execute=True;a.case='bwa-unfixed';folder=a.run_root/'cases'/a.case
  old={'run.out':'failed stdout\n','execution.json':json.dumps({'case':a.case,'exit_code':1,'state':'EXITED'}),'trace.tsv':'status\nFAILED\n','report.html':'failed report','timeline.html':'failed timeline','nextflow.log':'failed log'}
  for name,text in old.items():(folder/name).write_text(text)
  (folder/'.nextflow').mkdir();(folder/'.nextflow/history').write_text('prior failed session\n')
  other=a.run_root/'cases/chromap-fixed/runtime.config';other_original=other.read_bytes()
  with patch.object(r.subprocess,'check_output',return_value='nextflow version 26.04.6') as version,patch.object(r.subprocess,'run') as execute:
   with self.assertRaisesRegex(ValueError,'--resume'):r.launch(a)
   version.assert_not_called();execute.assert_not_called()
   for name,text in old.items():self.assertEqual((folder/name).read_text(),text)
   def run(command,**kwargs):
    self.assertIn('-resume',command);kwargs['stdout'].write('new stdout\n');(folder/'trace.tsv').write_text('status\nCACHED\n');return SimpleNamespace(returncode=0)
   execute.side_effect=run;a.resume=True;a.max_cpus=6;self.assertEqual(r.launch(a),0)
   self.assertEqual(version.call_count,1);self.assertEqual(execute.call_count,1)
  archives=list((folder/'attempts').iterdir());self.assertEqual(len(archives),1);archive=archives[0]
  for name,text in old.items():self.assertEqual((archive/name).read_text(),text)
  self.assertEqual((archive/'nextflow-history.tsv').read_text(),'prior failed session\n');self.assertTrue((folder/'.nextflow/history').exists())
  self.assertEqual(r.load(folder/'execution.json')['exit_code'],0);self.assertEqual(r.load(folder/'execution.json')['prior_attempt'],str(archive.relative_to(folder)))
  self.assertEqual((folder/'run.out').read_text(),'new stdout\n');self.assertEqual(other.read_bytes(),other_original)
  self.assertIn('params.json',r.load(archive/'attempt.json')['files']);self.assertIn('runtime.config',r.load(archive/'attempt.json')['files'])

if __name__=='__main__':unittest.main()
