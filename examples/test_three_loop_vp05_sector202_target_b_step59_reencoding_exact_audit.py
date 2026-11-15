"""Pure regression checks for Step59 re-encoding exact identity method."""
import unittest
from examples.three_loop_vp05_sector202_target_b_step59_reencoding_exact_audit import (
    CURRENT_CAP_STOP_SHA, exact_check,
)
class ReencodingAuditTests(unittest.TestCase):
    def test_hash_pin(self):
        self.assertEqual(CURRENT_CAP_STOP_SHA,
            "a5a341737487cc4a1f2e20323b1adc927ead02e043af44db4442857a7cfdc38a")
    def test_exact_equivalence(self):
        self.assertTrue(exact_check("1/(z+1)", "(z+1)**(-1)"))
        self.assertFalse(exact_check("1/(z+1)", "1/(z+2)"))
if __name__=="__main__":
    unittest.main()
