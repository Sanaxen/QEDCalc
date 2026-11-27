import unittest,time
from examples import three_loop_vp05_abc_correct_exact as m

class ExactTests(unittest.TestCase):
    def test_reduce_and_replay(self):
        f,z,d=m.sp.polys.fields.field("z,d",m.sp.QQ)
        a,b,c=(100,202),(200,202),(1,202)
        rows={0:{b:f.one,a:-z},1:{a:f.one,c:-d}}
        pivots={b:(rows[0],0),a:(rows[1],1)}
        cur,trace=m.reduce({b:f.one},pivots,{c},time.monotonic()+10,100)
        self.assertEqual(cur,{c:z*d})
        self.assertEqual(m.replay(trace,rows),{b:f.one,c:-z*d})
if __name__=="__main__":unittest.main()
