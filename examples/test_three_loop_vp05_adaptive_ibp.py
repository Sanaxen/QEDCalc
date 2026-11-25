import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from examples import three_loop_vp05_adaptive_ibp as a
from examples import three_loop_vp05_compact_ibp as c

class AdaptiveTests(unittest.TestCase):
    def test_cap(self):
        self.assertEqual(a.next_cap(a.BASE_CAP,9*a.GIB,a.BASE_CAP),a.BASE_CAP)
        self.assertEqual(a.next_cap(a.BASE_CAP,12*a.GIB,a.BASE_CAP),a.BASE_CAP+a.STEP)
        self.assertEqual(a.next_cap(a.MAX_CAP,20*a.GIB,a.MAX_CAP),a.MAX_CAP)
    def test_stream(self):
        m=a.meta(69,3,0)
        k=c.key((1,)*12)
        with tempfile.TemporaryDirectory() as d, patch.object(a,"memory",return_value=(32*a.GIB,20*a.GIB)), patch.object(a.shutil,"disk_usage") as disk:
            disk.return_value.free=10*a.GIB
            f=Path(d)/"state.stream"
            a.save(f,m,2,{k:{k:1}},[1],1,12,1,a.BASE_CAP)
            self.assertEqual(a.load(f,m,1000003),(2,{k:{k:1}},[1],1,12,1,a.BASE_CAP))
            with f.open("ab") as out:out.write(b"bad")
            with self.assertRaises(RuntimeError):a.load(f,m,1000003)
    def test_legacy_meta(self):
        m=a.old_meta(a.meta(196,3,0))
        self.assertEqual(m["cap"],1500000)
        self.assertEqual(m["version"],1)
