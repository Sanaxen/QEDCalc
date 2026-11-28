import hashlib,json,tempfile,unittest
from pathlib import Path
from examples import three_loop_vp05_native_packed_continue as m
class Tests(unittest.TestCase):
    def test_header(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"test.bin"
            data=b"VP05PACK4\n"+json.dumps(dict(meta={},cursor=0,rank=0,terms=0,keys=0)).encode()+b"\n"
            p.write_bytes(data)
            obj,sha=m.header(p,False)
            self.assertEqual(sha,hashlib.sha256(data).digest())
            p.write_bytes(data+sha)
            self.assertEqual(m.header(p)[0],obj)
            p.write_bytes(data+b"x"*32)
            with self.assertRaisesRegex(RuntimeError,"checksum"):m.header(p)
    def test_observed(self):
        self.assertEqual(sum(x[0] for x in m.OBS.values()),305000)
        self.assertEqual(m.CAP,120000000)
if __name__=="__main__":unittest.main()
