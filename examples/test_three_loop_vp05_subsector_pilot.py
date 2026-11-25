import unittest
from examples.three_loop_vp05_subsector_pilot import truncate_setting, SECTORS

class PilotTests(unittest.TestCase):
    def test_setting(self):
        self.assertEqual(truncate_setting("jobs:\n      truncate_sp: 2\n"),"      truncate_sp: 2")
    def test_refuse_unverified(self):
        for raw in ("", "truncate_sp: [2]", "truncate_sp: 1", "truncate_sp: 2\ntruncate_sp: 2"):
            with self.assertRaises(RuntimeError):
                truncate_setting(raw)
    def test_scope(self):
        self.assertTrue(all(s.bit_count()==3 for s in SECTORS))
