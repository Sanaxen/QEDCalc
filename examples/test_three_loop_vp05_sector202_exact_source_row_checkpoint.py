"""Offline check of atomic per-row exact source checkpoint serializer."""
from __future__ import annotations
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest

from examples import three_loop_vp05_sector202_exact_support_checkpoint as m


class PerRowCheckpointTests(unittest.TestCase):
    def test_atomic_state_is_compatible_and_checkpointed_per_row(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "A_state.json"
            args = SimpleNamespace(checkpoint=target)
            config = {
                "source_sha256": "a" * 64,
                "certificate_sha256": "b" * 64,
                "target": "A",
                "ids_sha256": "c" * 64,
                "max_columns": 256,
                "max_source_support": 400,
                "max_expression_chars": 7500,
            }
            # Synthetic exact values still use the existing serializer schema.
            basis = {(1, 139): ({(1, 139): 1}, {100: 1})}
            m.save_exact_source_checkpoint(args, config, 1, [100, 101], 0, basis)
            state = json.loads(target.read_text())
            self.assertEqual(state["processed"], 1)
            self.assertEqual(state["total"], 2)
            self.assertEqual(state["status"], "EXACT_SOURCE_CHECKPOINT_NOT_TARGET_PROOF")
            self.assertFalse(state["exact_target_reduction_proven"])
            self.assertTrue(state["source_pivots_exact_replay_verified"])
            self.assertEqual(len(state["pivots"]), 1)
            self.assertFalse(target.with_name(target.name + ".tmp").exists())
            old = target.read_bytes()
            basis[(2, 139)] = ({(2, 139): 1}, {101: 1})
            m.save_exact_source_checkpoint(args, config, 2, [100, 101], 0, basis)
            second = json.loads(target.read_text())
            self.assertEqual(second["processed"], 2)
            self.assertEqual(len(second["pivots"]), 2)
            self.assertNotEqual(old, target.read_bytes())
            self.assertFalse(target.with_name(target.name + ".tmp").exists())

    def test_existing_temp_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "A_state.json"
            temporary = path.with_name(path.name + ".tmp")
            temporary.write_text("do not overwrite")
            with self.assertRaises(FileExistsError):
                m.save_exact_source_checkpoint(
                    SimpleNamespace(checkpoint=path), {}, 0, [], 0, {})
            self.assertEqual(temporary.read_text(), "do not overwrite")
            self.assertFalse(path.exists())


if __name__ == "__main__":
    unittest.main()
