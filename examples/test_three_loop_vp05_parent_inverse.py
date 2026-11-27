import unittest
from examples import three_loop_vp05_parent_inverse as m

class InverseTests(unittest.TestCase):
    def test_inverse_contains_actual_source(self):
        spec=m.old.build_family_spec("VP05_full")
        kernel=m.old.build_kernel(spec.propagators)
        seed=m.f.scalar(204)
        for ij,entries in kernel.items():
            for target in m.q.exact_row(seed,entries,*ij):
                self.assertIn(ij,m.inverse_seeds(target,kernel)[seed])
    def test_exclusion(self):
        seed=m.f.scalar(204)
        self.assertEqual(m.exclusion(seed,{seed},204,"r8s6d2"),"already_seeded")
        self.assertEqual(m.exclusion(m.f.scalar(196),set(),204,"r8s6d2"),"analytic_or_zero")
        self.assertEqual(m.exclusion(m.f.scalar(69),set(),204,"r8s6d2"),"outside_parent")
    def test_normal_form(self):
        c=m.f.a.CAND;x=m.f.scalar(204)
        engine=m.p.Echelon(101,{c},float("inf"))
        engine.insert({x:1,c:98})
        self.assertEqual(m.normal({x:1,c:98},engine),{})
        self.assertEqual(m.normal({x:1},engine),{c:3})
        self.assertEqual(len(engine.piv),1)

if __name__=="__main__":unittest.main()
