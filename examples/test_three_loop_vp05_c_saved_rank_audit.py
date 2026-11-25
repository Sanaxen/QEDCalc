import unittest
from examples.three_loop_vp05_c_saved_rank_audit import fixed_minor

class FixedMinorTests(unittest.TestCase):
    def test_order_and_residues(self):
        rows=[{(2,):2,(3,):3},{(1,):5,(2,):7}]
        self.assertEqual(fixed_minor(rows,[(2,),(1,)],1000003),([2,5],10))
    def test_nontrivial_elimination(self):
        self.assertEqual(fixed_minor([{(0,):2,(1,):3},{(0,):4,(1,):7}],[(0,),(1,)],101),([2,1],2))
    def test_zero_pivot_refused(self):
        with self.assertRaises(RuntimeError):
            fixed_minor([{(1,):1}],[(0,)],101)
    def test_duplicate_columns_refused(self):
        with self.assertRaises(ValueError):
            fixed_minor([{(0,):1},{(0,):1}],[(0,),(0,)],101)
