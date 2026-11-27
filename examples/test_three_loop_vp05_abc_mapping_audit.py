import unittest
import gzip
import tempfile
from pathlib import Path
from examples import three_loop_vp05_abc_mapping_audit as m

class MappingAuditTests(unittest.TestCase):
    def test_proportional(self):
        field,z,d=m.sp.polys.fields.field("z,d",m.sp.QQ)
        a={(1,):z,(2,):d}
        self.assertEqual(m.proportional({k:2*v for k,v in a.items()},a),field(2))
        self.assertIsNone(m.proportional({(1,):z,(2,):z},a))
        self.assertIsNone(m.proportional({(1,):z},a))
    def test_parse_system(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"test.gz"
            with gzip.open(path,"wt",encoding="utf-8") as fh:
                fh.write("Eq\n123\n2\n0 z 10 20\n0 -1 11 21\n")
            self.assertEqual(list(m.parse_system(path)),[(1,"123",[["0","z","10","20"],["0","-1","11","21"]])])
    def test_direct_match(self):
        props=m.old.build_family_spec("VP05_full").propagators
        kernel=m.old.build_kernel(props)
        field,z,d=m.sp.polys.fields.field("z,d",m.sp.QQ)
        import time
        seed=m.gap.TARGETS[2]
        for ij in sorted(kernel):
            raw=m.ph.q.exact_row(seed,kernel[ij],*ij)
            if raw:
                row={k:field.from_expr(m.sp.sympify(c)) for k,c in raw.items() if c}
                matches=m.match(row,kernel,field,time.monotonic()+60)
                self.assertTrue(any(tuple(x["seed"])==seed and tuple(x["derivative"])==ij for x in matches))
                return
        self.fail("No nonzero physical row")

if __name__=="__main__":unittest.main()
