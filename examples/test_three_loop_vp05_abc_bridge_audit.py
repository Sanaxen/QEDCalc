import unittest
from examples import three_loop_vp05_abc_bridge_audit as m

class BridgeAuditTests(unittest.TestCase):
    def test_bridge(self):
        keys,ratio=m.two_term([["2","-1","48378511622144","131","0","0"],["2","1","4","73","0","0"]])
        self.assertEqual(keys,[(48378511622144,131),(4,73)])
        self.assertEqual(ratio,1)
    def test_weighted_bridge(self):
        _,ratio=m.two_term([["2","2","10","131","0","0"],["2","-z","4","73","0","0"]])
        self.assertEqual(ratio,m.old.Z/2)
    def test_not_bridge(self):
        self.assertIsNone(m.two_term([["1","1","4","73","0","0"]]))

if __name__=="__main__":unittest.main()
