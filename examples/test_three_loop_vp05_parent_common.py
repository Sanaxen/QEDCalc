import unittest
from examples import three_loop_vp05_parent_common as m

class CommonTests(unittest.TestCase):
    def test_extended_rules(self):
        x=m.f.scalar(76);y=m.f.scalar(140);c=m.f.a.CAND
        z=list(x);z[2]=0;z=tuple(z)
        blocked=list(y);blocked[0]=-7;blocked=tuple(blocked)
        row,used,b=m.substitute({x:2,y:3,z:4,blocked:5,c:-5},lambda k:m.sp.S.One)
        self.assertEqual(row,{blocked:5})
        self.assertEqual(used,{x:1,y:1,z:0})
        self.assertEqual(b,{blocked:(7,0)})
    def test_extension_seeds(self):
        for sec in m.NEW:
            seeds=m.extension_seeds(sec)
            self.assertEqual(len(seeds),13)
            self.assertTrue(all(m.gap.sector(x)==sec for x in seeds))
    def test_new_scalar_and_dot(self):
        props=m.old.build_family_spec("VP05_full").propagators
        for sec in m.NEW:
            reducer=m.f.Reducer(props,sec,float("inf"))
            x=m.f.scalar(sec)
            self.assertEqual(reducer.reduce(x),1)
            y=list(x);y[reducer.lines[0]]+=1
            self.assertEqual(m.sp.cancel(reducer.reduce(tuple(y))-(m.f.D/2-1)),0)
            reducer.close()

if __name__=="__main__":unittest.main()
