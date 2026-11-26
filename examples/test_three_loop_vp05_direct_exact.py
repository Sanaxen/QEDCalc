import unittest
from examples import three_loop_vp05_direct_exact as m

class ExactTests(unittest.TestCase):
    def test_rational_axpy(self):
        F,z,d=m.sp.polys.fields.field("z,d",m.sp.QQ)
        row={1:F.one,2:z/d}
        m.axpy(row,{1:F.one,2:z/d},-F.one)
        self.assertEqual(row,{})
    def test_field_specialization(self):
        engine=m.Exact(196,0,{},[],float("inf"))
        c=engine.F.from_expr((m.old.D-2)/2)
        self.assertEqual(engine.mod(c),500004)
    def test_trivial_certificate(self):
        engine=m.Exact(196,0,{},[],float("inf"))
        ex=[0,0,1,0,0,0,1,1,0,0,0,0]
        result={"target":ex,"trace":[],"remainder":[[ex,1]]}
        other={"field":[1000033,19,11],"remainder":[[ex,1]]}
        proof=engine.prove(result,other)
        self.assertEqual(proof["multipliers"],[])
        payload={"source_sha256":m.SHA,"kernel_sha256":m.b.c.PIN,**proof}
        engine.verify_saved(payload,result,other)
        payload["remainder"][0][1]="2"
        with self.assertRaises(RuntimeError):engine.verify_saved(payload,result,other)

if __name__=="__main__":unittest.main()
