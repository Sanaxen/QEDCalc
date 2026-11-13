"""Fast synthetic checks for Target A proof audit guards (no large source needed)."""
import unittest
from examples.three_loop_vp05_sector202_step93_proof_audit import (
    EXPECTED_STEP93_SHA, STATE, PROOF,
)


class ProofAuditSmokeTests(unittest.TestCase):
    def test_exact_known_state_hash(self):
        self.assertEqual(len(EXPECTED_STEP93_SHA),64)
        self.assertEqual(EXPECTED_STEP93_SHA,
                         "c685cd2627ad4d6f9bea6c7afc0b5e0f6611184b2382b303616283068a54c13c")
    def test_distinct_state_and_proof_paths(self):
        self.assertNotEqual(STATE,PROOF)
        self.assertEqual(PROOF.stem,STATE.stem+"_proof")


if __name__=="__main__":
    unittest.main()
