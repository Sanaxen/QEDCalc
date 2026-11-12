"""Promote fully audited VP05 sector202 Target A step51, preserving step50.

Requires 288/288 exact coefficient identities, 8/8 exact compact forms,
and 364/364 exact original-IBP replay bound to immutable input hashes.
The final Target A reduction is NOT proved: 100 residual terms remain.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path

from examples.three_loop_vp05_sector202_step51_scratch import (
    STATE, SCRATCH, SEAL, source_context, atomic_save,
)
from examples.three_loop_vp05_sector202_target_exact_reduction import (
    CHECKPOINT, SOURCE, CERT, sha,
)
from examples.three_loop_vp05_sector202_step51_exact_coefficient_audit import (
    PROGRESS as EXACT_PROGRESS,
)
from examples.three_loop_vp05_sector202_step51_compaction import OUT as COMPACTION, CAP
from examples.three_loop_vp05_sector202_step51_exact_ibp_replay import (
    REPORT, context, identity_config,
)
from examples.three_loop_vp05_sector202_target_exact_checkpoint import metrics
from examples.three_loop_vp05_sector202_exact_prefix_smoke import expr
import sympy as sp


def build_promoted(old, rem, trace, pivot_lead):
    if old.get("steps") != 50 or old.get("config", {}).get("target") != "A":
        raise RuntimeError("Only formally saved Target A step50 may be promoted")
    if old.get("exact_target_proven") is not False:
        raise RuntimeError("Unexpected target proof state")
    if tuple(pivot_lead) != min(tuple(k) for k, _ in old["remaining"]):
        raise RuntimeError("Promotion pivot does not match saved lead")
    if not rem or min(rem) <= tuple(pivot_lead):
        raise RuntimeError("Step51 pivot did not disappear or order not increased")
    if len(rem) != 100 or len(trace) != 186:
        raise RuntimeError("Unexpected Step51 candidate support sizes")
    if any(len(x) > CAP for x in list(rem.values()) + list(trace.values())):
        raise RuntimeError("Compacted candidate still exceeds formal cap")
    if len(old.get("pivot_path", [])) != 50:
        raise RuntimeError("Invalid original pivot path")
    out = dict(old)
    out["steps"] = 51
    out["status"] = "EXACT_TARGET_PREFIX_NOT_PROOF"
    out["remaining"] = [[list(k), v] for k, v in sorted(rem.items())]
    out["source"] = [[rid, v] for rid, v in sorted(trace.items())]
    out["pivot_path"] = old["pivot_path"] + [list(pivot_lead)]
    out["metrics"] = {
        "remainder_terms": len(rem), "original_support": len(trace),
        "row_expression_chars": max(map(len, rem.values()), default=0),
        "source_expression_chars": max(map(len, trace.values()), default=0),
        "max_expression_chars": max([len(x) for x in list(rem.values()) + list(trace.values())], default=0),
        "lead": list(min(rem)),
    }
    if (len(rem) > old["config"]["max_columns"]
        or len(trace) > old["config"]["max_support"]
        or out["metrics"]["max_expression_chars"] > old["config"]["max_expression_chars"]):
        raise RuntimeError("Formal checkpoint safety cap violated")
    out["exact_target_proven"] = False
    out["original_source_replay_proven"] = False
    out["protected_source_checkpoint_modified"] = False
    out["step51_original_ibp_replay_verified"] = True
    out["step51_exact_coefficient_count"] = 288
    out["step51_exact_compacted_count"] = 8
    return out


def validate_replay(report, cfg, key_count):
    if (report.get("version") != 1
        or report.get("config") != cfg
        or report.get("status") != "EXACT_IBP_REPLAY_PREFIX_NOT_TARGET_PROOF"
        or type(report.get("checked")) is not int
        or report["checked"] != key_count
        or key_count != 364
        or report.get("original_ibp_replay_verified") is not True
        or report.get("exact_target_proven") is not False
        or report.get("formal_target_state_modified") is not False
        or report.get("protected_source_checkpoint_modified") is not False):
        raise RuntimeError("364/364 verified exact replay evidence required")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", type=Path, default=STATE)
    ap.add_argument("--source-checkpoint", type=Path, default=CHECKPOINT)
    ap.add_argument("--input", type=Path, default=SOURCE)
    ap.add_argument("--certificate", type=Path, default=CERT)
    ap.add_argument("--scratch", type=Path, default=SCRATCH)
    ap.add_argument("--verified-seal", type=Path, default=SEAL)
    ap.add_argument("--exact-progress", type=Path, default=EXACT_PROGRESS)
    ap.add_argument("--compaction", type=Path, default=COMPACTION)
    ap.add_argument("--report", type=Path, default=REPORT)
    ap.add_argument("--backup", type=Path, default=STATE.with_name(
        "vp05_sector202_A_exact_target_state_step50_backup.json"))
    ap.add_argument("--check-only", action="store_true")
    args = ap.parse_args()
    protected = (args.source_checkpoint, args.input, args.certificate,
                 args.scratch, args.verified_seal, args.exact_progress,
                 args.compaction, args.report)
    if args.backup.resolve() in {p.resolve() for p in protected + (args.state,)}:
        ap.error("Backup must be a separate new artifact")
    old_bytes = args.state.read_bytes()
    old = json.loads(old_bytes.decode("utf-8-sig"))
    initial, rem, trace, rows, keys = context(args)
    report = json.loads(args.report.read_text(encoding="utf-8-sig"))
    cfg = identity_config(args, initial, rem, trace, keys)
    validate_replay(report, cfg, len(keys))
    pivot_lead, _, _ = source_context(old, args.source_checkpoint)
    candidate = build_promoted(old, rem, trace, pivot_lead)
    result = {"status": "STEP51_FORMAL_PROMOTION_PREFLIGHT_PASS_NOT_TARGET_PROOF",
              "steps_before": 50, "steps_after": 51, "residual_terms": len(rem),
              "original_support": len(trace),
              "max_expression_chars": candidate["metrics"]["max_expression_chars"],
              "source_state_sha256": sha(args.state),
              "original_replay_sha256": sha(args.report),
              "exact_target_proven": False}
    if args.check_only:
        print("VP05_STEP51_FORMAL_PROMOTION " + json.dumps(result), flush=True)
        return
    if args.backup.exists() or args.state.with_name(args.state.name + ".tmp").exists():
        raise FileExistsError("Backup or promotion temporary file already exists")
    # Preserve byte-identical old step50 and durable fsync BEFORE replacement.
    args.backup.parent.mkdir(parents=True, exist_ok=True)
    with args.backup.open("xb") as out:
        out.write(old_bytes)
        out.flush()
        os.fsync(out.fileno())
    if args.backup.read_bytes() != old_bytes or args.state.read_bytes() != old_bytes:
        raise RuntimeError("Backup mismatch or concurrent step50 modification")
    atomic_save(args.state, candidate, True)
    saved = json.loads(args.state.read_text(encoding="utf-8-sig"))
    if saved != candidate:
        raise RuntimeError("Post-promotion checksum/content mismatch")
    result["status"] = "STEP51_FORMAL_PREFIX_PROMOTED_WITH_BACKUP_NOT_TARGET_PROOF"
    result["backup_sha256"] = sha(args.backup)
    result["new_state_sha256"] = sha(args.state)
    print("VP05_STEP51_FORMAL_PROMOTION " + json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
