import unittest,itertools
from examples import three_loop_vp05_native_boundary_shell as m
class ScopeTests(unittest.TestCase):
    def test_metadata(self):
        for sec in m.SECTORS:
            for s in (5,6):
                for point in (0,1):
                    self.assertEqual(m.meta(sec,s,point,"empty"),{**m.b.meta(sec,s,point),"native_batch":7,"source_sha256":"empty"})
    def test_shell_size(self):
        self.assertEqual(m.b.c.expected(5),193050)
        self.assertEqual(m.b.c.expected(6),450450)
    def test_rows(self):
        for sec in m.SECTORS:
            for s in (5,6):
                rows=list(itertools.islice(m.b.c.rows(sec,s),15))
                self.assertEqual(len(rows),15)
                self.assertEqual(len({a for a,i,j in rows}),1)
                self.assertEqual(len({(i,j) for a,i,j in rows}),15)
                self.assertTrue(all(sum(max(-x,0) for x in a)==s for a,i,j in rows))
if __name__=="__main__":unittest.main()
