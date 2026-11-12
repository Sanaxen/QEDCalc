"""Guarded exact single-step attempt from verified VP05 sector202 Target A Step61.

Read-only preflight pins the precisely verified Step61 state SHA256. The
existing checkpoint engine attempts ONE Step62 elimination, retaining the
original 7500-character, 256-column and 400-source caps. Any cap stop leaves
the 61 elimination steps intact. No completed target proof is claimed.
"""
from __future__ import annotations
import argparse
import json
import subprocess
import sys
from pathlib import Path

from examples.three_loop_vp05_sector202_step51_scratch import STATE
from examples.three_loop_vp05_sector202_target_exact_reduction import (
    CHECKPOINT, SOURCE, CERT, sha,
)

EXPECTED_STEP61_SHA = "012fd465705559bf9a127f64649a012f1fdff96941e3c374ececbc4fe9948ec1"


def validate_state(path, source_checkpoint=CHECKPOINT, source=SOURCE, certificate=CERT):
    if sha(path) != EXPECTED_STEP61_SHA:
        raise RuntimeError("Expected exact verified Step61 SHA256 from exact progress log")
    state = json.loads(path.read_text(encoding="utf-8-sig"))
    config = state.get("config", {})
    if (state.get("steps") != 61 or config.get("target") != "A"
        or state.get("status") != "EXACT_TARGET_PREFIX_NOT_PROOF"
        or state.get("exact_target_proven") is not False
        or len(state.get("remaining", [])) != 87
        or len(state.get("source", [])) != 165
        or len(state.get("pivot_path", [])) != 61
        or config.get("max_expression_chars") != 7500
        or config.get("max_columns") != 256
        or config.get("max_support") != 400
        or config.get("source_checkpoint_sha256") != sha(source_checkpoint)
        or config.get("source_sha256") != sha(source)
        or config.get("certificate_sha256") != sha(certificate)):
        raise RuntimeError("Verified Step61 checkpoint metadata or input hashes mismatch")
    if state.get("metrics", {}).get("lead") != [166596413882368, 139]:
        raise RuntimeError("Unexpected next Step62 pivot lead")
    sizes = [len(v) for _, v in state["remaining"] + state["source"]]
    if max(sizes, default=0) != 7075:
        raise RuntimeError("Unexpected Step61 expression length")
    return state


def interpret(returncode, before, after):
    if after.get("steps") == 62 and len(after.get("pivot_path", [])) == 62:
        if returncode != 0 or after.get("exact_target_proven") is not False:
            raise RuntimeError("Step62 changed with unexpected error/proof state")
        return "STEP62_COMMITTED_CHECKPOINT_NOT_TARGET_PROOF"
    if after.get("steps") == 61 and (
        after == before or (
            {k: v for k, v in after.items() if k != "status"} ==
            {k: v for k, v in before.items() if k != "status"}
            and after.get("status") in (
                "EXACT_TARGET_PREFIX_NOT_PROOF", "EXACT_TARGET_CAP_REACHED_NOT_PROOF"
            )
        )
    ):
        return "STEP62_NOT_COMMITTED_BOUNDED_OR_CAP_STOP_NOT_PROOF"
    raise RuntimeError("Unexpected checkpoint mutation: manual review required")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", type=Path, default=STATE)
    ap.add_argument("--hours", type=float, default=12.0)
    ap.add_argument("--check-only", action="store_true")
    args = ap.parse_args()
    if not 0 < args.hours <= 12:
        ap.error("--hours must be within (0, 12]")
    before = validate_state(args.state)
    print("VP05_STEP62_GUARD " + json.dumps({
        "status": "STEP62_BOUNDED_PREFLIGHT_PASS_NOT_PROOF",
        "steps": 61, "remaining_terms": 87,
        "maximum_expression_chars": 7075,
        "formal_expression_cap": 7500,
        "hours_ceiling": args.hours,
        "state_sha256": sha(args.state),
    }), flush=True)
    if args.check_only:
        return
    cfg = before["config"]
    cmd = [sys.executable, "-m",
           "examples.three_loop_vp05_sector202_target_exact_checkpoint",
           "--resume", "--state", str(args.state), "--target", "A",
           "--new-steps", "1",
           "--max-columns", str(cfg["max_columns"]),
           "--max-support", str(cfg["max_support"]),
           "--max-expression-chars", str(cfg["max_expression_chars"]),
           "--max-steps-total", str(cfg["max_steps_total"])]
    timed_out = False
    try:
        run = subprocess.run(cmd, timeout=args.hours * 3600, check=False)
        rc = run.returncode
    except subprocess.TimeoutExpired:
        timed_out = True
        rc = -1
    after = json.loads(args.state.read_text(encoding="utf-8-sig"))
    status = interpret(rc, before, after)
    print("VP05_STEP62_GUARD " + json.dumps({
        "status": status, "timed_out": timed_out,
        "steps_before": 61, "steps_after": after["steps"],
        "remaining_terms": len(after["remaining"]),
        "original_support": len(after["source"]),
        "state_sha256": sha(args.state),
        "exact_target_proven": after.get("exact_target_proven"),
    }), flush=True)
    if rc != 0 and not timed_out:
        raise SystemExit(rc)


if __name__ == "__main__":
    main()
