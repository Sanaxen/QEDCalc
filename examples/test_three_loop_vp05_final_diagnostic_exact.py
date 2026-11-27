import unittest
from examples import three_loop_vp05_final_diagnostic_exact as m

class FinalDiagnosticTests(unittest.TestCase):
    def test_rational_rules(self):
        field,z,d=m.sp.polys.fields.field("z,d",m.sp.QQ)
        x=m.cov.R;y=m.cov.J;k=m.f.a.CAND
        self.assertEqual(m.ce.collapse({x:field.one,y:field.one},{x:{k:z/d},y:{k:-z/d}},field),{})
    def test_points(self):
        self.assertEqual(len(set((*m.old.POINTS,*m.retry.POINTS))),5)
        self.assertTrue(all(m.sp.isprime(pt[0]) for pt in (*m.old.POINTS,*m.retry.POINTS)))
    def test_direct_certificate(self):
        point=m.old.POINTS[1];target=m.cov.R;candidate=m.f.a.CAND
        eng=m.exact.Trace(point[0],{candidate},float("inf"))
        builder=m.retry.DiagnosticExact([],eng,point,float("inf"))
        cert,result=m.retry.make_certificate(builder,[],target,[],[],{target:{candidate:builder.field.one}},[],point)
        self.assertEqual(result,{candidate:builder.field.one})
        self.assertEqual(cert["pivots"],[])

if __name__=="__main__":unittest.main()
