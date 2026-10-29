import copy,json,pathlib,unittest
from compare import compare_rows
class CompareTests(unittest.TestCase):
 def test_small_numeric_change_is_preserved(self):
  a=[['chr1','1','10','peak1','10','.','2.000000','3','4']];b=copy.deepcopy(a);b[0][6]='2.000001';d=compare_rows(a,b)
  self.assertFalse(d['all_fields_exact']);self.assertEqual(d['changed_cells_by_column'],{7:1});self.assertEqual(d['changes'][0]['right'][6],'2.000001')
 def test_equal_counts_do_not_hide_coordinates(self):
  a=[['chr1','1','10','x']];b=[['chr1','2','10','x']];d=compare_rows(a,b)
  self.assertFalse(d['coordinate_sets_exact']);self.assertEqual(len(d['left_only']),1);self.assertEqual(len(d['right_only']),1)
 def test_display_exclusion_keeps_other_fields(self):
  a=[['chr1','1','10','x','0','.','1','10','0','1','9','0','2','3','4']];b=copy.deepcopy(a);b[0][6:8]=['0','0'];d=compare_rows(a,b,(7,8))
  self.assertFalse(d['all_fields_exact']);self.assertTrue(d['all_nonexcluded_fields_exact'])
  b[0][14]='4.01';self.assertFalse(compare_rows(a,b,(7,8))['all_nonexcluded_fields_exact'])
 def test_actual_human_control_scope(self):
  d=json.loads((pathlib.Path(__file__).parent/'comparison.json').read_text());a=d['comparisons']['old_vs_new'];b=d['comparisons']['new_vs_archived_cloud']
  self.assertTrue(a['broadPeak']['all_fields_exact']);self.assertTrue(a['xls']['all_noncomment_rows_exact']);self.assertEqual(a['broadPeak']['left_rows'],30438)
  self.assertEqual(set(a['gappedPeak']['changed_cells_by_column']),{'7','8'});self.assertTrue(a['gappedPeak']['all_nonexcluded_fields_exact'])
  self.assertTrue(all(x['all_fields_exact'] for x in b.values()));self.assertTrue(d['same_scientific_argv'])
if __name__=='__main__':unittest.main()
