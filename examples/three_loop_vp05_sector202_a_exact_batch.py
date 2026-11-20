"""Guarded batch of exact QQ(z,d) original-source pivots for VP05 Target A.

Uses the existing independently replaying exact source checkpoint engine in a
brand-new Target-A-only state file. Never touches Step93 B, union checkpoint,
Kira projects or candidate registry. Target A is NOT proven by a pivot set;
target identity requires a separately audited exact zero-remainder source replay.

Each subprocess batch is time limited; the underlying engine atomically
saves after each completed batch (NOT after every row). A timed-out batch is
never silently resumed by the same invocation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

from examples import three_loop_vp05_sector202_source_split_audit as split
from examples import three_loop_vp05_sector202_target_exact_reduction as exact

TAG = "VP05_SECTOR202_A_EXACT_BATCH "
ACK = "EXECUTE_VP05_A_339_EXACT_SOURCE_BATCH"
ROOT = exact.ROOT
DIR = exact.BASE
FILENAME = "vp05_sector202_A_339_exact_v1_checkpoint.json"
MAX_BATCHES = 20
MAX_ROWS = 5
MAX_TIMEOUT = 900
PARAMS = {"max_columns": 256, "max_source_support": 400,
          "max_expression_chars": 7500}
EXPECTED_TOTAL = 339
SOURCE_SHA = "f0dd7f338ead97e455306bc49c4ce475fe8a8bee3e5a866f6fa17de1e9ad0163"
CERT_SHA = "512114a669d3fb8761d89bfe11a51cc8ec146d46739a36b61e869edcddb583eb"


def project(run_id: str) -> tuple[Path, Path]:
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,24}", run_id):
        raise ValueError("Invalid run ID")
    ckpt = DIR / ("vp05_sector202_A_339_exact_" + run_id + "_v1.json")
    logdir = DIR / ("vp05_sector202_A_339_exact_" + run_id + "_logs")
    return ckpt, logdir


def sha(path: Path) -> str:
    if path.is_symlink() or not path.is_file():
        raise RuntimeError("Missing or linked pinned input: " + str(path))
    return hashlib.sha256(path.read_bytes()).hexdigest()


def preflight() -> dict:
    report = split.inspect()
    if (report.get("status") != "VP05_SECTOR202_A_EXACT_SOURCE_REVIEW_REQUIRED"
        or report["original_modular_support"]["target_a"]["row_count"] != EXPECTED_TOTAL
        or report["original_modular_support"]["A_only_count"] != 0
        or report["original_modular_support"]["intersection_count"] != EXPECTED_TOTAL
        or report["step93_exact_b"]["symbolic_QQ_z_d_original_ibp_replay_verified"] is not True
        or report["target_obligations"][0]["proven"] is not False):
        raise RuntimeError("Target A original source split scope changed")
    if sha(exact.SOURCE) != SOURCE_SHA or sha(exact.CERT) != CERT_SHA:
        raise RuntimeError("Original source/certificate differs from audited Step93 inputs")
    return {"source_sha256": SOURCE_SHA, "certificate_sha256": CERT_SHA,
            "A_original_support_rows": EXPECTED_TOTAL}


def checkpoint_state(path: Path) -> dict:
    if path.is_symlink() or path.with_name(path.name + ".tmp").exists():
        raise RuntimeError("Unresolved linked/temporary exact checkpoint; manual review")
    if not path.exists():
        return {"state": "not_started", "processed": 0, "total": EXPECTED_TOTAL,
                "checkpoint_sha256": None}
    raw = path.read_bytes()
    try:
        value = json.loads(raw.decode("utf-8-sig"))
    except (ValueError, UnicodeDecodeError) as exc:
        raise RuntimeError("Malformed exact A checkpoint") from exc
    config = value.get("config", {})
    support = split.inspect()["original_modular_support"]["target_a"]["source_row_ids"]
    selected_hash = hashlib.sha256(json.dumps(sorted(support)).encode()).hexdigest()
    if (value.get("version") != 1
        or value.get("status") != "EXACT_SOURCE_CHECKPOINT_NOT_TARGET_PROOF"
        or value.get("total") != EXPECTED_TOTAL
        or not isinstance(value.get("processed"), int)
        or not 0 <= value["processed"] <= EXPECTED_TOTAL
        or type(value.get("dependent")) is not int
        or value["dependent"] < 0 or value["dependent"] > value["processed"]
        or len(value.get("pivots", [])) + value["dependent"] != value["processed"]
        or value.get("source_pivots_exact_replay_verified") is not True
        or value.get("exact_target_reduction_proven") is not False
        or config != {
            "source_sha256": SOURCE_SHA, "certificate_sha256": CERT_SHA,
            "target": "A", "ids_sha256": selected_hash, **PARAMS}):
        raise RuntimeError("Saved A checkpoint schema/hash/scope does not match")
    return {"state": "source_rows_complete_NOT_target_proof"
            if value["processed"] == EXPECTED_TOTAL else "partial_source_checkpoint",
            "processed": value["processed"], "total": EXPECTED_TOTAL,
            "rank": len(value["pivots"]), "dependent": value["dependent"],
            "checkpoint_sha256": hashlib.sha256(raw).hexdigest()}


def audit(run_id: str) -> dict:
    scope = preflight()
    checkpoint, logdir = project(run_id)
    if logdir.is_symlink() or (logdir.exists() and not logdir.is_dir()):
        raise RuntimeError("Log path is not a regular directory")
    state = checkpoint_state(checkpoint)
    return {"status": "VP05_A_EXACT_SOURCE_CHECKPOINT_AUDIT_NOT_TARGET_PROOF",
            "run_id": run_id, "checkpoint": str(checkpoint), "logdir": str(logdir),
            "checkpoint_state": state, "source": scope,
            "exact_target_A_proven": False,
            "new_seed_sector202_local_retention_proven": False,
            "whole_family_63_closure_proven": False,
            "kira_executed": False, "files_modified": False}


def command(checkpoint: Path, *, resume: bool, rows: int) -> list[str]:
    args = [
        sys.executable, "-m", "examples.three_loop_vp05_sector202_exact_support_checkpoint",
        "--input", str(exact.SOURCE), "--certificate", str(exact.CERT),
        "--checkpoint", str(checkpoint), "--target", "A",
        "--rows-per-run", str(rows),
        "--max-columns", str(PARAMS["max_columns"]),
        "--max-source-support", str(PARAMS["max_source_support"]),
        "--max-expression-chars", str(PARAMS["max_expression_chars"]),
    ]
    if resume:
        args.append("--resume")
    return args


def run(run_id: str, *, acknowledge: str, batches: int,
        rows: int, timeout: int) -> dict:
    if acknowledge != ACK:
        raise ValueError("Exact A batch acknowledgement required")
    if (not 1 <= batches <= MAX_BATCHES or not 1 <= rows <= MAX_ROWS
        or not 1 <= timeout <= MAX_TIMEOUT):
        raise ValueError("Batch safety parameters exceed caps")
    if os.name != "nt":
        raise RuntimeError("Run only in the user's Windows repository")
    preflight()
    checkpoint, logdir = project(run_id)
    state = checkpoint_state(checkpoint)
    if state["state"] == "source_rows_complete_NOT_target_proof":
        return audit(run_id)
    if not DIR.is_dir():
        raise RuntimeError("Original output audit directory absent")
    logdir.mkdir(exist_ok=True)  # Dedicated per-run logs only.
    done = []
    for _ in range(batches):
        if state["processed"] >= EXPECTED_TOTAL:
            break
        # Never overwrite a saved job log; every source checkpoint is hashed.
        step = state["processed"]
        stdout = logdir / ("batch_from_%03d.log" % step)
        if stdout.exists() or stdout.is_symlink():
            raise RuntimeError("Prior batch exists at this exact checkpoint; manual review: " + str(stdout))
        args = command(checkpoint, resume=state["processed"] != 0, rows=rows)
        before = state["checkpoint_sha256"]
        t = time.monotonic()
        terminated = False
        with stdout.open("x", encoding="utf-8") as stream:
            try:
                proc = subprocess.run(args, cwd=ROOT, stdout=stream,
                                      stderr=subprocess.STDOUT, timeout=timeout)
                code = proc.returncode
            except subprocess.TimeoutExpired:
                code, terminated = None, True
        # Atomic batch checkpoint is either the previous fully validated version
        # or new complete batch. For new checkpoints engine validates source
        # pivots on every resume using original IBP rows.
        state = checkpoint_state(checkpoint)
        if state["processed"] < step or (before is not None and
                                        state["processed"] == step and
                                        state["checkpoint_sha256"] != before):
            raise RuntimeError("Saved checkpoint changed without committed source-row progress")
        done.append({"from": step, "to": state["processed"],
                     "exit_code": code, "timed_out": terminated,
                     "elapsed_s": round(time.monotonic()-t, 1),
                     "log": str(stdout)})
        if terminated or code != 0 or state["processed"] == step:
            break
    return {"status": ("VP05_A_339_EXACT_SOURCE_ROWS_COMPLETE_NOT_TARGET_PROOF"
                       if state["processed"] == EXPECTED_TOTAL else
                       "VP05_A_339_EXACT_SOURCE_PARTIAL_PRESERVED_NOT_PROOF"),
            "run_id": run_id, "checkpoint_state": state, "batches": done,
            "source_rows": EXPECTED_TOTAL, "exact_A_target_proven": False,
            "no_kira_executed": True,
            "original_sources_modified": False, "step93_B_proof_modified": False,
            "standard_seed_closure_proven": False}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("plan", "audit", "run"))
    ap.add_argument("--run-id", default="a339a")
    ap.add_argument("--acknowledge", default="")
    ap.add_argument("--batches", type=int, default=10)
    ap.add_argument("--rows-per-batch", type=int, default=5)
    ap.add_argument("--timeout-seconds", type=int, default=900)
    opts = ap.parse_args()
    result = (audit(opts.run_id) if opts.mode in ("plan", "audit") else
              run(opts.run_id, acknowledge=opts.acknowledge,
                  batches=opts.batches, rows=opts.rows_per_batch,
                  timeout=opts.timeout_seconds))
    print(TAG + json.dumps(result, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
