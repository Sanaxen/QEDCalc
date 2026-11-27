import unittest
from examples import three_loop_vp05_abc_banana as m

class BananaTests(unittest.TestCase):
    def test_geometry_and_average(self):
        props=m.old.build_family_spec("VP05_full").propagators
        center,original,lines,maps=m.geometry(props)
        self.assertEqual(len(maps),24)
        self.assertEqual(m.average(m.product(lines[0],m.old.MOM[4]),lines),m.old.Z/4)
        self.assertEqual(m.average(m.sp.S.One,lines),1)
    def test_covariance(self):
        x=m.old.dot(0,3)
        self.assertEqual(m.covariance(2*x),-m.old.dot(0,4))
        with self.assertRaises(RuntimeError):
            m.covariance(x*x)
    def test_python_integer_and_empty_product(self):
        props=m.old.build_family_spec("VP05_full").propagators
        center,original,lines,_=m.geometry(props)
        self.assertEqual(m.transform(1,center),m.sp.S.One)
        self.assertEqual(m.transform(0,center),m.sp.S.Zero)
        raw=m.sp.prod([])  # may return a native int depending on SymPy version
        projected=m.covariance(m.transform(raw,center))
        averaged=m.average(projected,lines)
        self.assertEqual(averaged,m.sp.S.One)
        row,_=m.expand_integral(averaged,original,props,m.s.inverse_polys(props))
        self.assertEqual(row,{m.BASE:m.sp.S.One})
    def test_scalar_roundtrip(self):
        props=m.old.build_family_spec("VP05_full").propagators
        _,original,_,_=m.geometry(props)
        row,_=m.expand_integral(m.sp.S.One,original,props,m.s.inverse_polys(props))
        self.assertEqual(row,{m.BASE:m.sp.S.One})

if __name__=="__main__":unittest.main()
