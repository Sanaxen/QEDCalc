import unittest
from examples import three_loop_vp05_stage2_boundary_recovery as m

class RecoveryTests(unittest.TestCase):
    def test_seed_specific_and_no_promotion(self):
        rows=[{"seed":s,"sector":78,"classification":"missing_or_failed_local_evidence"} for s in ("r8s5d3","r8s6d2")]
        out=m.merge(rows,{("r8s5d3",78):{"state":"completed_local_retained"}})
        self.assertTrue(out[0]["local_evidence_present"])
        self.assertFalse(out[1]["local_evidence_present"])
        self.assertFalse(any(x["full_seed_closure_proven"] for x in out))
    def test_stopped_not_pass(self):
        row={"seed":"r8s5d3","sector":206,"classification":"missing_or_failed_local_evidence"}
        self.assertFalse(m.merge([row],{("r8s5d3",206):{"state":"guard_stopped"}})[0]["local_evidence_present"])
    def test_existing_evidence_retained(self):
        row={"seed":"r9s5d2","sector":73,"classification":"saved_local_pass_inventory_match"}
        self.assertTrue(m.merge([row],{})[0]["local_evidence_present"])

if __name__=="__main__":unittest.main()
