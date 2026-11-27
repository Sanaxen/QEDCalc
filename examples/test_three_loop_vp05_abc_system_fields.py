import unittest
from examples import three_loop_vp05_abc_system_fields as m

class SystemFieldsTests(unittest.TestCase):
    def test_inventory(self):
        rows=[[["2","z","4","73","0","1"],["3","d","4","73","1","0"]]]
        inv=m.inventory(rows)
        self.assertEqual(len(inv["fields"]),6)
        self.assertEqual(inv["fields"][0]["distinct"],2)
        self.assertEqual(inv["auxiliary_by_key"],[{"key":["4","73"],"auxiliary":[["2","0","1"],["3","1","0"]]}])
    def test_bad_fields(self):
        with self.assertRaises(RuntimeError):
            m.inventory([[["1","z","4","73"]]])

if __name__=="__main__":unittest.main()
