import unittest
from unittest.mock import patch
from examples import three_loop_vp05_stage2_coverage_inventory as m

class CoverageTests(unittest.TestCase):
    def test_distinct_evidence(self):
        a,b,c,d,e=[(i,1)+(0,)*10 for i in range(1,6)]
        rows=m.classify({a,b,c,d,e},{a},{b:{"sha256":"test"}},{c:[]},{d:{"archive_verified":True}},{3:["r9s5d2"]})
        self.assertEqual([r["classification"] for r in rows],["candidate_identity","audited_candidate_reduction","replayed_analytic_rule","restricted_target_evidence_review","no_direct_target_certificate"])
        self.assertEqual(rows[-1]["local_boundary_seeds"],["r9s5d2"])
    def test_duplicate_rejected(self):
        target="VP05_full[1,0,0,0,0,0,0,0,0,0,0,0]"
        with self.assertRaisesRegex(RuntimeError,"duplicate"):
            m.keys([target,target])
    def test_boundary_not_promoted(self):
        groups={1:["VP05_full[1,0,0,0,0,0,0,0,0,0,0,0]"]}
        live={"restricted_exact_sector_audit_match":False,"matching_local_master_inventory":True}
        with patch.object(m.inventory,"analyze_sector",return_value=live):
            rows=m.boundary_rows(groups,"r9s5d2",{})
        self.assertEqual(rows[0]["classification"],"local_inventory_only")
        self.assertFalse(rows[0]["full_seed_closure_proven"])

if __name__=="__main__":unittest.main()
