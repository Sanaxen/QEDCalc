"""Offline regressions for the crash-resumable Step77+ exact batch controller."""
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from examples import three_loop_vp05_sector202_target_b_continuous_batch as m

class ContinuousBatchTests(unittest.TestCase):
    def test_bounds_and_sha(self):
        self.assertEqual(m.START,77)
        self.assertEqual(m.END_STATUS,"AUDITED_PREFIX_NOT_TARGET_PROOF")
        self.assertEqual(m.digest(b"hello"),hashlib.sha256(b"hello").hexdigest())
        self.assertNotEqual(m.WORK,m.B_STATE)
        self.assertNotEqual(m.WORK,m.STEP78_SCRATCH)

    def test_atomic_phase_checkpoint_resume(self):
        with TemporaryDirectory() as d:
            path=Path(d)/"coeff.json"
            manifest={"phase":"coeff","step":79,"job_count":3,"job_sha256":"abc"}
            state=m.checked_phase(path,manifest)
            self.assertEqual(state["verified"],0)
            state["verified"]=2
            m.atomic(path,state)
            self.assertEqual(m.checked_phase(path,manifest)["verified"],2)
            with self.assertRaises(RuntimeError):
                m.checked_phase(path,{**manifest,"job_count":4})

    def test_exclusive_snapshot_never_overwrites(self):
        with TemporaryDirectory() as d:
            path=Path(d)/"snapshot.json"
            m.exclusive_bytes(path,b'{"steps":77}')
            with self.assertRaises(FileExistsError):
                m.exclusive_bytes(path,b'{"steps":78}')
            self.assertEqual(path.read_bytes(),b'{"steps":77}')

    def test_phase_update_identity_and_lead(self):
        # Exact arithmetic comes from the independent reusable audit functions.
        self.assertTrue(m.coefficient_identity("remainder","z+2","2","1","z"))
        self.assertTrue(m.coefficient_identity("source","2","z+2","1","z"))
        self.assertFalse(m.coefficient_identity("source","2","z+3","1","z"))

    def test_missing_previous_certificate_fails_resume(self):
        with TemporaryDirectory() as d:
            work=Path(d)/"working.json"
            state={"steps":79,
                "config":{"target":"B","max_columns":256,
                          "max_support":400,"max_expression_chars":7500},
                "remaining":[[[5,139],"1"]]}
            work.write_text(json.dumps(state),encoding="utf8")
            j={"version":1,"start_step":77,"status":m.END_STATUS,
               "initial_scratch_sha256":m.EXPECTED_STEP78_SHA,
               "formal_unchanged":True,"target_b_proven":False,
               "audited_step":79,"max_step":85,"audited_sha256":"a"*64}
            with patch.object(m,"WORK",work), patch.object(m,"certificate_path",
                return_value=Path(d)/"missing_certificate.json"):
                with self.assertRaises(RuntimeError):
                    m.validate_journal(j)

    def test_stale_engine_tmp_quarantined_not_promoted(self):
        with TemporaryDirectory() as d:
            run=Path(d)
            work=run/"working.json"
            work.write_bytes(b'{"steps":77}')
            stale=run/"working.json.tmp"
            stale.write_bytes(b'{"steps":999}')
            with patch.object(m,"RUN_DIR",run),patch.object(m,"WORK",work):
                m.recover_interrupted_engine_tmp()
            self.assertEqual(work.read_bytes(),b'{"steps":77}')
            self.assertFalse(stale.exists())
            self.assertEqual(len(list((run/"quarantine").glob("*.tmp"))),1)

    def test_resume_checks_initial_scratch_hash(self):
        with TemporaryDirectory() as d:
            work=Path(d)/"working.json"
            state={"steps":78,
                "config":{"target":"B","max_columns":256,
                          "max_support":400,"max_expression_chars":7500},
                "remaining":[[[5,139],"1"]]}
            work.write_text(json.dumps(state))
            j={"version":1,"start_step":77,"status":m.END_STATUS,
               "initial_scratch_sha256":m.EXPECTED_STEP78_SHA,
               "formal_unchanged":True,"target_b_proven":False,
               "audited_step":77,"max_step":93,
               "audited_sha256":m.EXPECTED_STEP77_SHA}
            with patch.object(m,"WORK",work):
                with self.assertRaisesRegex(RuntimeError,"Initial saved Step78"):
                    m.validate_journal(j)

if __name__=="__main__":
    unittest.main()
