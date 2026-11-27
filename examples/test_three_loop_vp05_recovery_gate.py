import unittest
from examples import three_loop_vp05_recovery_gate as m

class BasisTests(unittest.TestCase):
    def test_exchange(self):
        f,z,d=m.sp.polys.fields.field("z,d",m.sp.QQ)
        a,b,c,u,v=(1,),(2,),(3,),(4,),(5,)
        det,r=m.basis_exchange({a,b,c},[a,b],[{u:z,v:-z,c:d},{u:f.one,v:f.one}],f)
        self.assertEqual(det,2*z)
        self.assertEqual(r[u],{a:1/(2*z),b:f.one/2,c:-d/(2*z)})
        self.assertEqual(r[v],{a:-1/(2*z),b:f.one/2,c:d/(2*z)})
    def test_singular(self):
        f,z,d=m.sp.polys.fields.field("z,d",m.sp.QQ)
        a,b,u,v=(1,),(2,),(3,),(4,)
        with self.assertRaises(RuntimeError):
            m.basis_exchange({a,b},[a,b],[{u:z,v:z},{u:f.one,v:f.one}],f)
if __name__=="__main__":unittest.main()
