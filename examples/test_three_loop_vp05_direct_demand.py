import unittest
from examples import three_loop_vp05_direct_demand as m

class DirectDemandTests(unittest.TestCase):
    def test_two_shell_replay(self):
        p=1000003
        ex=[tuple([i]+[0]*11) for i in (1,2,3)]
        a,c,d=map(m.b.c.key,ex)
        low=m.b.Packed();high=m.b.Packed()
        low.add(0,c,[(c,1),(a,2)])
        high.add(0,d,[(d,1),(c,3)])
        result=m.reduce_target(ex[2],[low,high],p)
        self.assertEqual(result["remainder"],[[list(ex[0]),6]])
        m.replay(result,[low,high],p)
        result["trace"][0]["factor"]=2
        with self.assertRaises(RuntimeError):
            m.replay(result,[low,high],p)
    def test_no_pivot(self):
        ex=(1,)+(0,)*11
        result=m.reduce_target(ex,[],1000003)
        self.assertEqual(result["remainder"],[[list(ex),1]])
        self.assertEqual(result["trace"],[])
        m.replay(result,[],1000003)
    def test_zero(self):
        ex=(1,)+(0,)*11
        k=m.b.c.key(ex);store=m.b.Packed()
        store.add(0,k,[(k,1)])
        result=m.reduce_target(ex,[store],1000003)
        self.assertEqual(result["remainder"],[])
        m.replay(result,[store],1000003)

if __name__=="__main__":unittest.main()
