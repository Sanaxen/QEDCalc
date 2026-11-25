import unittest
from examples.three_loop_vp05_subsector_truncate_batch import targets,setting,SECTORS
from three_loop.master_basis_api import parse_integral
class TruncTests(unittest.TestCase):
    def test_targets(self):
        for s in SECTORS:
            t=targets(s)
            self.assertEqual(len(set(t)),10)
            for a in t:
                _,v=parse_integral(a)
                self.assertEqual(sum(1<<i for i,x in enumerate(v) if x>0),s)
                self.assertTrue(3<=sum(v)<=5)
                self.assertTrue(all(x>=0 for x in v))
    def test_yaml(self):
        raw="      select_integrals:\n        select_mandatory_list:\n"
        self.assertIn("truncate_sp:\n        - {topologies: [VP05_full], l: 2}",setting(raw,2))
        with self.assertRaises(ValueError):
            setting(raw,3)
