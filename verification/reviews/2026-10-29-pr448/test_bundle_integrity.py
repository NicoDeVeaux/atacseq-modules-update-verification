import hashlib,importlib.util,json,tempfile,unittest
from pathlib import Path
source=Path(__file__).resolve().parent/'verify.py'
if not source.exists():source=Path(__file__).resolve().parent/'pr448-public-verify.py'
spec=importlib.util.spec_from_file_location('bundle_verifier',source);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
class IntegrityTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name);self.file=self.root/'data.txt';self.file.write_bytes(b'known');self.manifest={'files':{'data.txt':{'bytes':5,'sha256':hashlib.sha256(b'known').hexdigest()}}};self.save()
 def save(self):(self.root/'PUBLIC-MANIFEST.json').write_text(json.dumps(self.manifest))
 def test_complete_bundle(self):self.assertEqual(mod.verify(self.root)['public_files_verified'],1)
 def test_same_size_corruption(self):
  self.file.write_bytes(b'other')
  with self.assertRaisesRegex(ValueError,'Artifact mismatch'):mod.verify(self.root)
 def test_missing_file(self):
  self.file.unlink()
  with self.assertRaisesRegex(ValueError,'inventory'):mod.verify(self.root)
 def test_unlisted_file(self):
  (self.root/'extra.txt').write_text('unexpected')
  with self.assertRaisesRegex(ValueError,'inventory'):mod.verify(self.root)
 def test_directory_symlink(self):
  (self.root/'alias').symlink_to(self.root,target_is_directory=True)
  with self.assertRaisesRegex(ValueError,'Symlink'):mod.verify(self.root)
 def test_symlink_file(self):
  (self.root/'alias').symlink_to(self.file)
  with self.assertRaisesRegex(ValueError,'Nonregular'):mod.verify(self.root)
 def test_false_zero_file_success(self):
  self.manifest['files']={};self.save()
  with self.assertRaisesRegex(ValueError,'Missing artifact'):mod.verify(self.root)
 def test_invalid_hash_metadata(self):
  self.manifest['files']['data.txt']['sha256']='not-a-hash';self.save()
  with self.assertRaisesRegex(ValueError,'metadata'):mod.verify(self.root)
if __name__=='__main__':unittest.main()
