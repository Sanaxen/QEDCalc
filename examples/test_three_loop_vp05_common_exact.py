import copy
import unittest
from examples import three_loop_vp05_common_exact as m

class CommonExactTests(unittest.TestCase):
    def setUp(self):
        self.x=m.f.scalar(77);self.c=m.f.scalar(201)
        self.y=m.f.scalar(67);self.z=m.f.a.CAND
        self.v=m.Verifier({self.c,self.z},float("inf"))
    def test_direct_identity_empty_dag(self):
        cert={"target":list(self.x),"pivots":[],"target_dependencies":[],
              "remainder_before_identity":[[list(self.x),"1"]],
              "remainder":[[list(self.c),"1"]]}
        rules={self.x:{self.c:self.v.field.one}}
        expected=[(pt,{"candidate_only":True,"remainder":[[list(self.c),1]]}) for pt in m.old.POINTS]
        self.assertEqual(self.v.target_rule(cert,None,rules,expected),0)
        wrong=copy.deepcopy(cert);wrong["remainder"][0][1]="2"
        with self.assertRaisesRegex(RuntimeError,"Candidate remainder mismatch"):
            self.v.target_rule(wrong,None,rules,expected)
    def test_rational_and_zero_rules(self):
        field=self.v.field
        row={self.x:field.one,self.y:field.one,self.c:-field.one}
        rules={self.x:{self.c:field.one},self.y:{self.z:self.v.d/2-1}}
        self.assertEqual(m.collapse(row,rules,field),{self.z:self.v.d/2-1})
        self.assertEqual(m.collapse({self.x:field.one},{self.x:{}},field),{})

if __name__=="__main__":unittest.main()
