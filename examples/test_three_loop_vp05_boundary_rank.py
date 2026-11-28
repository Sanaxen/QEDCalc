import unittest,time
from examples import three_loop_vp05_boundary_rank as m
class RankTests(unittest.TestCase):
    def test_independent(self):
        x,y,c=(1,),(2,),(3,)
        rows=[{x:1,c:2},{y:1,c:3}]
        before=m.ranks(rows,{c},101,time.monotonic()+10)
        after=m.ranks([m.substitute(r,{x:{c:99}},101) for r in rows],{c},101,time.monotonic()+10)
        self.assertEqual((before["rank_E"],before["rank_N"],before["delta"]),(2,2,0))
        self.assertEqual((after["rank_E"],after["rank_N"],after["delta"]),(1,1,0))
    def test_dependent(self):
        x,c,d=(1,),(2,),(3,)
        r=m.ranks([{x:1,c:1},{x:1,d:1}],{c,d},101,time.monotonic()+10)
        self.assertEqual((r["rank_E"],r["rank_N"],r["delta"]),(2,1,1))
        self.assertEqual(len(r["candidate_relations"]),1)
if __name__=="__main__":unittest.main()
