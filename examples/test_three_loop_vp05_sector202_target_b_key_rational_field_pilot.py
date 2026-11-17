import unittest
from examples.three_loop_vp05_sector202_target_b_key_rational_field_pilot import exact_field_check
class ExactRationalFieldPilotTests(unittest.TestCase):
    def test_exact_cancel_across_fractions(self):
        self.assertTrue(exact_field_check("1",[
            ("1/(z+1)","z"),("1/(z+1)","1")]))
        self.assertTrue(exact_field_check("0",[
            ("1/(z+1)","d"),("-1/(z+1)","d")]))
    def test_exact_mismatch_rejected(self):
        with self.assertRaises(AssertionError):
            exact_field_check("1",[
                ("1/(z+1)","z+2")])
if __name__=="__main__":
    unittest.main()
