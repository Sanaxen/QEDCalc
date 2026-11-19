"""Read-only diagnosis of preserved VP05 sector202 sec202a RAM guard stop.

Uses only hash-verified isolated project, bounded saved Kira log tails and
bounded monitored_metrics.jsonl. It does not run Kira, deserialize Kira DB,
decompress SYSTEMs, restart projects, or promote an IBP identity.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from examples import three_loop_vp05_stage2_sector202_isolated as isolated
from examples import three_loop_vp05_stage2_residual_forensics as forensic

TAG = "VP05_SECTOR202_STOP_FORENSICS "
MAX_METRIC_BYTES = 4 * 1024 * 1024
MAX_METRIC_SAMPLES = 10000
MAX_INTERVALS = 30
EXPECTED_REASON = "ram_stop"
EXPECTED_KIRA_RETURN = -15


def metrics(path: Path) -> dict:
    """Strict bounded stream read; only samples already written by monitor."""
    if not forensic.regular_file(path):
        raise RuntimeError("Expected non-linked existing metrics file: " + str(path))
    if path.stat().st_size > MAX_METRIC_BYTES:
        raise RuntimeError("Metrics exceed bounded read cap, request manual review")
    samples: list[dict] = []
    last_time = -1.0
    for number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        if not line.strip():
            continue
        if number > MAX_METRIC_SAMPLES:
            raise RuntimeError("Excessive metric samples")
        record = json.loads(line)
        if not isinstance(record, dict):
            raise RuntimeError("Malformed monitor metrics")
        try:
            t, ram, swap = (float(record[x]) for x in
                            ("elapsed_s", "ram_used_gib", "swap_used_gib"))
        except (ValueError, TypeError, KeyError) as exc:
            raise RuntimeError("Missing or malformed resource monitor sample") from exc
        if (not all(map(math.isfinite, (t, ram, swap)))
            or t < last_time or t < 0 or ram < 0 or swap < 0):
            raise RuntimeError("Non-monotonic/invalid resource sample")
        cpu = record.get("kira_main_cpu_percent")
        if cpu is not None and (not isinstance(cpu, (float, int))
                                or not math.isfinite(cpu) or cpu < 0):
            raise RuntimeError("Invalid CPU sample")
        samples.append({"elapsed_s": t, "ram_gib": ram, "swap_gib": swap,
                        "cpu_percent": cpu, "last_sector": record.get("last_sector")})
        last_time = t
    if not samples:
        raise RuntimeError("No monitor resource samples available")
    out = {"samples": len(samples),
           "first": samples[0], "last": samples[-1],
           "max_ram_gib": max(x["ram_gib"] for x in samples),
           "max_swap_gib": max(x["swap_gib"] for x in samples),
           "first_warning": {}, "time_buckets": []}
    for threshold in (18, 20, 22):
        first = next((x for x in samples if x["ram_gib"] >= threshold), None)
        out["first_warning"][str(threshold) + "_gib"] = (
            first["elapsed_s"] if first else None)
    for band in range(min(MAX_INTERVALS, int(samples[-1]["elapsed_s"] // 60) + 1)):
        group = [x for x in samples if int(x["elapsed_s"] // 60) == band]
        if group:
            out["time_buckets"].append({
                "minute": band, "count": len(group),
                "ram_last_gib": group[-1]["ram_gib"],
                "ram_max_gib": max(x["ram_gib"] for x in group),
                "swap_max_gib": max(x["swap_gib"] for x in group),
                "last_reported_sector": group[-1]["last_sector"]})
    return out


def inspect(run_id: str = "sec202a") -> dict:
    # Full Step93/no202a chain plus new project's SHA-verified original inputs.
    scope = isolated.scope()
    saved = isolated.status(run_id, scope)
    if saved.get("state") != "guard_stopped_ram_stop":
        raise RuntimeError("Expected preserved sector202 RAM-stop, not " + str(saved.get("state")))
    exit_data = saved.get("monitor_result") or {}
    if (exit_data.get("reason") != EXPECTED_REASON
        or exit_data.get("success") is not False
        or exit_data.get("kira_returncode") != EXPECTED_KIRA_RETURN):
        raise RuntimeError("Monitor outcome differs from protected RAM guard stop")
    project = isolated.project_for(run_id)
    profile = forensic.project_profile(
        project, expected_targets=scope["targets"],
        mandatory_name=isolated.MANDATORY, preferred_name=isolated.PREFERRED)
    if (profile.get("project_exists") is not True
        or profile.get("mandatory_input_set_matches_expected") is not True
        or profile.get("preferred_input_set_matches_expected") is not True):
        raise RuntimeError("Preserved exact-sector inputs mismatch")
    history = metrics(project / "monitored_metrics.jsonl")
    actual_ram = history["max_ram_gib"]
    if actual_ram < isolated.RAM_STOP:
        raise RuntimeError("Monitor claims RAM stop but saved trace never reached threshold")
    if (history["max_swap_gib"] >= isolated.SWAP_STOP
        or history["samples"] < 2):
        raise RuntimeError("Unexpected swap/sample history for recorded RAM-only stop")
    if (not isinstance(exit_data.get("elapsed_s"), (float, int))
        or abs(float(exit_data["elapsed_s"]) - history["last"]["elapsed_s"]) > 15):
        raise RuntimeError("Saved resource trace/exit elapsed timing mismatch")
    log_rows = profile.get("log_files", [])
    progress = [r["last_sector_progress"] for r in log_rows
                if r.get("last_sector_progress")]
    master_meta = profile["metadata"]
    return {
        "status": "VP05_SECTOR202_RAM_STOP_FORENSICS_READ_ONLY",
        "run_id": run_id, "project": str(project),
        "candidate_count": 3, "effective_seed": "r7s5d3",
        "saved_monitor_reason": exit_data["reason"],
        "saved_kira_returncode": exit_data["kira_returncode"],
        "saved_elapsed_s": exit_data["elapsed_s"],
        "resource_trace": history,
        "last_log_sector_progress": progress[-1] if progress else None,
        "log_tail_inspection": log_rows,
        "saved_project": {
            "kira_db": master_meta["kira_db"],
            "system_equations": master_meta["system_equations"],
            "masters": master_meta["masters"],
            "masters_final": master_meta["masters_final"],
            "results_dir_present": master_meta["results_dir_present"],
            "tmp_dir_present": master_meta["tmp_dir_present"],
            "sectormappings_dir_present": master_meta["sectormappings_dir_present"],
            "log_file_count": len(log_rows),
            "logs_truncated": profile["log_files_truncated"],
        },
        "conclusions": {
            "ram_guard_stop_verified": True,
            "sector202_local_master_retention_proven": False,
            "kira_mathematical_failure_demonstrated": False,
            "last_log_progress_does_not_establish_failure_phase": True,
            "parent_206_234_or_whole_seed_closure_proven": False,
            "source_equations_can_be_reused_only_after_exact_context_audit": True,
            "protect_original_sec202a": True,
            "no_automatic_retry": True,
        },
        "next_action": (
            "Use saved Kira progress and RAM trend to identify actual equation-generation "
            "or downstream bottleneck; compare source envelope before considering "
            "smaller target-specific restricted IBP problems. No repeat of sec202a."
        ),
        "kira_executed": False,
        "files_modified": False,
        "promotion_ready_created": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", default="sec202a")
    args = parser.parse_args()
    print(TAG + json.dumps(inspect(args.run_id), ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
