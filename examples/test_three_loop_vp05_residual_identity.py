import unittest
from examples import three_loop_vp05_residual_identity as m

class ResidualIdentityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.props=m.old.build_family_spec("VP05_full").propagators
    def test_verified_scalar_map(self):
        src=m.f.scalar(196);dst=m.f.a.CAND
        proof=m.affine_match(src,dst,self.props,float("inf"))
        self.assertIsNotNone(proof)
        self.assertEqual(abs(int(proof["determinant"])),1)
        self.assertTrue(proof["numerator_polynomial_verified"])
    def test_rank(self):
        self.assertEqual(m.rank_certificate(m.f.scalar(196),self.props)["loop_rank"],3)
        self.assertTrue(m.rank_certificate(m.f.scalar(4),self.props)["scaleless_free_loop"])
    def test_different_powers(self):
        src=list(m.f.scalar(196));src[2]+=1
        self.assertIsNone(m.affine_match(tuple(src),m.f.a.CAND,self.props,float("inf")))

if __name__=="__main__":unittest.main()
