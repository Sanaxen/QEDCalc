import unittest
from examples.three_loop_vp05_c_exact_rank_certificate import evaluator,minor_certificate

class RankCertificateTests(unittest.TestCase):
    def test_rational_specialization(self):
        ev=evaluator((1000003,17,7))
        self.assertEqual(ev("(z+d)/2"),12)
        self.assertEqual(ev("z^2-d"),282)
    def test_pole_rejected(self):
        ev=evaluator((1000003,17,7))
        with self.assertRaises(ZeroDivisionError):
            ev("1/(z-17)")
    def test_ordered_minor(self):
        # First pivot column is larger than the second; determinant
        # is computed in discovery order without column-swap ambiguity.
        rows=[{(2,):2,(3,):3},{(1,):5,(2,):7}]
        r=minor_certificate(rows,1000003)
        self.assertEqual(r["ordered_columns"],[[2],[1]])
        self.assertEqual(r["determinant_mod_p"],10)
    def test_dependent_rejected(self):
        with self.assertRaises(RuntimeError):
            minor_certificate([{(1,):1},{(1,):2}],1000003)
