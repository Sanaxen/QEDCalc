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


def _protect_scalar_product_atoms(text: str):
    sp_names = sorted(
        set(re.findall(r"SP__[A-Za-z0-9']+__[A-Za-z0-9']+", text)),
        key=len,
        reverse=True,
    )
    safe_text = text
    safe_to_original = {}
    local_dict = {
        "D": sp.Symbol("D"),
        "m": sp.Symbol("m"),
        "z": sp.Symbol("z"),
    }
    for i, name in enumerate(sp_names):
        safe = f"SPATOM_{i}"
        safe_text = safe_text.replace(name, safe)
        safe_symbol = sp.Symbol(safe)
        safe_to_original[safe_symbol] = sp.Symbol(name)
        local_dict[safe] = safe_symbol
    return safe_text, local_dict, safe_to_original


def _split_top_level_add_terms(text: str) -> list[str]:
    """Split one huge scalar expression at top-level + and - operators.

    The saved Q01 expression is a flat sum of rational monomials. Parsing each
    top-level term independently avoids Python AST recursion limits while
    preserving the exact algebraic sum.
    """
    terms = []
    depth = 0
    start = 0
    for i, ch in enumerate(text):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth < 0:
                raise ValueError("unbalanced parentheses in saved scalar expression")
        elif depth == 0 and ch in "+-" and i > start:
            terms.append(text[start:i].strip())
            start = i
    tail = text[start:].strip()
    if tail:
        terms.append(tail)
    if depth != 0:
        raise ValueError("unbalanced parentheses in saved scalar expression")
    return [term for term in terms if term]


def _parse_saved_expression_terms(text: str):
    """Yield restored SymPy terms without constructing one giant parser AST."""
    safe_text, local_dict, safe_to_original = _protect_scalar_product_atoms(text)
    raw_terms = _split_top_level_add_terms(safe_text)
    for raw in raw_terms:
        parsed = sp.sympify(raw, locals=local_dict, evaluate=False)
        yield parsed.xreplace(safe_to_original)


def _scalar_product_atoms_from_terms(terms) -> tuple[str, ...]:
    atoms = set()
    for term in terms:
        atoms.update(
            str(symbol)
            for symbol in term.free_symbols
            if str(symbol).startswith("SP__")
        )
    return tuple(sorted(atoms))


def main() -> int:
    print("QEDCalc Q01 finite-q on-shell scalar reduction")
    if not INPUT.exists():
        print(f"missing input: {INPUT}")
        print("Run run_three_loop_q01_scalar_trace.bat first.")
        return 1

    text = INPUT.read_text(encoding="utf-8")

    t0 = time.perf_counter()
    parsed_terms = list(_parse_saved_expression_terms(text))
    parse_seconds = time.perf_counter() - t0

    before_atoms = _scalar_product_atoms_from_terms(parsed_terms)
    before_ops = sum(int(sp.count_ops(term)) for term in parsed_terms) + max(0, len(parsed_terms) - 1)

    t1 = time.perf_counter()
    reduced_terms = []
    for term in parsed_terms:
        reduced_terms.append(apply_finite_q_onshell(term).expression)
    reduce_seconds = time.perf_counter() - t1

    after_atoms = _scalar_product_atoms_from_terms(reduced_terms)
    after_ops = sum(int(sp.count_ops(term)) for term in reduced_terms) + max(0, len(reduced_terms) - 1)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(" + ".join(str(term) for term in reduced_terms), encoding="utf-8")

    removed = sorted(set(before_atoms) - set(after_atoms))
    payload = {
        "diagram_id": "Q01",
        "input": str(INPUT.relative_to(ROOT)),
        "output": str(OUTPUT.relative_to(ROOT)),
        "elapsed_parse_seconds": parse_seconds,
        "elapsed_onshell_seconds": reduce_seconds,
        "top_level_term_count": len(parsed_terms),
        "before_operation_count": before_ops,
        "after_operation_count": after_ops,
        "before_scalar_product_atom_count": len(before_atoms),
        "after_scalar_product_atom_count": len(after_atoms),
        "removed_external_atoms": removed,
        "after_scalar_product_atoms": list(after_atoms),
        "has_D": any(sp.Symbol("D") in term.free_symbols for term in reduced_terms),
        "has_z": any(sp.Symbol("z") in term.free_symbols for term in reduced_terms),
        "q_zero_taken": False,
    }
    SUMMARY.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"parse saved scalar trace: {parse_seconds:.3f} s")
    print(f"top-level terms: {len(parsed_terms)}")
    print(f"finite-q on-shell reduction: {reduce_seconds:.3f} s")
    print(f"operation count: {before_ops} -> {after_ops}")
    print(f"scalar-product atoms: {len(before_atoms)} -> {len(after_atoms)}")
    print("removed:", ", ".join(removed))
    print(f"generated: {OUTPUT}")
    print(f"generated: {SUMMARY}")
    print("Q01 finite-q on-shell scalar reduction PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
