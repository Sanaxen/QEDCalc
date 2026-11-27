import unittest
from examples import three_loop_vp05_abc_permutation_audit as m

class PermutationTests(unittest.TestCase):
    def test_inverse(self):
        perm=(2,0,1)
        x=(3,4,-2)
        self.assertEqual(m.to_physical(m.to_internal(x,perm),perm),x)
        self.assertEqual(m.mask_to_internal(3,perm),6)
    def test_auxiliary(self):
        self.assertEqual(m.read_permutation('auxiliary:\n - name: "VP05_full"\n   permutation: [2,0,1]\n',3),(2,0,1))
    def test_invalid(self):
        with self.assertRaises(ValueError):
            m.validate_perm([0,0,1],3)

if __name__=="__main__":unittest.main()
