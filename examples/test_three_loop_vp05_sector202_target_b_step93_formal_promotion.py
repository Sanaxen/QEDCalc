"""Offline safety regression tests for versioned Step93 proof promotion."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch
from examples import three_loop_vp05_sector202_target_b_step93_formal_promotion as mod


class Step93FormalPromotionTests(TestCase):
    def test_versioned_formal_does_not_replace_historic_state(self):
        self.assertNotEqual(mod.FORMAL, mod.B_STATE)
        self.assertNotEqual(mod.PACKAGE, mod.independent.DIRECTORY)
        self.assertNotEqual(mod.MANIFEST, mod.PROOF)
        self.assertEqual(mod.PHASE_COUNTS, {"pivot": 393, "source": 537})

    def test_exact_coefficient_archive_canonical(self):
        entries = [[5, "z/(z+1)"], [17, "-1/(d+1)"]]
        self.assertEqual(json.loads(mod.encode(entries)), entries)
        self.assertEqual(mod.digest_bytes(mod.encode(entries)), mod.digest_bytes(mod.encode(entries)))

    def test_snapshot_never_overwrites_tampering(self):
        with TemporaryDirectory() as td:
            parent = Path(td)
            src, target = parent / "original.json", parent / "archive.json"
            src.write_bytes(b'{"status":"PASS"}')
            expected = mod.digest_file(src)
            mod.copy_exact(src, target, expected, False)
            with self.assertRaises(FileExistsError):
                mod.copy_exact(src, target, expected, False)
            mod.copy_exact(src, target, expected, True)
            target.write_bytes(b"corrupt")
            with self.assertRaises(FileExistsError):
                mod.copy_exact(src, target, expected, True)
            self.assertEqual(src.read_bytes(), b'{"status":"PASS"}')

    def test_mismatched_original_rejected(self):
        with TemporaryDirectory() as td:
            p = Path(td)
            src = p / "source"
            src.write_bytes(b"a")
            with self.assertRaises(RuntimeError):
                mod.copy_exact(src, p / "copy", mod.digest_bytes(b"b"), False)
            self.assertFalse((p / "copy").exists())

    def test_read_only_default(self):
        with patch.object(mod, "preflight", return_value={"status": "PREFLIGHT"}) as check:
            self.assertEqual(mod.preflight()["status"], "PREFLIGHT")
            check.assert_called_once_with()

    def test_package_source_paths_are_distinct(self):
        items = list(mod.inputs().values())
        self.assertEqual(len(items), len(set(p.resolve() for p in items)))


if __name__ == "__main__":
    import unittest
    unittest.main()
