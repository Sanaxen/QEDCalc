import unittest
from examples import three_loop_vp05_parent_frontier as m

class FrontierTests(unittest.TestCase):
    def test_nonvacuous_targets(self):
        x=m.f.scalar(204);y=list(x);y[2]+=1;y=tuple(y)
        self.assertEqual(m.select_targets([{x:1,y:2}],204,{x},"r8s6d2"),[y])
    def test_frontier_retains_unknowns(self):
        x=m.f.scalar(204);y=list(x);y[2]+=1;y=tuple(y)
        hard=m.f.scalar(196)
        checks=[{"targets":[{"remainder":[[list(k),1] for k in (x,y,hard)]}]}]
        self.assertEqual(m.frontier(checks,{x},204,"r8s6d2",set()),[y])
    def test_scope(self):
        x=m.f.scalar(204);y=list(x);y[0]=-7
        self.assertFalse(m.q.scope(tuple(y),*m.limits("r8s6d2")))

if __name__=="__main__":unittest.main()
