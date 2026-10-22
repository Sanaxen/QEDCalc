"""Prepare bounded exact-source selectors from a modular target dependency DAG.

Only a selection utility: this does NOT prove exact target reduction.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from examples.three_loop_sector203_weight_audit import ROOT

DEFAULT = ROOT / "output/three_loop_integral_family_audit/vp05_sector202_target_dependency_selection.json"
OUT = ROOT / "output/three_loop_integral_family_audit/vp05_sector202_dependency_chunk.json"

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path, default=DEFAULT)
    p.add_argument("--output", type=Path, default=OUT)
    p.add_argument("--target", type=int, choices=(0, 1), default=0)
    p.add_argument("--start", type=int, default=0)
    p.add_argument("--rows", type=int, default=100)
    args = p.parse_args()
    if args.start < 0 or not 1 <= args.rows <= 100:
        p.error("Require --start >= 0 and 1 <= --rows <= 100")
    obj = json.loads(args.input.read_text(encoding="utf-8-sig"))
    if obj.get("status") != "MODULAR_DEPENDENCY_SOURCE_SELECTION_NOT_EXACT_PROOF":
        raise RuntimeError("Unexpected dependency selection format")
    target = obj["targets"][args.target]
    if target["target_index"] != args.target:
        raise RuntimeError("Target order mismatch")
    ids = target["global_zero_based_ids"]
    if ids != sorted(set(ids)) or target["count"] != len(ids):
        raise RuntimeError("Invalid target dependency IDs")
    chosen = ids[args.start:args.start+args.rows]
    if not chosen:
        raise RuntimeError("Empty requested dependency chunk")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(chosen, indent=2) + "\n", encoding="utf-8")
    print("VP05_SECTOR202_DEPENDENCY_CHUNK " + json.dumps({
        "status": "MODULAR_DEPENDENCY_CHUNK_NOT_PROOF", "target": args.target,
        "total_dependency_rows": len(ids), "chunk_start": args.start,
        "chunk_rows": len(chosen), "output": str(args.output),
        "first_original_id": chosen[0], "last_original_id": chosen[-1],
        "exact_target_reduction_proven": False,
    }), flush=True)

if __name__ == "__main__":
    main()
