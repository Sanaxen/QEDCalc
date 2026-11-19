"""Offline safety and exact-field tests for independent Step93 Target B proof."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from examples import three_loop_vp05_sector202_target_b_step93_independent_proof as m

class IndependentStep93Tests(unittest.TestCase):
    def test_exact_qq_identity(self):
        self.assertTrue(m.equal("1",[("z","1/(z+1)"),("1","1/(z+1)")]))
        self.assertFalse(m.equal("2",[("z","1/(z+1)"),("1","1/(z+1)")]))
    def test_provenance_row_codec(self):
        x=m.rows([[[1,139],"z+1"],[[2,139],"z"]],True)
        self.assertEqual(x[(1,139)],"z+1")
        with self.assertRaises(RuntimeError):
            m.rows([[[1,139],"1"],[[1,139],"2"]],True)
        self.assertEqual(m.rows([[10,"z"]],False),{10:"z"})
    def test_atomic_checkpoint(self):
        with TemporaryDirectory() as root:
            p=Path(root)/"checkpoint.json"
            m.atomic(p,{"verified":0},exclusive=True)
            with self.assertRaises(FileExistsError):
                m.atomic(p,{"verified":1},exclusive=True)
            m.atomic(p,{"verified":1})
            self.assertEqual(m.load(p)["verified"],1)
    def test_sources_are_read_only_outputs_separate(self):
        self.assertNotEqual(m.OUTPUT,m.DIRECTORY)
        self.assertNotEqual(m.PROOF,m.B_STATE)
        self.assertNotEqual(m.WORK,m.B_STATE)
        self.assertNotEqual(m.checkpoint_path("pivot"),m.checkpoint_path("source"))
    def test_static_phase_configuration(self):
        self.assertEqual(m.PHASES,("pivot","source"))
        self.assertEqual(m.STATUS,"INDEPENDENT_STEP93_EXACT_PREFIX_NOT_TARGET_PROOF")
        self.assertEqual(m.TAG,"VP05_B_STEP93_INDEPENDENT ")

if __name__=="__main__":unittest.main()
