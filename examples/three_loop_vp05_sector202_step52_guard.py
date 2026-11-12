"""Guarded single-step continuation of VP05 sector202 Target A from step51.

Runs the existing checkpoint reducer for exactly ONE new elimination, inside
a wall-clock bounded child process. Its existing own safety caps remain
unchanged. Does not reuse the completed step51 scratch, whose source SHA
is bound to step50.
"""
from __future__ import annotations
import argparse
import json
import subprocess
import sys
from pathlib import Path
from examples.three_loop_vp05_sector202_step51_scratch import STATE
from examples.three_loop_vp05_sector202_target_exact_reduction import CHECKPOINT, SOURCE, CERT, sha


def validate_state(path):
    state = json.loads(path.read_text(encoding="utf-8-sig"))
    if (state.get("steps") != 51 or state.get("config", {}).get("target") != "A"
        or state.get("status") != "EXACT_TARGET_PREFIX_NOT_PROOF"
        or state.get("exact_target_proven") is not False
        or state.get("step51_original_ibp_replay_verified") is not True
        or state.get("step51_exact_coefficient_count") != 288
        or state.get("step51_exact_compacted_count") != 8
        or len(state.get("remaining", [])) != 100
        or len(state.get("source", [])) != 186
        or len(state.get("pivot_path", [])) != 51
        or state.get("config", {}).get("max_expression_chars") != 7500
        or state.get("config", {}).get("source_checkpoint_sha256") != sha(CHECKPOINT)
        or state.get("config", {}).get("source_sha256") != sha(SOURCE)
        or state.get("config", {}).get("certificate_sha256") != sha(CERT)):
        raise RuntimeError("Expected audited Target A step51 with matching immutable inputs")
    if max((len(str(x[1])) for x in state["remaining"] + state["source"]), default=0) > 7500:
        raise RuntimeError("Step51 checkpoint exceeds formal cap")
    return state


def interpret(outcome, before, after):
    """No claim that step52 exists without confirmed durable state."""
    if after.get("steps") == 52 and len(after.get("pivot_path", [])) == 52:
        if outcome != 0:
            raise RuntimeError("Child returned error but state advanced; manual review required")
        return "STEP52_COMMITTED_CHECKPOINT_NOT_TARGET_PROOF"
    if after == before or (after.get("steps") == 51 and
        {k: v for k, v in after.items() if k != "status"} ==
        {k: v for k, v in before.items() if k != "status"} and
        after.get("status") in ("EXACT_TARGET_PREFIX_NOT_PROOF", "EXACT_TARGET_CAP_REACHED_NOT_PROOF")):
        return "STEP52_NOT_COMMITTED_BOUNDED_OR_CAP_STOP_NOT_PROOF"
    raise RuntimeError("Checkpoint changed unexpectedly; do not repeat without review")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", type=Path, default=STATE)
    ap.add_argument("--hours", type=float, default=12.0)
    ap.add_argument("--check-only", action="store_true")
    args = ap.parse_args()
    if not 0 < args.hours <= 12:
        ap.error("--hours must be in (0, 12]")
    before = validate_state(args.state)
    head = {"status": "STEP52_BOUNDED_PREFLIGHT_PASS_NOT_PROOF",
            "steps": 51, "remaining_terms": 100,
            "hours_ceiling": args.hours, "state_sha256": sha(args.state)}
    print("VP05_STEP52_GUARD " + json.dumps(head), flush=True)
    if args.check_only:
        return
    cmd = [sys.executable, "-m",
           "examples.three_loop_vp05_sector202_target_exact_checkpoint",
           "--resume", "--state", str(args.state),
           "--target", "A", "--new-steps", "1",
           "--max-columns", str(before["config"]["max_columns"]),
           "--max-support", str(before["config"]["max_support"]),
           "--max-expression-chars", str(before["config"]["max_expression_chars"]),
           "--max-steps-total", str(before["config"]["max_steps_total"])]
    timed_out = False
    try:
        proc = subprocess.run(cmd, timeout=args.hours * 3600,
                              check=False)
        result_code = proc.returncode
    except subprocess.TimeoutExpired:
        timed_out = True
        result_code = -1
    after = json.loads(args.state.read_text(encoding="utf-8-sig"))
    status = interpret(result_code, before, after)
    print("VP05_STEP52_GUARD " + json.dumps({
        "status": status, "timed_out": timed_out,
        "steps_before": 51, "steps_after": after["steps"],
        "remaining_terms": len(after["remaining"]),
        "state_sha256": sha(args.state),
        "exact_target_proven": after.get("exact_target_proven")}), flush=True)
    if result_code and not timed_out:
        raise SystemExit(result_code)


if __name__ == "__main__":
    main()
