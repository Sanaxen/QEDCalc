"""Exact Q01 projected-amplitude -> final60 coefficient synthesis with Fermat.

This is the external-CAS companion to the low-memory SymPy implementation.
It consumes only already-saved projected-amplitude and Kira/FireFly artifacts.
No projected trace and no Kira reduction are recomputed.

The important difference is that exact rational-function cancellation is handed
to the native Fermat executable in WSL.  Existing completed rows from the
low-memory SymPy checkpoint are imported, so an interrupted low-memory run can
resume at the first unfinished master instead of repeating completed work.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import gc
import json
import os
from pathlib import Path
import subprocess
from typing import Iterable

import sympy as sp

import examples.three_loop_q01_projected_amplitude_master_coefficients as base
import examples.three_loop_q01_projected_amplitude_master_coefficients_lowmem as lowmem
from three_loop.kira_isp_bridge import expand_qedcalc_integral_to_kira


CHECKPOINT = base.PROJECT / "q01_projected_amplitude_final60_coefficients_fermat_checkpoint.json"
OUTPUT_JSON = base.PROJECT / "q01_projected_amplitude_final60_coefficients.json"
OUTPUT_TXT = base.PROJECT / "q01_projected_amplitude_final60_coefficients.txt"
FERMAT_INPUT = base.PROJECT / "q01_coeff_fermat.in"
FERMAT_OUTPUT = base.PROJECT / "q01_coeff_fermat.out"
FERMAT_STDOUT = base.PROJECT / "q01_coeff_fermat.stdout.log"
DEFAULT_GROUP = 128

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


def _load_json_checkpoint(path: Path, signature: dict[str, object]) -> dict[str, dict[str, object]]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    if data.get("version") != 1 or data.get("signature") != signature:
        return {}
    completed = data.get("completed")
    return completed if isinstance(completed, dict) else {}


def _load_checkpoint(signature: dict[str, object]) -> dict[str, dict[str, object]]:
    completed = _load_json_checkpoint(CHECKPOINT, signature)
    if completed:
        print("resuming Fermat checkpoint:", len(completed), "masters already complete")
        return completed

    imported = _load_json_checkpoint(lowmem.CHECKPOINT, signature)
    if imported:
        print("importing low-memory SymPy checkpoint:", len(imported), "masters already complete")
        for row in imported.values():
            if isinstance(row, dict):
                row.setdefault("canonical_backend", "sympy-lowmem")
        return imported
    return {}


def _save_checkpoint(signature: dict[str, object], completed: dict[str, dict[str, object]]) -> None:
    tmp = CHECKPOINT.with_suffix(CHECKPOINT.suffix + ".tmp")
    tmp.write_text(
        json.dumps({"version": 1, "signature": signature, "completed": completed}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    tmp.replace(CHECKPOINT)


def _sympy_to_fermat(expr: sp.Expr) -> str:
    # Fermat accepts explicit * and ^.  Keeping explicit multiplication also
    # makes the generated input unambiguous for multi-character symbol names.
    return sp.sstr(expr).replace("**", "^")


def _clean_fermat_output(text: str) -> str:
    # &U asks Fermat for CAS/Maple-style output.  Preserve operators but remove
    # line wrapping so the coefficient remains one machine-readable string.
    return " ".join(line.strip() for line in text.replace("\r", "").split("\n") if line.strip())


def _is_zero_fermat(text: str) -> bool:
    compact = "".join(text.split())
    while compact.startswith("(") and compact.endswith(")"):
        compact = compact[1:-1]
    return compact == "0"


def _run_fermat_sum(parts: list[str], symbols: set[str]) -> str:
    if not parts:
        return "0"

    for path in (FERMAT_OUTPUT, FERMAT_STDOUT):
        try:
            path.unlink()
        except FileNotFoundError:
            pass

    lines = ["&N;", "&U;"]
    for symbol in sorted(symbols):
        if not symbol.replace("_", "").isalnum() or symbol[0].isdigit():
            raise RuntimeError(f"Fermat backend does not support symbol name safely: {symbol!r}")
        lines.append(f"&(J={symbol});")
    lines.extend(
        [
            f"&(S={FERMAT_OUTPUT.name});",
            "q := " + "+".join(f"({part})" for part in parts) + ";",
            "!(&o,^q);",
            "&(S=@);",
            "&q",
        ]
    )
    FERMAT_INPUT.write_text("\n".join(lines) + "\n", encoding="ascii")

    command = (
        f"$HOME/fermat/Ferl7/fer64 < {FERMAT_INPUT.name} "
        f"> {FERMAT_STDOUT.name} 2>&1"
    )
    proc = subprocess.run(
        ["wsl.exe", "--cd", str(base.PROJECT), "bash", "-lc", command],
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"Fermat failed with exit code {proc.returncode}; see {FERMAT_STDOUT}"
        )
    if not FERMAT_OUTPUT.exists():
        raise RuntimeError(f"Fermat did not create result file: {FERMAT_OUTPUT}")
    result = _clean_fermat_output(FERMAT_OUTPUT.read_text(encoding="utf-8", errors="replace"))
    if not result:
        raise RuntimeError(f"Fermat result file is empty: {FERMAT_OUTPUT}")
    return result


def _canonical_sum_fermat(parts: list[sp.Expr], *, group_size: int) -> tuple[str, set[str]]:
    """Exactly sum/cancel one master's coefficient with bounded Fermat fan-in."""
    if not parts:
        return "0", set()

    symbols: set[str] = set()
    work: list[str] = []
    for expr in parts:
        symbols.update(str(s) for s in expr.free_symbols)
        work.append(_sympy_to_fermat(expr))

    round_no = 0
    while len(work) > 1:
        round_no += 1
        reduced: list[str] = []
        total_groups = (len(work) + group_size - 1) // group_size
        for start in range(0, len(work), group_size):
            group = work[start : start + group_size]
            if len(group) == 1:
                reduced.append(group[0])
                continue
            group_no = start // group_size + 1
            if total_groups > 1:
                print(
                    f"    Fermat round {round_no}: group {group_no}/{total_groups} terms={len(group)}",
                    flush=True,
                )
            reduced.append(_run_fermat_sum(group, symbols))
        work = reduced

    # A single original part still needs canonical Fermat normalization.
    if len(parts) == 1:
        work[0] = _run_fermat_sum(work, symbols)
    return work[0], symbols


def _fermat_self_test() -> None:
    result = _run_fermat_sum(["(d+z)/(d-z)", "(d-z)/(d+z)"], {"d", "z"})
    # Do not depend on Fermat's sign/order formatting.  Feed the difference back
    # to Fermat and require exact zero.
    expected = "2*(d^2+z^2)/(d^2-z^2)"
    check = _run_fermat_sum([result, f"-({expected})"], {"d", "z"})
    if not _is_zero_fermat(check):
        raise RuntimeError(f"Fermat backend self-test mismatch: result={result!r}, difference={check!r}")
    print("Fermat backend self-test: PASS")


def main() -> None:
    group_size = int(os.environ.get("QEDCALC_FERMAT_GROUP", str(DEFAULT_GROUP)))
    if group_size < 2:
        raise SystemExit("ERROR: QEDCALC_FERMAT_GROUP must be >= 2")

    print("QEDCalc Q01 projected-amplitude -> final60 master coefficient synthesis [FERMAT]")
    print("mode: saved artifacts only; no new projected trace or Kira reduction")
    print("Fermat bounded fan-in:", group_size)
    _fermat_self_test()

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
    print("Fermat exact canonicalization starting...")

    del resolve, rules, zeros, bridge_records, projected
    gc.collect()

    signature = _artifact_signature(form_file)
    completed = _load_checkpoint(signature)
    _save_checkpoint(signature, completed)

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
        coeff, symbols = _canonical_sum_fermat(parts, group_size=group_size)
        row = {
            "indices": list(master),
            "integral": base._fmt(master),
            "coefficient": coeff,
            "coefficient_format": "fermat-maple",
            "nonzero": not _is_zero_fermat(coeff),
            "source_contributions": len(parts),
            "symbols": sorted(symbols),
            "final60": master in final60,
            "canonical_backend": "fermat",
        }
        completed[key] = row
        _save_checkpoint(signature, completed)
        del parts
        gc.collect()

    rows: list[dict[str, object]] = []
    for master in sorted(final60):
        row = completed.get(_key(master))
        if row is None:
            row = {
                "indices": list(master),
                "integral": base._fmt(master),
                "coefficient": "0",
                "coefficient_format": "fermat-maple",
                "nonzero": False,
                "source_contributions": 0,
                "symbols": [],
                "final60": True,
                "canonical_backend": "fermat",
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
        "fermat_backend_self_test": True,
    }
    passed = all(pass_checks.values())

    summary = {
        "mode": "exact saved-artifact coefficient synthesis; Fermat rational-function backend; no projected trace or Kira recomputation",
        "source": str(base.SOURCE),
        "project": str(base.PROJECT),
        "reduction_alt_dir": str(base.ALT_ROOT),
        "form_export": str(form_file),
        "masters_file": str(masters_file),
        "fermat_group_size": group_size,
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
        "QEDCalc Q01 projected-amplitude -> final60 master coefficient synthesis [FERMAT]",
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

    for temp in (FERMAT_INPUT, FERMAT_OUTPUT, FERMAT_STDOUT):
        try:
            temp.unlink()
        except FileNotFoundError:
            pass

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
