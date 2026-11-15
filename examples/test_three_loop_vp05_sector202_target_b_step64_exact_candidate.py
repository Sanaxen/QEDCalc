"""Safety checks for hash-pinned Target B Step64 exact coefficient pilot."""
import unittest
from examples.three_loop_vp05_sector202_target_b_step64_exact_candidate import (
    KNOWN_B_STEP63_SHA, OUT, STATE, STEP50_BACKUP, STEP51_BACKUP,
    STEP52_BACKUP, STEP58_BACKUP, STEP59_BACKUP, get_jobs, exact_coefficient,
)
class Step64CandidateTests(unittest.TestCase):
    def test_pinned_checkpoint_hash(self):
        self.assertEqual(KNOWN_B_STEP63_SHA,
            "78bcc7570d5bc8a85b0c478c3b750559e3d73154781889607ac3bde43badf9d5")
    def test_protected_outputs_isolated(self):
        paths=[OUT,STATE,STEP50_BACKUP,STEP51_BACKUP,STEP52_BACKUP,STEP58_BACKUP,STEP59_BACKUP]
        self.assertEqual(len({x.resolve() for x in paths}),len(paths))
    def test_wrong_step_rejected(self):
        with self.assertRaises(RuntimeError):
            get_jobs({"steps":62,"config":{"target":"B"}},{"pivots":[]})
    def test_small_exact_coefficient(self):
        val,_,_=exact_coefficient("1/(z+1)","1","1/(z+1)",-1)
        self.assertEqual(val,"0")
if __name__=="__main__":
    unittest.main()
