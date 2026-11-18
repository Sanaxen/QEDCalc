import unittest
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from examples.three_loop_vp05_sector202_target_b_step71_read_only_audit import (
    manifest,validate_certificate_bridge,STATUS,CHECKPOINT,SOURCE,CERT,
    B_STATE,BACKUP,SCRATCH,COEFF,IBP,EXPECTED_STEP70_SHA,EXPECTED_STEP71_SHA
)
class Step71ReadOnlyAuditTests(unittest.TestCase):
    def test_phase_counts_differ_and_sha_binding(self):
        validate_certificate_bridge(
            {"job_count":211},211,
            {"job_count":48,"coefficient_checkpoint_sha256":"abc"},48,"abc")
        with self.assertRaises(RuntimeError):
            validate_certificate_bridge(
                {"job_count":211},211,
                {"job_count":48,"coefficient_checkpoint_sha256":"wrong"},48,"abc")
        with self.assertRaises(RuntimeError):
            validate_certificate_bridge(
                {"job_count":48},48,
                {"job_count":48,"coefficient_checkpoint_sha256":"abc"},48,"abc")
    def test_historical_paths_distinct(self):
        paths=[B_STATE,BACKUP,SCRATCH,COEFF,IBP]
        self.assertEqual(len(paths),len({p.resolve() for p in paths}))
    def test_ordered_exact_manifest(self):
        entries=[["remainder",[8,148]],["source",18]]
        cfg={"version":1,"phase":"coeff",
             "formal_step70_sha256":EXPECTED_STEP70_SHA,
             "scratch_step71_sha256":EXPECTED_STEP71_SHA,
             "source_checkpoint_sha256":"a","source_sha256":"b",
             "certificate_sha256":"c","job_count":2,
             "job_sha256":hashlib.sha256(json.dumps(entries,separators=(",",":")).encode()).hexdigest()}
        checked=[{"index":0,"key":[8,148],"kind":"remainder","method":"exact_QQ_z_d_coeff"},
                 {"index":1,"key":18,"kind":"source","method":"exact_QQ_z_d_coeff"}]
        with TemporaryDirectory() as root:
            path=Path(root)/"coeff.json"
            data={"version":1,"status":STATUS,"config":cfg,"checked":checked,
                  "target_b_proven":False,"formal_state_modified":False}
            path.write_text(json.dumps(data),encoding="utf8")
            sha_map={CHECKPOINT:"a",SOURCE:"b",CERT:"c"}
            with patch("examples.three_loop_vp05_sector202_target_b_step71_read_only_audit.sha",
                       side_effect=lambda p:sha_map.get(p)):
                self.assertEqual(manifest("coeff",path)[1],2)
                data["checked"][1]["method"]="numeric_not_exact"
                path.write_text(json.dumps(data),encoding="utf8")
                with self.assertRaises(RuntimeError):
                    manifest("coeff",path)
if __name__=="__main__":
    unittest.main()
