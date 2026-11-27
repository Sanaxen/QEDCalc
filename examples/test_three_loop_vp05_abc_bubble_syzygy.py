import unittest
from examples import three_loop_vp05_abc_bubble_syzygy as m

class SyzygyTests(unittest.TestCase):
    def test_divisibility(self):
        vectors=list(m.vectors(3))
        self.assertTrue(vectors)
        for A,C in vectors:
            for v,f in ((2*m.x*A+m.a.S*C,m.a.F),(m.a.S*A+2*m.y*C,m.a.G)):
                self.assertFalse(m.sp.denom(m.sp.cancel(v/f)).has(m.x,m.y))
    def test_degree_zero(self):
        self.assertEqual(list(m.vectors(0)),[])
    def test_outer_replay(self):
        for A,C in m.vectors(3):
            row=m.a.outer(A,C)
            self.assertTrue(all(not v.free_symbols-{m.d,m.z} for v in row.values()))

if __name__=="__main__":unittest.main()
