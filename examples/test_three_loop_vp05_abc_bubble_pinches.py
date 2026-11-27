import unittest
from examples import three_loop_vp05_abc_bubble_pinches as m

class BubblePinchTests(unittest.TestCase):
    def test_substitute(self):
        k=("UJ",1,0); t=("T",0,0); j=("JJ",1,1)
        self.assertEqual(m.substitute({k:2,t:3,j:1},{k:m.sp.S(4)}),{t:11,j:1})
    def test_missing_rule(self):
        with self.assertRaises(KeyError):
            m.substitute({("UJ",1,0):1},{})
    def test_roundtrip(self):
        row={("JJ",2,0):m.a.d+m.a.z}
        self.assertEqual(m.decode(m.a.encode(row)),row)

if __name__=="__main__":unittest.main()
