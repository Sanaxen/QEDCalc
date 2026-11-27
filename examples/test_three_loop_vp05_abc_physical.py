import unittest
import time
from unittest.mock import patch
from examples import three_loop_vp05_abc_physical as m

class PhysicalTests(unittest.TestCase):
    def test_relation_trace(self):
        A,B,C=m.gap.TARGETS
        with patch.object(m.f.e.b.a,"memory"):
            eng=m.exact.Trace(1000003,set(),time.monotonic()+60)
            eng.insert_source({A:2,B:3,C:5},0)
            rem,deps=m.trace_row(eng,{A:4,B:6,C:10})
            self.assertEqual(rem,{})
            self.assertEqual(len(deps),1)
            rem,_=m.trace_row(eng,{A:4,B:6,C:11})
            self.assertTrue(rem)
    def test_seed_scope(self):
        self.assertTrue(all(m.seed_ok(k) for k in m.gap.TARGETS))
        self.assertFalse(m.seed_ok((1,)*12))
        self.assertFalse(m.seed_ok((0,)*12))
    def test_exact_relation_dag(self):
        A,B,C=m.gap.TARGETS
        row={A:m.sp.Integer(2),B:m.sp.Integer(3),C:m.sp.Integer(5)}
        target={k:2*x for k,x in row.items()}
        ij=(0,0)
        ref={"seed":list(A),"derivative":list(ij),"row":m.p.encode(row)}
        deadline=time.monotonic()+60
        with patch.object(m.f.e.b.a,"memory"),patch.object(m.q,"exact_row",return_value=row):
            eng=m.retry.make_trace([row],set(),m.POINTS[0],deadline)
            free,direct=m.trace_row(eng,m.p.field_row(target,m.POINTS[0]))
            self.assertFalse(free)
            cert=m.make_proof([row],[ref],target,eng,m.POINTS[0],direct,deadline)
            self.assertEqual(m.verify(cert,target,{ij:[]},deadline),1)
            cert["target_dependencies"][0][1]="0"
            with self.assertRaises(RuntimeError):
                m.verify(cert,target,{ij:[]},deadline)

if __name__=="__main__":unittest.main()
