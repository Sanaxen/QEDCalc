import time
import unittest
from examples import three_loop_vp05_abc_cost_probe as m

class CostProbeTests(unittest.TestCase):
    def test_retain(self):
        a,b,c=(100,202),(200,202),(1,202)
        rows=[[(b,"1"),(a,"-2")],[(a,"1"),(c,"-3")]]
        r=m.probe(rows,(1000003,17,7),[a,b],{c},time.monotonic()+60,100)
        self.assertEqual(r["pivot_count"],2)
        self.assertTrue(all(t["retained_only"] for t in r["targets"]))
        self.assertEqual(r["targets"][1]["source_support"],2)
        self.assertEqual(r["targets"][1]["remainder"],[[list(c),6]])
    def test_unresolved(self):
        a,b=(100,202),(200,202)
        r=m.probe([], (1000003,17,7),[a],{b},time.monotonic()+60,100)
        self.assertFalse(r["targets"][0]["retained_only"])

if __name__=="__main__":unittest.main()
