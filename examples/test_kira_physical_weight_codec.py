import unittest
from examples.kira_physical_weight_codec import PhysicalWeightCodec,read_permutation,sector

class FakeCodec:
    def __init__(self,**kw):
        self.options=kw
    def encode(self,x):
        return tuple(x)
    def decode(self,x):
        return x

class FakeModule:
    WeightCodec=FakeCodec

class CodecTests(unittest.TestCase):
    def setUp(self):
        self.codec=PhysicalWeightCodec(FakeModule,np=3,bits=(1,2,3,4),iord=5,topsectors=[3],permutation=(2,0,1))
    def test_permutation(self):
        self.assertEqual(self.codec.internal_tops,[6])
        self.assertEqual(self.codec.encode((2,1,-1)),(-1,2,1))
        self.assertEqual(self.codec.decode_default((-1,2,1)),(2,1,-1))
    def test_sector_guard(self):
        key=((-1,2,1),3)
        self.assertEqual(self.codec.decode_key(key,custom_keys=set()),(2,1,-1))
        with self.assertRaises(ValueError):
            self.codec.decode_key((key[0],5),custom_keys=set())
        with self.assertRaises(ValueError):
            self.codec.decode_key(key,custom_keys={key})
    def test_metadata(self):
        text='auxiliary:\n - name: "Other"\n   permutation: [0,1,2]\n - name: "VP05_full"\n   permutation: [2,0,1]\n'
        self.assertEqual(read_permutation(text,"VP05_full",3),(2,0,1))
        with self.assertRaises(ValueError):
            read_permutation(text,"missing",3)
    def test_sector(self):
        self.assertEqual(sector((1,-1,0,2)),9)

if __name__=="__main__":unittest.main()
