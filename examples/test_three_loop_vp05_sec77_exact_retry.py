import unittest
from examples import three_loop_vp05_sec77_exact_retry as m

class RetryTests(unittest.TestCase):
    def test_points(self):
        self.assertEqual(len(set((*m.old.POINTS,*m.POINTS))),5)
        self.assertTrue(all(m.sp.isprime(pt[0]) for pt in m.POINTS))
    def test_specialization_diagnostic(self):
        pt=m.old.POINTS[0]
        x,y=sorted([m.f.scalar(77),m.f.scalar(71)],key=m.f.e.b.c.key,reverse=True)
        c=m.f.a.CAND
        rows=[{x:m.f.Z-pt[1],y:m.sp.S.One,c:-m.sp.S.One}]
        eng=m.make_trace(rows,{c},pt,float("inf"))
        builder=m.DiagnosticExact(rows,eng,pt,float("inf"))
        with self.assertRaisesRegex(RuntimeError,"Exact leading key differs"):
            builder.build(y)
        self.assertEqual(builder.failure["exact_lead"],list(x))
        self.assertEqual(builder.failure["evaluations"][0]["value"],0)
    def test_alternate_point(self):
        pt=m.POINTS[0];c=m.f.a.CAND;x=m.f.scalar(77)
        rows=[{x:m.f.Z-17,c:-m.sp.S.One}]
        eng=m.make_trace(rows,{c},pt,float("inf"))
        b=m.DiagnosticExact(rows,eng,pt,float("inf"))
        b.build(x);rem,_=b.target(x,[x])
        self.assertEqual(rem,{c:1/(b.z-17)})

if __name__=="__main__":unittest.main()
