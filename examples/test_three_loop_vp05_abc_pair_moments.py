import unittest
from examples import three_loop_vp05_abc_pair_moments as m

class PairMomentsTests(unittest.TestCase):
    def test_compact_coefficients(self):
        P,Q,R,z=m.sp.symbols("P Q R z")
        B,H,C,T=m.sp.symbols("B H C T")
        M=(z+8)*C/6+m.sp.Rational(4,3)*T
        A=(2-z/4)*M+(B-H)/4+2*T
        coeff=m.compact(P,Q,R,z)
        actual=sum(coeff[k]*x for k,x in zip(("B","H","C","T"),(B,H,C,T)))
        self.assertEqual(m.sp.cancel(actual-(P*A+Q*B+R*C)),0)
    def test_exact_row_comparison(self):
        z=m.old.Z
        m.require_equal({m.T:(z*z-1)/(z-1)},{m.T:z+1},"equal")
        with self.assertRaises(RuntimeError):
            m.require_equal({m.T:1},{m.T:2},"different")
    def test_pair_polynomial_identity(self):
        b=m.b
        props=b.old.build_family_spec("VP05_full").propagators
        _,_,lines,_=b.geometry(props)
        from itertools import combinations
        lhs=sum(b.sq(x+y) for x,y in combinations(lines,2))
        rhs=b.old.Z+2*sum(b.sq(x) for x in lines)
        self.assertEqual(m.sp.expand(lhs-rhs),0)

if __name__=="__main__":unittest.main()
