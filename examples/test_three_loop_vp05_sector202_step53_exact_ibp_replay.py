"""Offline tests for strict Step53 candidate materialization and replay guard."""
import unittest
from examples.three_loop_vp05_sector202_step53_exact_ibp_replay import (
    materialize, check_progress,
)


class Step53ReplayTests(unittest.TestCase):
    def setUp(self):
        self.state = {"remaining": [[[1,139],"z"], [[2,139],"1"]],
                      "source": [[4,"1"]]}
        self.jobs = [("remainder",(1,139),"1")]
        self.records = [{"index":0, "id":"remainder:1,139",
                         "kind":"remainder","key":[1,139],
                         "value":"0", "chars":1,
                         "exact_local_identity":True,"within_formal_cap":True}]

    def test_replay_progress_requires_exact_hash(self):
        cfg={"column_count":364}
        good={"version":1,"config":cfg,
              "status":"STEP53_EXACT_IBP_REPLAY_PREFIX_NOT_TARGET_PROOF",
              "checked":124,"exact_target_proven":False,
              "formal_target_state_modified":False}
        check_progress(good,cfg)
        for bad in (-1, 365, True):
            with self.assertRaises(RuntimeError):
                check_progress({**good,"checked":bad},cfg)
        with self.assertRaises(RuntimeError):
            check_progress({**good,"config":{}},cfg)

    def test_reject_incomplete_candidate(self):
        with self.assertRaises(RuntimeError):
            materialize(self.state,self.jobs,{"done":self.records})


if __name__ == "__main__":
    unittest.main()
