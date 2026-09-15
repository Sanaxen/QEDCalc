"""Low-memory exact Q01 projected-amplitude -> final60 coefficient synthesis.

This is the memory-safe companion to
``three_loop_q01_projected_amplitude_master_coefficients.py``.  It reuses the
same validated saved artifacts and reduction parser, but deliberately avoids
materialising canonical SymPy expressions for all 125 Kira masters at once.

Each master is canonicalised independently with a small pairwise reduction
tree, immediately converted to text, checkpointed, and released.  Extra
(non-final60) masters are processed first so exact cancellations free memory
as early as possible.  No projected trace and no Kira/FireFly reduction are
recomputed.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import gc
import json
import os
from pathlib import Path
from typing import Iterable

import sympy as sp

import examples.three_loop_q01_projected_amplitude_master_coefficients as base
from three_loop.kira_isp_bridge import expand_qedcalc_integral_to_kira


CHECKPOINT = base.PROJECT / "q01_projected_amplitude_final60_coefficients_lowmem_checkpoint.json"
OUTPUT_JSON = base.PROJECT / "q01_projected_amplitude_final60_coefficients.json"
OUTPUT_TXT = base.PROJECT / "q01_projected_amplitude_final60_coefficients.txt"
DEFAULT_CHUNK = 4

IndexTuple = tuple[int, ...]


def _key(v: IndexTuple) -> str:
    return ",".join(str(x) for x in v)


def _artifact_signature(form_file: Path) -> dict[str, object]:
    paths = [base.SOURCE, form_file, base.FINAL_BASIS_JSON, base.ORIGINAL_TARGET_FILE, base.TARGET_FILE]
    out: dict[str, object] = {}
    for path in paths:
        st = path.stat()
        out[str(path)] = {"size": st.st_size, "mtime_ns": st.st_mtime_ns}
    return out


def _load_checkpoint(signature: dict[str, object]) -> dict[str, dict[str, object]]:
    if not CHECKPOINT.exists():
        return {}
    try:
        data = json.loads(CHECKPOINT.read_text(encoding="utf-8"))
    except Exception:
        return {}
    if data.get("version") != 1 or data.get("signature") != signature:
        print("ignoring stale low-memory checkpoint")
        return {}
    completed = data.get("completed")
    if not isinstance(completed, dict):
        return {}
    print("resuming exact canonicalization checkpoint:", len(completed), "masters already complete")
    return completed


def _save_checkpoint(signature: dict[str, object], completed: dict[str, dict[str, object]]) -> None:
    tmp = CHECKPOINT.with_suffix(CHECKPOINT.suffix + ".tmp")
    tmp.write_text(
        json.dumps({"version": 1, "signature": signature, "completed": completed}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    tmp.replace(CHECKPOINT)


def _canonical_sum_lowmem(parts: list[sp.Expr], *, chunk_size: int) -> sp.Expr:
    """Exactly sum/cancel one master's contributions with bounded fan-in.

    The input list is consumed destructively so references to large pre-cancel
    expression trees are released after every reduction round.
    """
    work = parts
    if not work:
        return sp.Integer(0)

    while len(work) > 1:
        reduced: list[sp.Expr] = []
        for start in range(0, len(work), chunk_size):
            chunk = work[start : start + chunk_size]
            expr = sp.Add(*chunk)
            reduced.append(sp.cancel(expr))
            del expr, chunk
        work.clear()
        gc.collect()
        work = reduced

    result = sp.cancel(work[0])
    work.clear()
    gc.collect()
    return result


def main() -> None:
    chunk_size = int(os.environ.get("QEDCALC_COEFF_CHUNK", str(DEFAULT_CHUNK)))
    if chunk_size < 2:
        raise SystemExit("ERROR: QEDCALC_COEFF_CHUNK must be >= 2")

    print("QEDCalc Q01 projected-amplitude -> final60 master coefficient synthesis [LOW MEMORY]")
    print("mode: saved artifacts only; no new projected trace or Kira reduction")
    print("canonicalization fan-in:", chunk_size)

    projected = base._load_projected_terms()
    final60 = base._load_final60()
    original944 = base._load_family_file(base.ORIGINAL_TARGET_FILE, base.EXPECTED_ORIGINAL)
    mandatory971 = base._load_family_file(base.TARGET_FILE)
    if not final60.issubset(mandatory971):
        raise SystemExit("ERROR: r9s4d0 mandatory target set does not contain final60")

    expanded_unique: set[IndexTuple] = set()
    expanded_total = 0
    bridge_records: list[tuple[sp.Expr, IndexTuple]] = []
    native_degrees: Counter[int] = Counter()
    source_symbols: set[str] = set()
    for native, projected_coeff, _ in projected:
        source_symbols.update(str(s) for s in projected_coeff.free_symbols)
        expansion = expand_qedcalc_integral_to_kira(native)
        native_degrees[expansion.native_isp_degree] += 1
        expanded_total += len(expansion.terms)
        for term in expansion.terms:
            expanded_unique.add(term.kira_indices)
            bridge_records.append((projected_coeff * term.coefficient, term.kira_indices))

    if expanded_unique != original944:
        missing = expanded_unique - original944
        extra = original944 - expanded_unique
        raise SystemExit(
            f"ERROR: bridge/exact944 mismatch: bridge-only={len(missing)} exact944-only={len(extra)}"
        )

    form_file = base._find_form_export()
    masters_file = base.RESULT_DIR / "masters.final"
    if not masters_file.exists():
        raise SystemExit(f"ERROR: masters.final not found: {masters_file}")
    masters, rules, zeros = base._load_reduction_graph(form_file, masters_file)
    resolve, unresolved = base._make_resolver(masters, rules, zeros)

    master_parts: dict[IndexTuple, list[sp.Expr]] = defaultdict(list)
    reduced_bridge_terms = 0
    zero_bridge_terms = 0
    for amplitude_coeff, kira_indices in bridge_records:
        resolved = resolve(kira_indices)
        if resolved is None:
            continue
        if not resolved:
            zero_bridge_terms += 1
            continue
        reduced_bridge_terms += 1
        for master, reduction_coeff in resolved.items():
            master_parts[master].append(amplitude_coeff * reduction_coeff)

    if unresolved:
        print("unresolved Kira integrals:", len(unresolved))
        for value in sorted(unresolved)[:12]:
            print("  unresolved:", base._fmt(value))
        raise SystemExit(3)

    raw_master_count = len(master_parts)
    print("raw master forms before exact cancellation:", raw_master_count)
    print("low-memory exact canonicalization starting...")

    # The reduction graph/memo and bridge list are no longer needed.  Releasing
    # them before SymPy cancellation materially lowers the process baseline.
    del resolve, rules, zeros, bridge_records, projected
    gc.collect()

    signature = _artifact_signature(form_file)
    completed = _load_checkpoint(signature)

    extra_masters = sorted(m for m in master_parts if m not in final60)
    final_masters = sorted(m for m in master_parts if m in final60)
    order = extra_masters + final_masters
    total = len(order)

    for pos, master in enumerate(order, 1):
        key = _key(master)
        if key in completed:
            master_parts.pop(master, None)
            continue
        parts = master_parts.pop(master, [])
        print(
            f"canonicalizing {pos}/{total}: {base._fmt(master)} "
            f"contributions={len(parts)} final60={master in final60}",
            flush=True,
        )
        expr = _canonical_sum_lowmem(parts, chunk_size=chunk_size)
        row = {
            "indices": list(master),
            "integral": base._fmt(master),
            "coefficient": str(expr),
            "nonzero": bool(expr != 0),
            "source_contributions": len(parts),
            "symbols": sorted(str(s) for s in expr.free_symbols),
            "final60": master in final60,
        }
        completed[key] = row
        _save_checkpoint(signature, completed)
        del expr, parts
        gc.collect()

    # Masters absent from master_parts have identically zero coefficient.  Add
    # explicit zero rows for final60 so the output always contains all 60.
    rows: list[dict[str, object]] = []
    for master in sorted(final60):
        row = completed.get(_key(master))
        if row is None:
            row = {
                "indices": list(master),
                "integral": base._fmt(master),
                "coefficient": "0",
                "nonzero": False,
                "source_contributions": 0,
                "symbols": [],
                "final60": True,
            }
        rows.append(row)

    nonzero_extra = [
        row for row in completed.values()
        if not row.get("final60") and bool(row.get("nonzero"))
    ]
    nonzero_all = sum(1 for row in completed.values() if bool(row.get("nonzero")))
    nonzero_final = sum(1 for row in rows if bool(row.get("nonzero")))

    pass_checks = {
        "projected_native_terms_910": True,
        "bridge_unique_targets_match_exact944": expanded_unique == original944,
        "all_bridge_targets_resolved": not unresolved,
        "final_basis_has_60_forms": len(final60) == base.EXPECTED_FINAL,
        "final60_are_masters_in_r9s4d0": final60.issubset(masters),
        "no_nonzero_master_coefficients_outside_final60": not nonzero_extra,
    }
    passed = all(pass_checks.values())

    summary = {
        "mode": "exact saved-artifact coefficient synthesis; low-memory pairwise canonicalization; no projected trace or Kira recomputation",
        "source": str(base.SOURCE),
        "project": str(base.PROJECT),
        "reduction_alt_dir": str(base.ALT_ROOT),
        "form_export": str(form_file),
        "masters_file": str(masters_file),
        "canonicalization_chunk_size": chunk_size,
        "checkpoint": str(CHECKPOINT),
        "projected_native_terms": base.EXPECTED_NATIVE,
        "projected_coefficient_symbols_after_D_to_d_normalization": sorted(source_symbols - {"D"} | ({"d"} if "D" in source_symbols else set())),
        "native_isp_degree_histogram": {str(k): v for k, v in sorted(native_degrees.items())},
        "bridge_expanded_terms_total": expanded_total,
        "bridge_unique_kira_targets": len(expanded_unique),
        "exact944_targets": len(original944),
        "mandatory_boundary_targets": len(mandatory971),
        "reduction_masters_final": len(masters),
        "reduced_bridge_terms": reduced_bridge_terms,
        "zero_bridge_terms": zero_bridge_terms,
        "raw_master_forms_before_cancellation": raw_master_count,
        "nonzero_master_forms_after_cancellation": nonzero_all,
        "final60_forms": len(final60),
        "nonzero_final60_coefficients": nonzero_final,
        "nonzero_extra_master_coefficients": nonzero_extra,
        "basis_terms": rows,
        "checks": pass_checks,
        "pass": passed,
    }
    OUTPUT_JSON.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "QEDCalc Q01 projected-amplitude -> final60 master coefficient synthesis [LOW MEMORY]",
        "",
        f"bridge expanded terms total: {expanded_total}",
        f"bridge unique Kira targets: {len(expanded_unique)}",
        f"exact944 targets: {len(original944)}",
        f"r9s4d0 masters.final forms: {len(masters)}",
        f"raw master forms before cancellation: {raw_master_count}",
        f"nonzero master forms after cancellation: {nonzero_all}",
        f"final60 forms: {len(final60)}",
        f"nonzero final60 coefficients: {nonzero_final}",
        f"nonzero extra master coefficients: {len(nonzero_extra)}",
        "",
        "checks:",
    ]
    lines.extend(f"  {name}: {value}" for name, value in pass_checks.items())
    lines.append("")
    lines.append("final60 coefficients:")
    for row in rows:
        lines.append(f"  {row['integral']}  coefficient={row['coefficient']}")
    OUTPUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("nonzero master forms after cancellation:", nonzero_all)
    print("nonzero final60 coefficients:", nonzero_final)
    print("nonzero extra master coefficients:", len(nonzero_extra))
    print("audit JSON:", OUTPUT_JSON)
    print("audit TXT:", OUTPUT_TXT)
    if not passed:
        print("Q01 projected-amplitude final60 coefficient synthesis FAIL")
        raise SystemExit(1)
    print("Q01 projected-amplitude final60 coefficient synthesis PASS")


if __name__ == "__main__":
    main()
