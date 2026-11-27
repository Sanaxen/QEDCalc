import unittest
from examples import three_loop_vp05_203_exact_lift as m

class LiftTests(unittest.TestCase):
    def test_add(self):
        f,z,d=m.sp.polys.fields.field("z,d",m.sp.QQ)
        r={1:z,2:d}
        m.add(r,{1:z,3:d},-f.one)
        self.assertEqual(r,{2:d,3:-d})
    def test_lift(self):
        import time
        from unittest.mock import patch
        f,z,d=m.sp.polys.fields.field("z,d",m.sp.QQ)
        witness=[{"row_index":i+1000} for i in range(528)]
        groups=[{"rows":[i],"representative":i,"ratios_to_representative":[{"row":i,"ratio":"1"}]} for i in range(527)]
        groups.append({"rows":[527],"representative":527,"ratios_to_representative":[{"row":527,"ratio":"1"}]})
        groups[0]["rows"].append(1)
        groups[0]["ratios_to_representative"].append({"row":1,"ratio":"1/2"})
        del groups[1]
        packed=[{"original_rows":g["rows"]} for g in groups]
        with patch.object(m.old,"memory_guard"):
            r=m.lift(groups,packed,{i:z for i in range(len(groups))},witness,{},f,time.monotonic()+60)
        self.assertEqual(len(r),528)
        self.assertEqual(r[1001],z/2)
if __name__=="__main__":unittest.main()
