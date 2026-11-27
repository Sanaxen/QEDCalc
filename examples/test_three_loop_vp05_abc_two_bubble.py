import unittest
from examples import three_loop_vp05_abc_two_bubble as m

class TwoBubbleTests(unittest.TestCase):
    def test_inner_ode(self):
        self.assertTrue(m.check_inner())
    def test_sources(self):
        rows=list(m.sources())
        self.assertEqual(len(rows),12)
        self.assertTrue(all(row for _,row in rows))
        self.assertTrue(all(not (v.free_symbols-{m.d,m.z}) for _,row in rows for v in row.values()))
    def test_symmetry_and_tadpole(self):
        row={}
        m.polynomial(row,m.x+m.y,"JJ")
        self.assertEqual(row,{("JJ",1,0):2})
        row={}
        m.polynomial(row,1,"UJ")
        self.assertEqual(row,{("T",0,0):m.d/2-1})
    def test_exact_certificate(self):
        a=("JJ",2,0); b=("JJ",1,1); c=("T",0,0)
        rows=[{a:m.sp.S.One,b:m.sp.S.One},{b:m.sp.S.One,c:m.sp.S.One}]
        target={a:m.sp.S.One,c:-m.sp.S.One}
        rem,used,rank=m.reduce_exact(rows,target)
        self.assertFalse(rem)
        self.assertEqual(rank,2)
        self.assertEqual(used,{0:1,1:-1})
    def test_uncleared_derivative(self):
        with self.assertRaises(RuntimeError):
            m.outer(m.sp.S.One,m.sp.S.Zero)

if __name__=="__main__":unittest.main()
