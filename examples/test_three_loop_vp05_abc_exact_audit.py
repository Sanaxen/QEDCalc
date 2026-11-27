import unittest
from examples import three_loop_vp05_abc_exact_audit as m

class PreferredTests(unittest.TestCase):
    def test_order(self):
        a="VP05_full[0,1,0,1,0,0,1,1,0,0,0,0]"
        b="VP05_full[1,0,0,1,0,0,1,0,0,0,0,0]"
        self.assertEqual(m.preferred(a+"\n"+b),{(1,202):(0,1,0,1,0,0,1,1,0,0,0,0),(2,73):(1,0,0,1,0,0,1,0,0,0,0,0)})
        with self.assertRaises(ValueError):m.preferred(a+"\n"+a)
if __name__=="__main__":unittest.main()
