import unittest
from examples import three_loop_vp05_residual_structure as m

class StructureTests(unittest.TestCase):
    def setUp(self):
        self.props=m.old.build_family_spec("VP05_full").propagators
    def test_inverse(self):
        self.assertEqual(len(m.inverse_polys(self.props)),12)
    def test_massive_not_zero(self):
        self.assertIsNone(m.massless_factor(m.f.scalar(73),self.props))
    def test_affine_scalar(self):
        src=m.f.scalar(71);dst=m.f.scalar(78)
        mapping=m.r.affine_match(src,dst,self.props,float("inf"))
        self.assertIsNotNone(mapping)
        row,poly=m.affine_expansion(src,mapping,self.props,m.inverse_polys(self.props))
        self.assertEqual(row,{dst:1})
        self.assertEqual(poly,"1")
    def test_numerator_identity(self):
        src=m.f.scalar(71);dst=m.f.scalar(78)
        mapping=m.r.affine_match(src,dst,self.props,float("inf"))
        key=list(src);key[3]=-2
        row,_=m.affine_expansion(tuple(key),mapping,self.props,m.inverse_polys(self.props))
        self.assertTrue(row)
        self.assertTrue(all(len(k)==12 for k in row))

if __name__=="__main__":unittest.main()
