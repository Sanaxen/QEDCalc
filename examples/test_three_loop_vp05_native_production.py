import tempfile
import unittest
import struct
from pathlib import Path
from examples import three_loop_vp05_native_production as p

class NativeImportTests(unittest.TestCase):
    def test_valid_and_corrupt(self):
        b=p.b;n=p.n
        k=b.c.key((1,1,1,0,0,0,0,0,0,0,0,0))
        rows=[(0,{}),(1,{})]
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"result"
            with path.open("wb") as f:
                f.write(struct.pack("<II",n.MAGIC,2))
                n.write_row(f,[(k,1)])
                f.write(struct.pack("<IQ",1,1))
                n.write_row(f,[])
                f.write(struct.pack("<IQ",1,1))
                f.write(struct.pack("<QQQ",123,100,0))
            store=b.Packed()
            pending,trace,*_=p.import_result(path,store,rows)
            self.assertEqual(pending,[(0,k,{k:1})])
            self.assertEqual(trace,[(1,1),(1,1)])
            self.assertEqual(store.terms,0)
            data=path.read_bytes()
            path.write_bytes(data[:-1])
            with self.assertRaises(RuntimeError):p.import_result(path,store,rows)
            path.write_bytes(data+b"x")
            with self.assertRaises(RuntimeError):p.import_result(path,store,rows)

if __name__=="__main__":unittest.main()
