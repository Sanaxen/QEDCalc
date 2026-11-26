import struct
import tempfile
import unittest
from pathlib import Path
from examples import three_loop_vp05_native_batch as m

class NativeBatchTests(unittest.TestCase):
    def test_second_prime_import(self):
        p=1000033
        a=m.b.c.key((1,1,1,0,0,0,0,0,0,0,0,0))
        k=m.b.c.key((2,1,1,0,0,0,0,0,0,0,0,0))
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"out"
            with path.open("wb") as f:
                f.write(struct.pack("<II",m.n.MAGIC,2))
                m.n.write_row(f,[(a,p-1),(k,1)])
                f.write(struct.pack("<IQ",1,2))
                m.n.write_row(f,[])
                f.write(struct.pack("<IQ",1,2))
                f.write(struct.pack("<QQQ",100,0,0))
            store=m.b.Packed()
            rows=[(0,{}),(1,{})]
            pending,*_=m.read_result(path,store,rows,p)
            self.assertEqual(pending,[(0,k,{a:p-1,k:1})])
            self.assertEqual(store.terms,0)
            with self.assertRaises(RuntimeError):m.read_result(path,store,rows,1000003)
            path.write_bytes(path.read_bytes()[:-1])
            with self.assertRaises(RuntimeError):m.read_result(path,store,rows,p)
    def test_scope(self):
        self.assertEqual(m.JOBS,((196,1),(200,0),(200,1)))
        self.assertIsNone(m.source_for(196,1))
        self.assertIsNone(m.source_for(200,1))
        self.assertIsNotNone(m.source_for(200,0))

if __name__=="__main__":unittest.main()
