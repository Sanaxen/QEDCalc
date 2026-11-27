import unittest
from examples import three_loop_vp05_abc_boundary_scope as m

class ABCTests(unittest.TestCase):
    def test_opaque_elimination(self):
        f,z,d=m.sp.polys.fields.field("z,d",m.sp.QQ)
        A,B,C=(100,139),(200,139),(300,139)
        M=m.OPAQUE
        row,trace,scales=m.eliminate({A:f.one,C:-z,M:-d},{B:f.one,C:-d,M:-z},{1:f.one},{2:f.one},[A,B,C],f)
        self.assertEqual(row,{A:z,B:-d,C:d*d-z*z})
        self.assertEqual(trace,{1:z,2:-d})
        self.assertNotIn(M,row)
    def test_unexpected_support_rejected(self):
        f,z,d=m.sp.polys.fields.field("z,d",m.sp.QQ)
        with self.assertRaisesRegex(RuntimeError,"support"):
            m.eliminate({}, {}, {}, {}, [(100,139),(200,139),(300,139)], f)
    def test_boundary_scope(self):
        rows=[{"local_evidence_present":False,"sector":203,"seed":"r8s6d2","candidate_count":4},
              {"local_evidence_present":True,"sector":202,"seed":"r9s5d2","candidate_count":3}]
        out=m.scope_rows(rows)
        self.assertEqual(len(out),1)
        self.assertTrue(out[0]["contains_202"])
        self.assertTrue(out[0]["contains_203"])
        self.assertFalse(out[0]["boundary_closed"])

if __name__=="__main__":unittest.main()
