import unittest
from math import comb
from examples import three_loop_vp05_boundary202203 as m
class EnvelopeTests(unittest.TestCase):
    def test_counts(self):
        for sec in (202,203):
            p=sec.bit_count();n=12-p
            for s,d in ((6,2),(5,3)):
                targets=list(m.envelope(sec,8,s,d))
                self.assertEqual(len(set(targets)),len(targets))
                self.assertEqual(len(targets),comb(p+min(d,8-p),p)*comb(n+s,n))
                for ex in targets:
                    self.assertEqual(m.sector(ex),sec)
                    self.assertLessEqual(sum(max(0,x) for x in ex),8)
                    self.assertLessEqual(sum(max(0,-x) for x in ex),s)
if __name__=="__main__":unittest.main()
