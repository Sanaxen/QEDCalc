import unittest
from examples import three_loop_vp05_factorized as m

class FactorizedTests(unittest.TestCase):
    def test_radial(self):
        self.assertEqual(m.radial(1,0),1)
        self.assertEqual(m.radial(1,1),1)
        self.assertEqual(m.sp.cancel(m.radial(2,0)-(m.D/2-1)),0)
        self.assertEqual(m.sp.cancel(m.radial(2,1)-m.D/2),0)
    def test_pairing_counts(self):
        self.assertEqual(len(list(m.pairings(tuple(range(6))))),15)
    def test_actual_family(self):
        spec=m.old.build_family_spec("VP05_full")
        r=m.Reducer(spec.propagators,196,float("inf"))
        self.assertEqual(r.reduce(m.scalar(196)),1)
        self.assertEqual(m.sp.cancel(r.reduce(m.a.BLOCK)-(m.D-2)),0)
        mon=tuple(2 if pair==(0,1) else 0 for pair in m.PAIRS)
        self.assertEqual(m.sp.cancel(r.moment(mon,(1,1,1))-1/m.D),0)
        mon=tuple(4 if pair==(0,1) else 0 for pair in m.PAIRS)
        self.assertEqual(m.sp.cancel(r.moment(mon,(1,1,1))-3/(m.D*(m.D+2))),0)
        r.close()

if __name__=="__main__":unittest.main()
