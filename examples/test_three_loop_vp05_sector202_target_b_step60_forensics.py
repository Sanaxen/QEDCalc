"""Read-only forensic comparator pure regression checks."""
import unittest
from examples.three_loop_vp05_sector202_target_b_step60_forensics import compare_state

class TestStep60Forensics(unittest.TestCase):
    def test_unmodified(self):
        a={"steps":59,"status":"EXACT_TARGET_PREFIX_NOT_PROOF",
           "remaining":[[[1,139],"1/(z+1)"]],"source":[[2,"1"]],
           "pivot_path":[[5,139]],"config":{"target":"B"}}
        d=compare_state(a,a)
        self.assertTrue(d["remaining_keys_equal"])
        self.assertEqual(d["remaining_string_changes"],0)
        self.assertEqual(d["source_string_changes"],0)
    def test_reencoding_detected(self):
        a={"remaining":[[[1,139],"1/(z+1)"]],"source":[[2,"1"]]}
        b={"remaining":[[[1,139],"(z+1)**(-1)"]],"source":[[2,"1"]]}
        d=compare_state(b,a)
        self.assertTrue(d["remaining_keys_equal"])
        self.assertEqual(d["remaining_string_changes"],1)
    def test_changed_keys_detected(self):
        a={"remaining":[[[1,139],"1"]],"source":[]}
        b={"remaining":[[[2,139],"1"]],"source":[]}
        self.assertFalse(compare_state(b,a)["remaining_keys_equal"])
if __name__=="__main__":
    unittest.main()
