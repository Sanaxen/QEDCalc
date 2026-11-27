import copy
import unittest
from examples import three_loop_vp05_parent_exact_audit as m

class AuditTests(unittest.TestCase):
    def setUp(self):
        self.x=m.f.scalar(204);self.c=m.f.a.CAND
        self.v=m.Verifier({self.c},float("inf"))
        self.rec={"lead":list(self.x),"source":0,"divisor":"2","dependencies":[],
                  "row":[[list(self.x),"1"],[list(self.c),"-d"]]}
    def source(self,ref):
        return {self.x:2,self.c:-2*m.f.D}
    def test_pivot_and_shared(self):
        self.v.pivot(self.rec,self.source,set())
        self.v.pivot(self.rec,self.source,set())
        self.assertEqual(len(self.v.pivots),1)
    def test_bad_divisor(self):
        rec=copy.deepcopy(self.rec);rec["divisor"]="3"
        with self.assertRaisesRegex(RuntimeError,"Nonzero exact pivot"):
            self.v.pivot(rec,self.source,set())
    def test_bad_shared(self):
        self.v.pivot(self.rec,self.source,set())
        rec=copy.deepcopy(self.rec);rec["divisor"]="3"
        with self.assertRaisesRegex(RuntimeError,"Conflicting shared"):
            self.v.pivot(rec,self.source,set())
    def test_target(self):
        cert={"target":list(self.x),"pivots":[self.rec],
              "target_dependencies":[[list(self.x),"1"]],
              "remainder_before_identity":[[list(self.c),"d"]],
              "remainder":[[list(self.c),"d"]],"identities":[]}
        expected=[(pt,{"candidate_only":True,"remainder":[[list(self.c),pt[2]]]}) for pt in m.old.POINTS]
        self.assertEqual(self.v.target(cert,self.source,{},expected),1)
        cert["target_dependencies"][0][1]="2"
        with self.assertRaisesRegex(RuntimeError,"Nonzero exact target"):
            self.v.target(cert,self.source,{},expected)

if __name__=="__main__":unittest.main()
