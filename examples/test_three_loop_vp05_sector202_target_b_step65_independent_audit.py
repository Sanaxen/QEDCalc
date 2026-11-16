"""Step65 independent exact audit safety regression tests."""
import unittest
from examples.three_loop_vp05_sector202_target_b_step65_independent_audit import (
    AUDIT, OUT, STATE, EXPECTED_STEP64_SHA, STEP63_BACKUP, EXPECTED_STEP63_SHA
)
from examples.three_loop_vp05_sector202_target_b_step65_scratch_guard import SCRATCH_SHA
class Step65IndependentAuditTests(unittest.TestCase):
    def test_audited_baseline_sha(self):
        self.assertEqual(EXPECTED_STEP64_SHA,
            "9e5ba49502e24f9367e15b42221086c470dd9670519798e8ab555e147a33992a")
        self.assertEqual(EXPECTED_STEP63_SHA,
            "78bcc7570d5bc8a85b0c478c3b750559e3d73154781889607ac3bde43badf9d5")
        self.assertEqual(SCRATCH_SHA,
            "e7ef7c12cb68cb8492723a864ba80febda9a8a5415581ec4bd1cd2ad15989fcc")
    def test_read_only_inputs_not_checkpoint(self):
        paths=[AUDIT,OUT,STATE,STEP63_BACKUP]
        self.assertEqual(len({p.resolve() for p in paths}),len(paths))
if __name__=="__main__":
    unittest.main()
