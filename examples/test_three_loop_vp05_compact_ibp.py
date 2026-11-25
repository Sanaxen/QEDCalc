import unittest
from examples.three_loop_vp05_compact_ibp import key,decode,reduce_row,expected
class CompactTests(unittest.TestCase):
    def test_key(self):
        a=(1,-6,0,3,0,1,0,-2,0,0,0,0)
        self.assertEqual(decode(key(a)),a)
        self.assertNotEqual(key(a),key(tuple(reversed(a))))
    def test_rank(self):
        a=(1,)*12;b=(2,)+(1,)*11
        k,v=reduce_row({a:2,b:3},{},101,0)
        self.assertEqual(k,key(b))
        self.assertEqual(reduce_row({a:4,b:6},{k:v},101,len(v)),(None,None))
    def test_count(self):
        self.assertEqual(expected(2),6750)
