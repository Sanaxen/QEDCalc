import unittest,time
from unittest.mock import patch
from examples import three_loop_vp05_correct_rank as m

class RankTests(unittest.TestCase):
    def test_independent(self):
        a,c,t=(100,202),(3,202),(4,73)
        with patch.object(m.old,"memory_guard"):
            r=m.ranks([[(a,"1"),(t,"-1")]],(1000003,17,7),c,t,100,time.monotonic()+10)
        self.assertEqual((r["rank_E"],r["rank_E_M"],r["rank_E_M_C"]),(1,2,3))
        self.assertTrue(r["full_row_rank"])
    def test_dependent(self):
        c,t=(3,202),(4,73)
        with patch.object(m.old,"memory_guard"):
            r=m.ranks([[(c,"1"),(t,"-1")]],(1000003,17,7),c,t,100,time.monotonic()+10)
        self.assertEqual((r["rank_E"],r["rank_E_M"],r["rank_E_M_C"]),(1,2,2))
        self.assertFalse(r["C_independent_mod_M_at_point"])
if __name__=="__main__":unittest.main()
