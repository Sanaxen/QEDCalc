import unittest
import sympy as sp
from examples import three_loop_vp05_a_fieldpilot_target_proof as proof
from examples import three_loop_vp05_sector202_target_exact_reduction as exact

class TargetProofTests(unittest.TestCase):
    def test_exact_two_step_and_original_replay(self):
        z,d=sp.symbols("z d")
        a,b=(0,),(1,)
        rows={10:{"terms":[{"key":[0],"coefficient":"1"},{"key":[1],"coefficient":"z"}]},
              20:{"terms":[{"key":[1],"coefficient":"1"}]}}
        pivots={a:({a:sp.S.One,b:z},{10:sp.S.One}),
                b:({b:sp.S.One},{20:sp.S.One})}
        initial={a:sp.S.One,b:d}
        source,steps=proof.reduce_field(initial,pivots)
        self.assertEqual(steps,2)
        self.assertEqual(sp.cancel(source[20]-(d-z)),0)
        self.assertTrue(exact.replay(source,rows,z,d,initial))
    def test_unresolved_lead(self):
        with self.assertRaisesRegex(RuntimeError,"UNRESOLVED_LEAD"):
            proof.reduce_field({(0,):sp.S.One},{})
    def test_step_cap(self):
        with self.assertRaisesRegex(RuntimeError,"STEP_CAP"):
            proof.reduce_field({(0,):sp.S.One},{(0,):({(0,):sp.S.One},{1:sp.S.One})},max_steps=0)
    def test_nonzero_wrong_provenance_rejected_by_replay(self):
        z,d=sp.symbols("z d")
        rows={1:{"terms":[{"key":[0],"coefficient":"2"}]}}
        self.assertFalse(exact.replay({1:sp.S.One},rows,z,d,{(0,):sp.S.One}))
