import unittest
from examples import three_loop_vp05_residual_moments as m

class MomentTests(unittest.TestCase):
    def setUp(self):
        self.props=m.old.build_family_spec("VP05_full").propagators
    def test_bubble(self):
        candidates={m.f.scalar(78),m.f.a.CAND}
        result=m.bubble71(self.props,candidates,float("inf"))
        self.assertEqual(result["kind"],"bubble_tadpole_tensor")
        self.assertTrue(set(m.p.decode(result["rule"]))<=candidates)
    def test_symmetry(self):
        maps=list(m.maps228(self.props,float("inf")))
        self.assertTrue(maps)
        self.assertTrue(all(abs(int(x["determinant"]))==1 for x in maps))
        self.assertTrue(any(x["source_lines"]!=x["destination_lines"] for x in maps))
    def test_radial_normalization(self):
        self.assertEqual(m.f.radial(1,1),1)
        self.assertEqual(m.f.radial(1,2),1)

if __name__=="__main__":unittest.main()
