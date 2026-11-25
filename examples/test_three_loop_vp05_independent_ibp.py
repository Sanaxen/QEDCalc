import unittest
from examples.three_loop_vp05_independent_ibp import seeds,row,insert,SECTORS
class IBPTests(unittest.TestCase):
    def test_seeds(self):
        for s in SECTORS:
            a=list(seeds(s,1))
            self.assertEqual(len(a),100)
            self.assertEqual(len(set(a)),100)
            self.assertTrue(all(sum(1<<i for i,x in enumerate(t) if x>0)==s for t in a))
    def test_tadpole(self):
        self.assertEqual(row((2,),[(2,(2,))],0,0,7),{(2,):3,(3,):-4})
    def test_rank(self):
        p={}
        n,inc=insert({(1,):2,(2,):3},p,101,0)
        self.assertTrue(inc)
        self.assertEqual(insert({(1,):4,(2,):6},p,101,n),(0,False))
