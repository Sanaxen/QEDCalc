import unittest
import sympy as sp
from sympy.polys.fields import field
from examples import three_loop_vp05_sector202_exact_support_checkpoint as eng
from examples import three_loop_vp05_exact_arithmetic_probe as ar

class FieldPilotTests(unittest.TestCase):
    def test_persistent_pair_matches_two_exact_updates(self):
        z,d=sp.symbols("z d")
        f,_,_=field("z,d",sp.QQ)
        row={0:z+1,1:d,2:sp.S.One}
        trace={10:sp.S.One}
        state=None
        for lead,brow,btrace in [
            (0,{0:sp.S.One,1:z},{20:1/(d+1)}),
            (1,{1:sp.S.One,2:z/d},{30:1/(z+1)})]:
            factor=row[lead]
            expected=ar.sympy_sparse_subtract(row,brow,factor)
            expected_trace=ar.sympy_sparse_subtract(trace,btrace,factor)
            row,trace,state=eng.field_subtract_pair(row,trace,brow,btrace,lead,state,f)
            self.assertTrue(ar.exact_same(row,expected))
            self.assertTrue(ar.exact_same(trace,expected_trace))
            self.assertNotIn(lead,row)
