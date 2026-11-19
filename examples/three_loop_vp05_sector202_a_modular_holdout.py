"""Bounded original-source finite-field holdouts for VP05 sector202 Target A.

339 original IBP rows supporting A at p=1000003 are a strict subset of
the 389 rows supporting B. This tests whether those SAME original source
equations span the *proposed* A-C-small4 identity at other primes.
Passes are numerical diagnostics ONLY, never an exact QQ(z,d) proof or
Kira sector-local master retention, and cannot promote Stage-2.

No Kira/FireFly, no output writes, no use of sec202a Kira DB encoding.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import stat
import time
from pathlib import Path

from examples import three_loop_vp05_sector202_source_split_audit as split
from examples import three_loop_vp05_sector202_target_exact_reduction as exact
from examples import three_loop_vp05_sector202_reuse_audit as reuse
from examples import three_loop_vp05_sector202_quotient_sensitivity as previous
from examples.three_loop_sector203_ffrank_audit import coefficient
from examples.three_loop_sector203_weight_audit import ROOT, load_codec

TAG = "VP05_SECTOR202_A_MODULAR_HOLDOUT "
SOURCE = exact.SOURCE
MAX_DECOMPRESSED = 256 * 1024 * 1024
MAX_TOTAL_CELLS = 1200000
MAX_FILL = 20000
MAX_STEPS = 20000
MAX_SECONDS = 900
POINTS = exact.POINTS


def add(cur: dict, pivot: dict, factor: int, p: int) -> None:
    for k, v in pivot.items():
        updated = (cur.get(k, 0) - factor * v) % p
        if updated:
            cur[k] = updated
        else:
            cur.pop(k, None)


def forward(row: dict, pivots: dict, p: int, max_fill: int,
            max_steps: int, deadline: float) -> tuple[dict, int, str]:
    """Numerical sparse forward reduction, with strict fill/step/time caps."""
    cur = dict(row)
    steps = 0
    while cur:
        if len(cur) > max_fill:
            return cur, steps, "FILL_CAP"
        if steps >= max_steps:
            return cur, steps, "STEP_CAP"
        if time.monotonic() >= deadline:
            return cur, steps, "TIME_CAP"
        lead = min(cur)
        if lead not in pivots:
            return cur, steps, "UNRESOLVED_LEAD"
        add(cur, pivots[lead], cur[lead], p)
        steps += 1
    return cur, steps, "ZERO_REMAINDER"


def insert(row: dict, pivots: dict, p: int, max_fill: int,
           max_steps: int, deadline: float) -> tuple[bool, str, int]:
    cur, steps, status = forward(row, pivots, p, max_fill, max_steps, deadline)
    if status == "UNRESOLVED_LEAD":
        lead = min(cur)
        inv = pow(cur[lead], -1, p)
        normalized = {k: (v * inv) % p for k, v in cur.items()}
        if normalized[lead] != 1:
            raise AssertionError("Pivot normalization failed")
        pivots[lead] = normalized
        return True, "PIVOT_ADDED", steps
    return False, status, steps


def row_at_point(terms: list, p: int, z: int, d: int) -> dict:
    cur = {}
    for item in terms:
        key = tuple(item["key"])
        if len(key) != 2 or any(type(x) is not int for x in key):
            raise RuntimeError("Malformed original Kira integral weight key")
        value = coefficient(item["coefficient"], z, d, p)
        updated = (cur.get(key, 0) + value) % p
        if updated:
            cur[key] = updated
        else:
            cur.pop(key, None)
    return cur


def target_at_point(codec, point: tuple[int, int, int]) -> dict:
    p, z, d = point
    encoded = []
    for powers in previous.TARGETS:
        key = (codec.encode(powers), 139)
        if tuple(codec.decode(key[0])) != powers:
            raise RuntimeError("Original Kira codec roundtrip changed")
        encoded.append(key)
    a = coefficient(exact.FORMULAS[0], z, d, p)
    b = coefficient(exact.FORMULAS[1], z, d, p)
    target = {encoded[0]: 1}
    add(target, {encoded[2]: a}, 1, p)
    add(target, {(4, 73): b}, 1, p)
    return target


def validate_selection(report: dict) -> list[int]:
    if (report.get("status") != "VP05_SECTOR202_A_EXACT_SOURCE_REVIEW_REQUIRED"
        or report.get("original_restricted_kira_source_context", {}).get(
            "source_to_new_r7s5d3_scope_equivalence_proven") is not False
        or report.get("sector202_all_three_masters_verified") is not False):
        raise RuntimeError("Protected source-split evidence no longer matches")
    support = report["original_modular_support"]
    a = support["target_a"]["source_row_ids"]
    b = support["target_b"]["source_row_ids"]
    if (len(a) != 339 or len(b) != 389
        or len(a) != len(set(a)) or len(b) != len(set(b))
        or not set(a).issubset(b)
        or support["A_only_count"] != 0
        or support["intersection_count"] != 339
        or support["union_count"] != 389
        or report["step93_exact_b"]["exact_B_support_equal_to_modular_B_support"] is not True):
        raise RuntimeError("Unexpected A-subset-B source support evidence")
    return sorted(a)


def original_rows(ids: list[int]) -> dict[int, list]:
    """Read only the exported source bundle; refuse unexpected bytes and format."""
    manifest = split.read_pinned(
        split.FORMAL_MANIFEST, split.gap.EXPECTED_MANIFEST_SHA256)
    sha = manifest["source_and_evidence_sha256"]["original_source_rows.json.gz"]
    if not stat.S_ISREG(SOURCE.lstat().st_mode):
        raise RuntimeError("Original source gzip is absent, linked or not regular")
    if reuse.sha256_regular(SOURCE) != sha:
        raise RuntimeError("Original source gzip differs from Step93 pinned SHA")
    with gzip.open(SOURCE, "rb") as stream:
        raw = stream.read(MAX_DECOMPRESSED + 1)
    if len(raw) > MAX_DECOMPRESSED:
        raise RuntimeError("Original source expansion exceeds safety cap")
    bundle = json.loads(raw)
    if (bundle.get("status") != "ORIGINAL_EXACT_SOURCE_ROWS_EXPORTED"
        or bundle.get("saved_equation_count") != 2678
        or bundle.get("selected_equation_count") != 2241
        or len(bundle.get("rows", [])) != 2241):
        raise RuntimeError("Unexpected original exact source bundle")
    rows = {}
    for record in bundle["rows"]:
        idx = record.get("global_zero_based")
        if type(idx) is not int or idx in rows or not isinstance(record.get("terms"), list):
            raise RuntimeError("Malformed/duplicate source row ID")
        if idx in ids:
            rows[idx] = record["terms"]
    if set(rows) != set(ids):
        raise RuntimeError("A-support row missing from protected source bundle")
    return rows


def evaluate(*, point: tuple[int, int, int], ids: list[int], rows: dict,
             codec, max_fill: int, max_steps: int,
             max_seconds: int, max_total_cells: int) -> dict:
    p, z, d = point
    deadline = time.monotonic() + max_seconds
    pivots: dict = {}
    status = "A_MODULAR_HOLDOUT_REVIEW_REQUIRED"
    phase = "source_rank"
    processed = 0
    total_ops = 0
    cells = 0
    cap = None
    for rid in ids:
        if time.monotonic() >= deadline:
            cap = "TIME_CAP"
            break
        try:
            row = row_at_point(rows[rid], p, z, d)
        except (ValueError, ZeroDivisionError) as exc:
            cap = "SINGULAR_SOURCE_COEFFICIENT: " + str(exc)[:100]
            break
        new, code, steps = insert(row, pivots, p, max_fill, max_steps, deadline)
        total_ops += steps
        processed += 1
        if code not in ("PIVOT_ADDED", "ZERO_REMAINDER"):
            cap = code
            break
        if new:
            cells += len(pivots[min(set(pivots) - set(list(pivots)[:-1]))]) if False else 0
            # Total cells are recomputed to avoid a hidden assumption about
            # pivot dictionary key iteration order across codec versions.
            cells = sum(len(row) for row in pivots.values())
            if cells > max_total_cells:
                cap = "TOTAL_CELLS_CAP"
                break
    result = {
        "status": status, "phase": phase, "point": list(point),
        "requested_source_rows": len(ids), "processed_source_rows": processed,
        "basis_rank": len(pivots), "total_stored_pivot_cells": cells,
        "elimination_steps": total_ops,
        "stopped_by_cap": cap, "target_remainder_terms": None,
        "target_remainder_first_key": None,
        "source_rowspan_includes_candidate_A": False,
        "original_qq_z_d_identity_proven": False,
    }
    if cap is not None or processed != len(ids):
        return result
    try:
        target = target_at_point(codec, point)
        rem, steps, final = forward(target, pivots, p, max_fill,
                                     max_steps, deadline)
    except (ValueError, ZeroDivisionError) as exc:
        result["stopped_by_cap"] = "SINGULAR_TARGET: " + str(exc)[:100]
        return result
    result["phase"] = "candidate_A_reduction"
    result["elimination_steps"] += steps
    result["target_remainder_terms"] = len(rem)
    result["target_remainder_first_key"] = list(min(rem)) if rem else None
    result["target_reduction_status"] = final
    result["source_rowspan_includes_candidate_A"] = final == "ZERO_REMAINDER"
    result["status"] = (
        "A_MODULAR_HOLDOUT_SAVED_SOURCE_SPAN_PASS_NOT_EXACT_PROOF"
        if final == "ZERO_REMAINDER" else
        "A_MODULAR_HOLDOUT_SAVED_SOURCE_SPAN_GAP"
        if final == "UNRESOLVED_LEAD" else
        "A_MODULAR_HOLDOUT_REVIEW_REQUIRED")
    if final not in ("ZERO_REMAINDER", "UNRESOLVED_LEAD"):
        result["stopped_by_cap"] = final
    return result


def inspect(point_index: int = 1, *, max_fill: int = MAX_FILL,
            max_steps: int = MAX_STEPS, max_seconds: int = MAX_SECONDS,
            max_total_cells: int = MAX_TOTAL_CELLS) -> dict:
    if point_index not in (0, 1, 2):
        raise ValueError("Only three pinned finite-field points are allowed")
    if min(max_fill, max_steps, max_seconds, max_total_cells) < 1:
        raise ValueError("Caps must be positive")
    split_report = split.inspect()
    ids = validate_selection(split_report)
    rows = original_rows(ids)
    codec_module = load_codec((ROOT / "output/tools/pyred_weight.py").resolve())
    bits, ordering = codec_module.from_kiradb(str(previous.P / "results/kira.db"))
    if ordering != 5:
        raise RuntimeError("Original source-project Kira integral ordering changed")
    codec = codec_module.WeightCodec(np=12, bits=bits, iord=ordering, topsectors=[203])
    result = evaluate(point=POINTS[point_index], ids=ids, rows=rows,
                      codec=codec, max_fill=max_fill, max_steps=max_steps,
                      max_seconds=max_seconds, max_total_cells=max_total_cells)
    result.update({
        "family": "VP05_full", "sector": 202, "target": "A",
        "original_source_rows_available": 2241, "A_original_source_rows_selected": len(ids),
        "point_index": point_index,
        "max_seconds": max_seconds, "max_fill": max_fill, "max_steps": max_steps,
        "max_total_cells": max_total_cells,
        "source_codec_provenance": "original provisional sector203 Kira DB, ordering=5",
        "new_r7s5d3_local_master_retention_proven": False,
        "global_63_master_closure_proven": False,
        "files_modified": False, "kira_executed": False, "original_exact_source_protected": True})
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--point-index", type=int, choices=(0, 1, 2), default=1)
    parser.add_argument("--max-seconds", type=int, default=MAX_SECONDS)
    parser.add_argument("--max-fill", type=int, default=MAX_FILL)
    parser.add_argument("--max-steps", type=int, default=MAX_STEPS)
    parser.add_argument("--max-total-cells", type=int, default=MAX_TOTAL_CELLS)
    args = parser.parse_args()
    print(TAG + json.dumps(inspect(args.point_index, max_fill=args.max_fill,
                                   max_steps=args.max_steps, max_seconds=args.max_seconds,
                                   max_total_cells=args.max_total_cells),
                           ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
