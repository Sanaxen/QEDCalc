import unittest
from examples.three_loop_vp05_sector202_target_b_step66_normalized_ibp_replay import (
    verify_unscaled_key,verify_unscaled_key_field,check_certificate_prefix,DIRECT_COUNT,TOTAL_KEYS,METHOD,
    OUT,PROTECTED,COEFFICIENT,DIRECT,SCRATCH,
)
class Step66NormalizedReplayTest(unittest.TestCase):
    def test_exact_identity_and_bad_coefficient(self):
        k=(1,139)
        self.assertTrue(verify_unscaled_key(k,{k:"z+1"},{k:[("1/2","2*(z+1)")] }))
        with self.assertRaises(AssertionError):
            verify_unscaled_key(k,{k:"z+2"},{k:[("1/2","2*(z+1)")] })
        self.assertTrue(verify_unscaled_key((2,139),{},{}))
        self.assertTrue(verify_unscaled_key_field(k,{k:"z+1"},
            {k:[("1/2","2*(z+1)")]}))
        self.assertTrue(verify_unscaled_key_field((2,139),{},{}))
        with self.assertRaises(AssertionError):
            verify_unscaled_key_field(k,{k:"z+2"},
                {k:[("1/2","2*(z+1)")]})
        self.assertTrue(verify_unscaled_key_field(k,{k:"1"},
            {k:[("1/(z+1)","z"),("1/(z+1)","1")]}))
    def test_direct_prefix_binding(self):
        jobs=[(i,139) for i in range(2)]
        rows=[{"index":0,"key":[0,139],"method":"original_source_delta_exact"}]
        self.assertTrue(check_certificate_prefix(rows,jobs,"original_source_delta_exact"))
        with self.assertRaises(RuntimeError):
            check_certificate_prefix([{"index":0,"key":[0,139],"method":"unverified"}],
                jobs,"original_source_delta_exact")
    def test_protected_paths_distinct(self):
        paths=[p.resolve() for p,_ in PROTECTED]+[
            SCRATCH.resolve(),COEFFICIENT.resolve(),DIRECT.resolve(),OUT.resolve()]
        self.assertEqual(len(paths),len(set(paths)))
        self.assertEqual((DIRECT_COUNT,TOTAL_KEYS),(113,330))
        self.assertIn("259",METHOD)
if __name__=="__main__":
    unittest.main()
