import unittest
from examples import three_loop_vp05_parent_substitution as m

class ParentTests(unittest.TestCase):
    def test_substitution(self):
        x=m.f.scalar(69);c=m.f.a.CAND
        y=list(x);y[0]=0;y=tuple(y)
        z=list(x);z[1]=-7;z=tuple(z)
        row,used,blocked=m.substitute({x:m.sp.S.One,c:-2,y:3,z:4},lambda k:2)
        self.assertEqual(row,{z:4})
        self.assertEqual(used,{x:2,y:0})
        self.assertEqual(blocked,{z:(7,0)})
    def test_protected_candidate(self):
        x=m.f.scalar(69);c=m.f.a.CAND
        e=m.Echelon(101,{c},float("inf"))
        e.insert({x:1,c:98})
        self.assertEqual(e.target(x)["remainder"],[[list(c),3]])
        self.assertTrue(e.target(x)["candidate_only"])
        e.insert({c:1})
        self.assertEqual(e.candidate_relations,1)
    def test_unknown_target(self):
        e=m.Echelon(101,{m.f.a.CAND},float("inf"))
        self.assertFalse(e.target(m.f.scalar(69))["candidate_only"])

if __name__=="__main__":unittest.main()
