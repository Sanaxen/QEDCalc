"""Safety regression tests for independent Step64 exact coefficient audit."""
import unittest
from examples.three_loop_vp05_sector202_target_b_step64_independent_audit import (
    AUDIT, OUT, STATE, EXPECTED_STEP63_SHA, CHECKPOINT, SOURCE, CERT,
)
class Step64IndependentAuditTests(unittest.TestCase):
    def test_sha_pin(self):
        self.assertEqual(EXPECTED_STEP63_SHA,
            "78bcc7570d5bc8a85b0c478c3b750559e3d73154781889607ac3bde43badf9d5")
    def test_output_isolated(self):
        paths=[AUDIT,OUT,STATE,CHECKPOINT,SOURCE,CERT]
        self.assertEqual(len({p.resolve() for p in paths}),len(paths))
        self.assertIn("independent_local_exact_audit_checkpoint",AUDIT.name)
if __name__=="__main__":
    unittest.main()
