"""Rewrite saved Q01 finite-q on-shell scalar output to the external basis (p,q)."""
from __future__ import annotations

import json
from pathlib import Path
import re
import time

import sympy as sp

from three_loop import rewrite_to_pq_external_basis


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "output" / "3loop_q01_projected_scalar_onshell.txt"
OUTPUT = ROOT / "output" / "3loop_q01_projected_scalar_pq.txt"
SUMMARY = ROOT / "output" / "3loop_q01_projected_scalar_pq_summary.json"


def _protect_scalar_product_atoms(text: str):
    sp_names = sorted(
        set(re.findall(r"SP__[A-Za-z0-9']+__[A-Za-z0-9']+", text)),
        key=len,
        reverse=True,
    )
    safe_text = text
    safe_to_original = {}
    local_dict = {"D": sp.Symbol("D"), "m": sp.Symbol("m"), "z": sp.Symbol("z")}
    for i, name in enumerate(sp_names):
        safe = f"SPATOM_{i}"
        safe_text = safe_text.replace(name, safe)
        safe_symbol = sp.Symbol(safe)
        safe_to_original[safe_symbol] = sp.Symbol(name)
        local_dict[safe] = safe_symbol
    return safe_text, local_dict, safe_to_original


def _split_top_level_add_terms(text: str) -> list[str]:
    terms = []
    depth = 0
    start = 0
    for i, ch in enumerate(text):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth < 0:
                raise ValueError("unbalanced parentheses")
        elif depth == 0 and ch in "+-" and i > start:
            terms.append(text[start:i].strip())
            start = i
    tail = text[start:].strip()
    if tail:
        terms.append(tail)
    if depth != 0:
        raise ValueError("unbalanced parentheses")
    return [term for term in terms if term]


def _parse_terms(text: str):
    safe_text, local_dict, safe_to_original = _protect_scalar_product_atoms(text)
    for raw in _split_top_level_add_terms(safe_text):
        parsed = sp.sympify(raw, locals=local_dict, evaluate=False)
        yield parsed.xreplace(safe_to_original)


def _atoms(terms) -> tuple[str, ...]:
    out = set()
    for term in terms:
        out.update(str(s) for s in term.free_symbols if str(s).startswith("SP__"))
    return tuple(sorted(out))


def main() -> int:
    print("QEDCalc Q01 finite-q p-q external-basis reduction")
    if not INPUT.exists():
        print(f"missing input: {INPUT}")
        print("Run run_three_loop_q01_onshell_reduce.bat first.")
        return 1

    text = INPUT.read_text(encoding="utf-8")
    t0 = time.perf_counter()
    parsed_terms = list(_parse_terms(text))
    parse_seconds = time.perf_counter() - t0

    before_atoms = _atoms(parsed_terms)
    t1 = time.perf_counter()
    reduced_terms = [rewrite_to_pq_external_basis(term).expression for term in parsed_terms]
    reduce_seconds = time.perf_counter() - t1
    after_atoms = _atoms(reduced_terms)

    OUTPUT.write_text(" + ".join(str(term) for term in reduced_terms), encoding="utf-8")
    removed = sorted(set(before_atoms) - set(after_atoms))
    added = sorted(set(after_atoms) - set(before_atoms))
    payload = {
        "diagram_id": "Q01",
        "input": str(INPUT.relative_to(ROOT)),
        "output": str(OUTPUT.relative_to(ROOT)),
        "elapsed_parse_seconds": parse_seconds,
        "elapsed_basis_seconds": reduce_seconds,
        "top_level_term_count": len(parsed_terms),
        "before_scalar_product_atom_count": len(before_atoms),
        "after_scalar_product_atom_count": len(after_atoms),
        "removed_atoms": removed,
        "added_atoms": added,
        "after_scalar_product_atoms": list(after_atoms),
        "contains_pprime_atoms": any("p'" in name for name in after_atoms),
        "has_D": any(sp.Symbol("D") in term.free_symbols for term in reduced_terms),
        "has_z": any(sp.Symbol("z") in term.free_symbols for term in reduced_terms),
        "q_zero_taken": False,
    }
    SUMMARY.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"parse saved on-shell scalar trace: {parse_seconds:.3f} s")
    print(f"top-level terms: {len(parsed_terms)}")
    print(f"p-q basis reduction: {reduce_seconds:.3f} s")
    print(f"scalar-product atoms: {len(before_atoms)} -> {len(after_atoms)}")
    print("removed:", ", ".join(removed))
    print("added:", ", ".join(added))
    print(f"generated: {OUTPUT}")
    print(f"generated: {SUMMARY}")
    print("Q01 finite-q p-q external-basis reduction PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
