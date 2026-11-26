import unittest
from examples import three_loop_vp05_parent_demand as m

class ParentDemandTests(unittest.TestCase):
    def test_parent_masks(self):
        self.assertEqual(m.one_line_parents(69,69|2|8),(71,77))
        self.assertEqual(m.one_line_parents(69,196),())
    def test_envelope(self):
        rows=list(m.boundary_seeds(69|2,5,1,1))
        self.assertEqual(len(rows),45)
        self.assertEqual(len(set(rows)),45)
        self.assertTrue(all(m.sector(ex)==71 and m.scope(ex,5,1,1) for ex in rows))
    def test_symbolic_cancellation(self):
        ex=(1,1)+(0,)*10
        zero=(0,)*12
        a=list(zero);a[1]=m.old.Z
        b=list(zero);b[0]=-m.old.Z
        entries=[(0,tuple(a)),(0,tuple(b))]+[(0,zero)]*10
        r=m.exact_row(ex,entries,0,1)
        self.assertEqual(r[(2,0)+(0,)*10],-m.old.Z)
        self.assertEqual(r[(0,2)+(0,)*10],m.old.Z)

if __name__=="__main__":unittest.main()
