import unittest
import sympy as sp
from examples.three_loop_vp05_sector202_target_b_step66_original_ibp_replay import (
    verify_key, rows_dict, EXPECTED_STEP66_SHA, SAVED_STEP65_SHA,
)

class Step66ExactReplayTests(unittest.TestCase):
    def test_pinned_shas(self):
        self.assertEqual(EXPECTED_STEP66_SHA,"9b30bed319c5e23cc84016acdb1605fe8082bedb09c84a4f8f4d8f676de82d7d")
        self.assertEqual(SAVED_STEP65_SHA,"eeab74cfde337424db3e8d54de8078c3f82c994a0a35a689531842d79a8c941f")
    def test_exact_delta_and_tampering(self):
        # original row: 2*x + (z+1)*y = 0; old=x, new=-(z+1)*y/2
        original={1:{"terms":[{"key":[1,139],"coefficient":"2"},
                              {"key":[2,139],"coefficient":"z+1"}]}}
        old={(1,139):"1"}
        new={(2,139):"-(z+1)/2"}
        self.assertTrue(verify_key((1,139),old,new,{}, {1:"1/2"},original))
        self.assertTrue(verify_key((2,139),old,new,{}, {1:"1/2"},original))
        with self.assertRaises(AssertionError):
            verify_key((2,139),old,{(2,139):"-(z+2)/2"},{},{1:"1/2"},original)
    def test_duplicate_rejection(self):
        with self.assertRaises(RuntimeError):
            rows_dict([[[1,139],"1"],[[1,139],"2"]],True)

if __name__=="__main__":
    unittest.main()
