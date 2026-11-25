import unittest
from examples.three_loop_vp05_remaining_safe_batch import eligible, EXPECTED

class SafeScopeTests(unittest.TestCase):
    def test_exact_scope(self):
        self.assertEqual(EXPECTED,{"r8s5d3":(78,101,116),"r8s6d2":(204,205,228,229,230,231,237)})
        self.assertEqual(sum(map(len,EXPECTED.values())),10)
        for seed,sectors in EXPECTED.items():
            for sector in sectors:
                self.assertTrue(eligible(seed,sector))
                self.assertNotEqual(sector&202,202)
    def test_blocked_and_completed(self):
        for seed in EXPECTED:
            for sector in (202,203,206,207,234,238,239,73):
                self.assertFalse(eligible(seed,sector))
        self.assertFalse(eligible("r9s5d2",78))
