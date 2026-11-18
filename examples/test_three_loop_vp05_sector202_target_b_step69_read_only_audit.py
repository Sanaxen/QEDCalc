import unittest
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from examples.three_loop_vp05_sector202_target_b_step69_read_only_audit import (
    manifest,validate_certificate_bridge,STATUS,CHECKPOINT,SOURCE,CERT,
    B_STATE,BACKUP,SCRATCH,COEFF,IBP,
    EXPECTED_STEP68_SHA,EXPECTED_STEP69_SHA,
)
class Step69SavedAuditTests(unittest.TestCase):
    def test_no_path_overlap(self):
        paths=[B_STATE,BACKUP,SCRATCH,COEFF,IBP]
        self.assertEqual(len(paths),len({p.resolve() for p in paths}))
    def test_distinct_coefficient_and_ibp_counts_allowed(self):
        # Regression: coefficient job inventory need not contain 43 keys.
        validate_certificate_bridge(
            {"job_count":200},200,
            {"job_count":43,"coefficient_checkpoint_sha256":"abc"},43,"abc")
        with self.assertRaises(RuntimeError):
            validate_certificate_bridge(
                {"job_count":200},200,
                {"job_count":43,"coefficient_checkpoint_sha256":"wrong"},43,"abc")
        with self.assertRaises(RuntimeError):
            validate_certificate_bridge(
                {"job_count":200},200,
                {"job_count":42,"coefficient_checkpoint_sha256":"abc"},43,"abc")
    def test_complete_exact_coefficient_manifest(self):
        entries=[["remainder",[8,139]],["source",18]]
        cfg={"version":1,"phase":"coeff",
             "formal_step68_sha256":EXPECTED_STEP68_SHA,
             "scratch_step69_sha256":EXPECTED_STEP69_SHA,
             "source_checkpoint_sha256":"a","source_sha256":"b",
             "certificate_sha256":"c","job_count":2,
             "job_sha256":hashlib.sha256(json.dumps(entries,separators=(",",":")).encode()).hexdigest()}
        checked=[{"index":0,"key":[8,139],"kind":"remainder","method":"exact_QQ_z_d_coeff"},
                 {"index":1,"key":18,"kind":"source","method":"exact_QQ_z_d_coeff"}]
        with TemporaryDirectory() as root:
            path=Path(root)/"coeff.json"
            data={"version":1,"status":STATUS,"config":cfg,"checked":checked,
                  "target_b_proven":False,"formal_state_modified":False}
            path.write_text(json.dumps(data),encoding="utf8")
            sha_map={CHECKPOINT:"a",SOURCE:"b",CERT:"c"}
            with patch("examples.three_loop_vp05_sector202_target_b_step69_read_only_audit.sha",
                       side_effect=lambda p:sha_map.get(p)):
                self.assertEqual(manifest("coeff",path)[1],2)
                data["checked"][1]["method"]="numeric_not_exact"
                path.write_text(json.dumps(data),encoding="utf8")
                with self.assertRaises(RuntimeError):
                    manifest("coeff",path)
if __name__=="__main__":
    unittest.main()
