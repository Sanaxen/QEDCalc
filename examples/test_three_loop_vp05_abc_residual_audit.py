import unittest
import time
from unittest.mock import patch
from examples import three_loop_vp05_abc_residual_audit as m

class ResidualTests(unittest.TestCase):
    def test_cap_reason(self):
        with patch.object(m.old,"memory_guard"):
            e=m.Trace(1000003,time.monotonic()+60)
            e.ops=m.p.MAX_OPS+1
            with self.assertRaisesRegex(m.Cap,"operations"):
                e.guard({})
            e.ops=0
            e.terms=m.p.MAX_TERMS+1
            with self.assertRaisesRegex(m.Cap,"stored_pivot_terms"):
                e.guard({})
    def test_replay_residual(self):
        A,B,C=m.gap.TARGETS
        with patch.object(m.old,"memory_guard"):
            rows=[{A:m.sp.Integer(1),B:m.sp.Integer(-1)}]
            target={A:m.sp.Integer(1),B:m.sp.Integer(-1),C:m.sp.Integer(2)}
            result=m.replay(rows,[1],target,m.physical.POINTS[0],time.monotonic()+60)[0]
            self.assertTrue(result["completed"])
            self.assertEqual(result["residual"],[[list(C),2]])
            self.assertEqual(result["rank"],1)

if __name__=="__main__":unittest.main()
