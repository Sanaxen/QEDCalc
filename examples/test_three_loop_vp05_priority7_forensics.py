import gzip,tempfile,time,unittest
from pathlib import Path
from examples import three_loop_vp05_priority7_forensics as m
class ScanTests(unittest.TestCase):
    def test_complete(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"system.gz"
            p.write_bytes(gzip.compress(b"Eq\n123\n2\n0 z 12345 204\n0 -d 12346 204\n"))
            r=m.scan(p,time.monotonic()+10)
            self.assertTrue(r["complete_stream"])
            self.assertEqual((r["rows"],r["terms"]),(1,2))
    def test_truncated(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"system.gz"
            p.write_bytes(gzip.compress(b"Eq\n123\n1\n0 z 12345 204\n")[:-5])
            self.assertFalse(m.scan(p,time.monotonic()+10)["complete_stream"])
    def test_bad_row(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"system.gz"
            p.write_bytes(gzip.compress(b"Eq\n123\n2\n0 z 12345 204\n"))
            self.assertFalse(m.scan(p,time.monotonic()+10)["complete_stream"])
if __name__=="__main__":unittest.main()
