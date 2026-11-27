import unittest
from examples import three_loop_vp05_residual_covariance as m

class CovarianceTests(unittest.TestCase):
    def setUp(self):
        self.props=m.old.build_family_spec("VP05_full").propagators
    def test_projection(self):
        row,cert=m.covariance_row(m.J,self.props,m.s.inverse_polys(self.props))
        self.assertTrue(row)
        expr=m.sp.sympify(cert["projected_polynomial"])
        self.assertFalse(any(expr.has(m.old.dot(i,4)) for i in range(3)))
    def test_scope(self):
        with self.assertRaisesRegex(RuntimeError,"Single numerator scope"):
            m.covariance_row(m.f.scalar(228),self.props,m.s.inverse_polys(self.props))
    def test_combined_symmetry(self):
        base=m.f.scalar(228);num=list(base);num[4]=-1
        candidates={base,tuple(num),m.f.a.CAND}
        _,sym=m.m.symmetry228([m.R],candidates,self.props,float("inf"))
        results,cert=m.solve([m.R,m.J],candidates,self.props,float("inf"),sym)
        self.assertEqual(len(results),2)
        self.assertGreater(cert["covariance_equations"],0)
        for rec in results:
            if rec["kind"]!="unresolved":
                self.assertTrue(set(m.p.decode(rec["rule"]))<=candidates)

if __name__=="__main__":unittest.main()
