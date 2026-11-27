import unittest,time
from examples import three_loop_vp05_boundary202203_exact as m
class ExactTests(unittest.TestCase):
    def test_expand(self):
        f,z,d=m.sp.polys.fields.field("z,d",m.sp.QQ)
        recipes={0:(f.one,{}),1:(1/z,{0:d})}
        self.assertEqual(m.expand({1:z},recipes,f,time.monotonic()+10),{1:f.one,0:-d})
    def test_collapse(self):
        f,z,d=m.sp.polys.fields.field("z,d",m.sp.QQ)
        self.assertEqual(m.collapse({(1,):z,(2,):d},lambda k:k,{(1,):{(2,):-d/z}},f),{})
if __name__=="__main__":unittest.main()
