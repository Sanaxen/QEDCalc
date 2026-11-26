import unittest
from examples import three_loop_vp05_target_reuse_probe as m

class TargetProbeTests(unittest.TestCase):
    def test_cross_shell_substitution(self):
        b=m.b
        p=1000003
        keys=sorted(b.c.key(tuple([i]+[0]*11)) for i in (1,2,3))
        a,c,d=keys
        low=b.Packed();high=b.Packed()
        low.add(0,c,[(c,1),(a,2)])
        high.add(0,d,[(d,1),(c,3)])
        free,used,ops,state=m.substitute(d,[low,high],p)
        self.assertEqual(free,{a:6})
        self.assertEqual(used,{1:1,0:1})
        self.assertEqual(state,"nonzero")
        self.assertEqual(ops,4)
    def test_free_target_not_irreducibility_proof(self):
        free,used,ops,state=m.substitute(123,[],1000003)
        self.assertEqual((free,used,ops,state),({123:1},{},0,"nonzero"))
    def test_zero_and_cap(self):
        store=m.b.Packed()
        store.add(0,123,[(123,1)])
        self.assertEqual(m.substitute(123,[store],1000003)[3],"zero")
        store=m.b.Packed()
        store.add(0,123,[(123,1),(122,2)])
        self.assertEqual(m.substitute(123,[store],1000003,cap=0)[3],"cap")
    def test_manifest_scope(self):
        ex=[int(bool(69&(1<<i))) for i in range(12)]
        name="VP05_full["+",".join(map(str,ex))+"]"
        result=m.inventory({"candidate_masters":[name],"closure_targets":[name]},69)
        self.assertEqual(len(result),10)
        self.assertEqual(result[tuple(ex)],{"candidate_masters","closure_targets","scalar_dot_diagnostic"})

if __name__=="__main__":unittest.main()
