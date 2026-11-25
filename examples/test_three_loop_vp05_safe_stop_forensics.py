import unittest
from examples.three_loop_vp05_safe_stop_forensics import group_stops

class GroupStopsTests(unittest.TestCase):
    def test_groups(self):
        rows=[{"state":"guard_stopped","sector":205,"detail":{"last_sector":["200","2","14"]}},
              {"state":"guard_stopped","sector":204,"detail":{"last_sector":["200","1","5"]}},
              {"state":"completed_local_retained","sector":78,"detail":{}}]
        self.assertEqual(group_stops(rows),{"200":[204,205]})
    def test_missing_progress(self):
        with self.assertRaises(RuntimeError):
            group_stops([{"state":"guard_stopped","sector":204,"detail":{}}])
