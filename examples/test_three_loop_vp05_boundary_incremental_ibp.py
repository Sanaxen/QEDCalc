import unittest
from examples import three_loop_vp05_boundary_incremental_ibp as m
class ScheduleTests(unittest.TestCase):
    def test_scope(self):
        for sec,s,d in m.JOBS:
            seq=m.schedule(sec,s,d,set(),{})
            self.assertEqual(len(seq),len(set(seq)))
            self.assertTrue(all(m.envelope.sector(k)==sec and m.degrees(k)[0]<=s and m.degrees(k)[1]<=d for k in seq))
    def test_priority(self):
        k=(0,1,0,1,0,0,1,1,0,0,0,0)
        self.assertEqual(m.schedule(202,6,2,{k},{})[0],k)
if __name__=="__main__":unittest.main()
