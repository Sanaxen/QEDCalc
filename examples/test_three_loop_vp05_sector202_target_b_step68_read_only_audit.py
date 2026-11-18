import unittest
import hashlib
import json
from examples.three_loop_vp05_sector202_target_b_step68_read_only_audit import (
    B_STATE,BACKUP,SCRATCH,COEFF,IBP,STEP67_SCRATCH,
    STEP66_SCRATCH,manifest,STATUS,
)
class Step68SavedAuditTests(unittest.TestCase):
    def test_unique_promotion_and_saved_evidence_paths(self):
        paths=[B_STATE,BACKUP,SCRATCH,COEFF,IBP,STEP67_SCRATCH,STEP66_SCRATCH]
        self.assertEqual(len(paths),len({p.resolve() for p in paths}))
    def test_certificate_method(self):
        from unittest.mock import patch
        from tempfile import TemporaryDirectory
        from pathlib import Path
        from examples.three_loop_vp05_sector202_target_b_step68_read_only_audit import (
            EXPECTED_STEP67_SHA,EXPECTED_STEP68_SHA,CHECKPOINT,SOURCE,CERT,
        )
        with TemporaryDirectory() as td:
            p=Path(td)/"cert.json"
            keys=[["remainder",[1,139]],["source",10]]
            cfg={"version":1,"phase":"coeff",
                "formal_step67_sha256":EXPECTED_STEP67_SHA,
                "scratch_step68_sha256":EXPECTED_STEP68_SHA,
                "source_checkpoint_sha256":"x","source_sha256":"y",
                "certificate_sha256":"z","job_count":2,
                "job_sha256":hashlib.sha256(json.dumps(keys,separators=(",",":")).encode()).hexdigest()}
            state={"version":1,"status":STATUS,"config":cfg,
                "checked":[{"index":0,"key":[1,139],"kind":"remainder","method":"exact_QQ_z_d_coeff"},
                           {"index":1,"key":10,"kind":"source","method":"exact_QQ_z_d_coeff"}],
                "formal_state_modified":False,"target_b_proven":False}
            p.write_text(json.dumps(state))
            with patch("examples.three_loop_vp05_sector202_target_b_step68_read_only_audit.sha",
                       side_effect=lambda path: {CHECKPOINT:"x",SOURCE:"y",CERT:"z"}.get(path)):
                self.assertEqual(manifest("coeff",p)[1],2)
            state["checked"][1]["method"]="not_exact"
            p.write_text(json.dumps(state))
            with patch("examples.three_loop_vp05_sector202_target_b_step68_read_only_audit.sha",
                       side_effect=lambda path: {CHECKPOINT:"x",SOURCE:"y",CERT:"z"}.get(path)):
                with self.assertRaises(RuntimeError):
                    manifest("coeff",p)
if __name__=="__main__":
    unittest.main()
