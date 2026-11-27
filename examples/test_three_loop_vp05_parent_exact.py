import unittest
from examples import three_loop_vp05_parent_exact as m

class ExactTests(unittest.TestCase):
    def test_exact_trace(self):
        x=m.f.scalar(204);y=m.f.scalar(76);c=m.f.a.CAND
        pt=m.old.POINTS[0]
        e=m.Trace(pt[0],{c},float("inf"))
        rows=[{y:1,c:-m.f.D},{x:1,y:-2}]
        for i,row in enumerate(rows):e.insert_source(m.p.field_row(row,pt),i)
        free,direct=e.target_trace(x)
        deps=m.dependency_order(e.trace,direct)
        exact=m.Exact(rows,e,pt,float("inf"))
        for k in deps:exact.build(k)
        rem,_=exact.target(x,direct)
        self.assertEqual(rem,{c:2*exact.d})
    def test_collapse(self):
        x=m.f.scalar(76);c=m.f.a.CAND
        self.assertEqual(m.collapse({x:2,c:-2},{x:c}),{})
    def test_dependency_order(self):
        self.assertEqual(m.dependency_order({1:(0,()),2:(1,(1,))},[2,1]),[1,2])

if __name__=="__main__":unittest.main()
