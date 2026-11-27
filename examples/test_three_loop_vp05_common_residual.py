import unittest
from examples import three_loop_vp05_common_residual as m

class ResidualTests(unittest.TestCase):
    def test_apply_rules(self):
        x=m.f.scalar(76);y=m.f.scalar(140);u=m.f.scalar(71);c=m.f.a.CAND
        pt=m.old.POINTS[0]
        checks=[{"point":list(pt),"targets":[{"target":list(u),"remainder":[[list(x),2],[list(y),3],[list(u),4]]}]}]
        records=[{"integral":list(x),"kind":"affine","rule":[[list(c),"1"]]},
                 {"integral":list(y),"kind":"factorized","rule":[[list(c),"d/2-1"]]},
                 {"integral":list(u),"kind":"unresolved","rule":[]}]
        result=m.apply(checks,records,{c})[0]["targets"][0]
        self.assertFalse(result["candidate_only"])
        self.assertEqual(dict((tuple(k),v) for k,v in result["remainder"]),{c:(2+3*m.f.evaluate(m.f.D/2-1,pt))%pt[0],u:4})
    def test_zero_rule(self):
        x=m.f.scalar(4);c=m.f.a.CAND
        checks=[{"point":list(m.old.POINTS[0]),"targets":[{"target":list(x),"remainder":[[list(x),1]]}]}]
        result=m.apply(checks,[{"integral":list(x),"kind":"free_loop_zero","rule":[]}],{c})[0]["targets"][0]
        self.assertTrue(result["candidate_only"])
        self.assertEqual(result["remainder"],[])

if __name__=="__main__":unittest.main()
