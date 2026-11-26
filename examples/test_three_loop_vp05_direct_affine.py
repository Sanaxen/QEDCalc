import unittest
from examples import three_loop_vp05_direct_affine as m

class AffineTests(unittest.TestCase):
    def test_actual_family(self):
        spec=m.old.build_family_spec("VP05_full")
        for sec in (196,200):
            ex=tuple(int(bool(sec&(1<<i))) for i in range(12))
            result=m.affine(spec.propagators,ex,m.CAND)
            self.assertEqual(result["propagators_verified"],3)
            self.assertEqual(result["jacobian_absolute"],1)
        proof=m.moment_proof(spec.propagators)
        self.assertEqual(m.sp.expand(m.sp.sympify(proof["coefficient"])-(m.old.D-2)),0)
        self.assertFalse(proof["original_symbolic_IBP_certificate"])
    def test_invalid_basis(self):
        spec=m.old.build_family_spec("VP05_full")
        with self.assertRaises(RuntimeError):
            m.basis(spec.propagators,(1,)+(0,)*11)

if __name__=="__main__":unittest.main()
