"""Offline unit tests of read-only target coefficient inventory."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from examples.three_loop_vp05_sector202_target_expression_inventory import (
    inspect,rank_entries,
)
class TargetExpressionInventoryTests(unittest.TestCase):
    def test_sorted_longest_entries(self):
        state={"remaining":[[[1,73],"z+2"],[[2,73],"(z+d+2)/3"]],
               "source":[[12,"(z+5)/2"]]}
        a=rank_entries(state,2,3)
        self.assertEqual(len(a),2)
        self.assertEqual(a[0]["chars"],len("(z+d+2)/3"))
        self.assertEqual(a[0]["preview"],"(z+")

    def test_inventory_read_only_and_hash_guards(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths=[Path(tmp)/name for name in ("checkpoint","source","certificate")]
            for path,value in zip(paths,(b"checkpoint",b"source",b"certificate")):
                path.write_bytes(value)
            config={k:hashlib.sha256(p.read_bytes()).hexdigest() for k,p in zip(
                ("source_checkpoint_sha256","source_sha256","certificate_sha256"),paths)}
            config.update({"target":"A","max_expression_chars":7500})
            state={"version":1,"status":"EXACT_TARGET_PREFIX_NOT_PROOF",
                   "exact_target_proven":False,"steps":1,"pivot_path":[[1,73]],
                   "config":config,"remaining":[[[2,73],"z+2"]],
                   "source":[[12,"-1/2"]],
                   "metrics":{"row_expression_chars":3,"source_expression_chars":4,
                              "remainder_terms":1,"original_support":1}}
            before=json.dumps(state,sort_keys=True)
            report=inspect(state,*paths)
            self.assertEqual(report["steps"],1)
            self.assertFalse(report["checkpoint_modified"])
            self.assertEqual(before,json.dumps(state,sort_keys=True))
            paths[0].write_bytes(b"tampered")
            with self.assertRaisesRegex(RuntimeError,"digest mismatch"):
                inspect(state,*paths)

    def test_reject_inconsistent_metrics(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths=[Path(tmp)/str(i) for i in range(3)]
            for p in paths:p.write_bytes(b"x")
            d=hashlib.sha256(b"x").hexdigest()
            state={"version":1,"status":"EXACT_TARGET_PREFIX_NOT_PROOF",
                   "exact_target_proven":False,"steps":0,"pivot_path":[],
                   "config":{"source_checkpoint_sha256":d,"source_sha256":d,
                             "certificate_sha256":d},
                   "remaining":[],"source":[],
                   "metrics":{"row_expression_chars":1,"source_expression_chars":0,
                              "remainder_terms":0,"original_support":0}}
            with self.assertRaisesRegex(RuntimeError,"metrics"):
                inspect(state,*paths)

if __name__=="__main__":
    unittest.main()
