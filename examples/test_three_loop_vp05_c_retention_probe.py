import unittest
from examples.three_loop_vp05_c_retention_probe import rank_probe

class CRetentionTests(unittest.TestCase):
    def test_independent_C_modulo_M(self):
        r=rank_probe([{(0,):1,(1,):2}],(1,),(2,),1000003)
        self.assertEqual(r["equation_rank"],1)
        self.assertTrue(r["C_rank_increment"])
        self.assertTrue(r["M_rank_increment"])
        self.assertTrue(r["C_rank_increment_modulo_M"])
    def test_C_dependent_modulo_M(self):
        r=rank_probe([{(1,):1,(2,):2}],(1,),(2,),1000003)
        self.assertTrue(r["C_rank_increment"])
        self.assertFalse(r["C_rank_increment_modulo_M"])
    def test_C_in_original_rowspace(self):
        r=rank_probe([{(1,):1}],(1,),(2,),1000003)
        self.assertFalse(r["C_rank_increment"])
        self.assertFalse(r["C_rank_increment_modulo_M"])
