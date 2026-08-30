"""Apply exact finite-q on-shell kinematics to the saved Q01 scalar trace.

This is a post-processing step: it reuses output/3loop_q01_projected_scalar.txt
and therefore does not repeat the expensive D-dimensional Clifford trace.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import time

import sympy as sp

from three_loop import apply_finite_q_onshell


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "output" / "3loop_q01_projected_scalar.txt"
OUTPUT = ROOT / "output" / "3loop_q01_projected_scalar_onshell.txt"
SUMMARY = ROOT / "output" / "3loop_q01_projected_scalar_onshell_summary.json"


def _parse_saved_expression(text: str) -> sp.Expr:
    """Parse saved scalar expressions whose Symbol names may contain apostrophes.

    Python/SymPy's textual parser cannot directly read identifiers such as
    ``SP__p'__p'``.  Replace every scalar-product atom by a parser-safe token,
    parse that expression, then restore the exact original Symbol objects.
    """
    sp_names = sorted(
        set(re.findall(r"SP__[A-Za-z0-9']+__[A-Za-z0-9']+", text)),
        key=len,
        reverse=True,
    )
    safe_text = text
    safe_to_original = {}
    for i, name in enumerate(sp_names):
        safe = f"SPATOM_{i}"
        safe_text = safe_text.replace(name, safe)
        safe_to_original[sp.Symbol(safe)] = sp.Symbol(name)

    local_dict = {
        "D": sp.Symbol("D"),
        "m": sp.Symbol("m"),
        "z": sp.Symbol("z"),
    }
    local_dict.update({str(s): s for s in safe_to_original})
    parsed = sp.sympify(safe_text, locals=local_dict, evaluate=False)
    return parsed.xreplace(safe_to_original)


def main() -> int:
    print("QEDCalc Q01 finite-q on-shell scalar reduction")
    if not INPUT.exists():
        print(f"missing input: {INPUT}")
        print("Run run_three_loop_q01_scalar_trace.bat first.")
        return 1

    text = INPUT.read_text(encoding="utf-8")

    t0 = time.perf_counter()
    expr = _parse_saved_expression(text)
    parse_seconds = time.perf_counter() - t0

    t1 = time.perf_counter()
    reduced = apply_finite_q_onshell(expr)
    reduce_seconds = time.perf_counter() - t1

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(str(reduced.expression), encoding="utf-8")

    removed = sorted(
        set(reduced.before_scalar_product_atoms)
        - set(reduced.after_scalar_product_atoms)
    )
    payload = {
        "diagram_id": "Q01",
        "input": str(INPUT.relative_to(ROOT)),
        "output": str(OUTPUT.relative_to(ROOT)),
        "elapsed_parse_seconds": parse_seconds,
        "elapsed_onshell_seconds": reduce_seconds,
        "before_operation_count": reduced.before_operation_count,
        "after_operation_count": reduced.after_operation_count,
        "before_scalar_product_atom_count": len(reduced.before_scalar_product_atoms),
        "after_scalar_product_atom_count": len(reduced.after_scalar_product_atoms),
        "removed_external_atoms": removed,
        "after_scalar_product_atoms": list(reduced.after_scalar_product_atoms),
        "has_D": sp.Symbol("D") in reduced.expression.free_symbols,
        "has_z": sp.Symbol("z") in reduced.expression.free_symbols,
        "q_zero_taken": False,
    }
    SUMMARY.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"parse saved scalar trace: {parse_seconds:.3f} s")
    print(f"finite-q on-shell reduction: {reduce_seconds:.3f} s")
    print(
        "operation count: "
        f"{reduced.before_operation_count} -> {reduced.after_operation_count}"
    )
    print(
        "scalar-product atoms: "
        f"{len(reduced.before_scalar_product_atoms)} -> "
        f"{len(reduced.after_scalar_product_atoms)}"
    )
    print("removed:", ", ".join(removed))
    print(f"generated: {OUTPUT}")
    print(f"generated: {SUMMARY}")
    print("Q01 finite-q on-shell scalar reduction PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
