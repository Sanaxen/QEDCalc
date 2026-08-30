"""Map the saved Q01 finite-q p-q scalar expression to integral indices."""
from __future__ import annotations

import json
from pathlib import Path
import re
import time

import sympy as sp

from three_loop import q01_scalar_numerator_to_integrals


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "output" / "3loop_q01_projected_scalar_pq.txt"
OUTPUT = ROOT / "output" / "3loop_q01_integral_indices.txt"
SUMMARY = ROOT / "output" / "3loop_q01_integral_indices_summary.json"


def _protect_scalar_product_atoms(text: str):
    names = sorted(
        set(re.findall(r"SP__[A-Za-z0-9']+__[A-Za-z0-9']+", text)),
        key=len,
        reverse=True,
    )
    safe_text = text
    safe_to_original = {}
    local_dict = {"D": sp.Symbol("D"), "m": sp.Symbol("m"), "z": sp.Symbol("z")}
    for i, name in enumerate(names):
        safe = f"SPATOM_{i}"
        safe_text = safe_text.replace(name, safe)
        safe_symbol = sp.Symbol(safe)
        safe_to_original[safe_symbol] = sp.Symbol(name)
        local_dict[safe] = safe_symbol
    return safe_text, local_dict, safe_to_original


def _normalize_top_level_signs(text: str) -> str:
    out = []
    i = 0
    depth = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch == "(":
            depth += 1
            out.append(ch)
            i += 1
            continue
        if ch == ")":
            depth -= 1
            out.append(ch)
            i += 1
            continue
        if depth == 0 and ch in "+-":
            sign = 1
            j = i
            saw = False
            while j < n:
                while j < n and text[j].isspace():
                    j += 1
                if j < n and text[j] in "+-":
                    saw = True
                    if text[j] == "-":
                        sign *= -1
                    j += 1
                    continue
                break
            if saw:
                out.append("-" if sign < 0 else "+")
                i = j
                continue
        out.append(ch)
        i += 1
    return "".join(out)


def _split_top_level_terms(text: str) -> list[str]:
    text = _normalize_top_level_signs(text)
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
            term = text[start:i].strip()
            if term not in {"", "+", "-"}:
                terms.append(term)
            start = i
    tail = text[start:].strip()
    if tail not in {"", "+", "-"}:
        terms.append(tail)
    if depth != 0:
        raise ValueError("unbalanced parentheses")
    return terms


def _parse_terms(text: str):
    safe_text, local_dict, safe_to_original = _protect_scalar_product_atoms(text)
    for raw in _split_top_level_terms(safe_text):
        parsed = sp.sympify(raw, locals=local_dict, evaluate=False)
        yield parsed.xreplace(safe_to_original)


def main() -> int:
    print("QEDCalc Q01 scalar-to-integral-index mapping")
    if not INPUT.exists():
        print(f"missing input: {INPUT}")
        print("Run run_three_loop_q01_pq_basis_reduce.bat first.")
        return 1

    text = INPUT.read_text(encoding="utf-8")
    t0 = time.perf_counter()
    parsed_terms = list(_parse_terms(text))
    parse_seconds = time.perf_counter() - t0

    aggregate = {}
    t1 = time.perf_counter()
    for term in parsed_terms:
        mapped = q01_scalar_numerator_to_integrals(term)
        for index, coeff in mapped.terms.items():
            aggregate[index] = aggregate.get(index, sp.Integer(0)) + coeff
    aggregate = {idx: sp.cancel(coeff) for idx, coeff in aggregate.items() if coeff != 0}
    aggregate = {idx: coeff for idx, coeff in aggregate.items() if coeff != 0}
    map_seconds = time.perf_counter() - t1

    ordered = sorted(aggregate.items(), key=lambda item: item[0].powers, reverse=True)
    lines = [
        f"{sp.sstr(coeff)} * I({','.join(map(str, index.powers))})"
        for index, coeff in ordered
    ]
    OUTPUT.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")

    negative_isp = sum(
        1 for index in aggregate
        if any(power < 0 for power in index.powers[9:])
    )
    distinct_sectors = len({tuple(1 if power > 0 else 0 for power in idx.powers[:9]) for idx in aggregate})
    payload = {
        "diagram_id": "Q01",
        "input": str(INPUT.relative_to(ROOT)),
        "output": str(OUTPUT.relative_to(ROOT)),
        "elapsed_parse_seconds": parse_seconds,
        "elapsed_mapping_seconds": map_seconds,
        "source_top_level_term_count": len(parsed_terms),
        "distinct_integral_count": len(aggregate),
        "distinct_physical_sector_count": distinct_sectors,
        "integrals_with_negative_isp_power": negative_isp,
        "family_size": 12,
        "physical_denominator_count": 9,
        "q_zero_taken": False,
    }
    SUMMARY.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"parse saved p-q scalar expression: {parse_seconds:.3f} s")
    print(f"source top-level terms: {len(parsed_terms)}")
    print(f"integral-index mapping: {map_seconds:.3f} s")
    print(f"distinct integrals: {len(aggregate)}")
    print(f"distinct physical sectors: {distinct_sectors}")
    print(f"integrals with negative ISP powers: {negative_isp}")
    print(f"generated: {OUTPUT}")
    print(f"generated: {SUMMARY}")
    print("Q01 scalar-to-integral-index mapping PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
