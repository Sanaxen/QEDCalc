import unittest
from examples import three_loop_vp05_boundary_symmetry as m
class SymmetryTests(unittest.TestCase):
    def test_permutation(self):
        x,y=m.sp.symbols("x y")
        self.assertEqual(m.permutation_of_polynomials([y,x],[x,y]),(1,0))
        self.assertIsNone(m.permutation_of_polynomials([x+y,x],[x,y]))
    def test_orbits(self):
        keys=[(1,2),(2,1),(1,1)]
        self.assertEqual(m.orbits(keys,[(0,1),(1,0)]),[((1,1),1),((1,2),2)])
    def test_nonclosed(self):
        with self.assertRaises(RuntimeError):
            m.orbits([(1,2)],[(0,1),(1,0)])
if __name__=="__main__":unittest.main()
