import unittest
from examples import three_loop_vp05_abc_custom_ids as m

class CustomIdTests(unittest.TestCase):
    def test_alias(self):
        terms=[["2","-2","10000","202","0","0"],["2","1","1","202","0","0"]]
        self.assertEqual(m.alias(terms,{(1,202)}),((1,202),(10000,202),2))
        self.assertEqual(m.alias(list(reversed(terms)),{(1,202)}),((1,202),(10000,202),2))
    def test_no_alias(self):
        terms=[["2","-1","10000","202","0","0"],["2","1","1","202","0","0"]]
        self.assertIsNone(m.alias(terms,set()))
        self.assertIsNone(m.alias(terms,{(1,202),(10000,202)}))
        self.assertIsNone(m.alias(terms[:1],{(1,202)}))

if __name__=="__main__":unittest.main()
