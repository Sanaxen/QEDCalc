"""Probe the saved Q01 projected-amplitude coefficient artifact without recomputation.

This helper only reads ``output/3loop_q01_integral_indices.txt``.  It verifies
that the canonical 910 native integrals are present, extracts the coefficient
text multiplying each ``I(...)`` token, and tests whether those coefficients
can be parsed by SymPy.  The expensive projected trace is never regenerated.
"""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import re

import sympy as sp
from sympy.parsing.sympy_parser import (
    convert_xor,
    parse_expr,
    standard_transformations,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "output" / "3loop_q01_integral_indices.txt"
OUTPUT_JSON = ROOT / "output" / "3loop_q01_saved_projected_amplitude_probe.json"
EXPECTED_NATIVE = 910

_INTEGRAL_RE = re.compile(r"\bI\(\s*([-+]?\d+(?:\s*,\s*[-+]?\d+){11})\s*\)")
_IDENT_RE = re.compile(r"\b[A-Za-z_]\w*\b")
_TRANSFORMS = standard_transformations + (convert_xor,)


def _extract_coefficient(text: str, match: re.Match[str]) -> str:
    before = text[: match.start()].strip()
    after = text[match.end() :].strip()
    if after:
        raise ValueError(f"unexpected text after I(...): {after[:120]!r}")
    if before.endswith("*"):
        before = before[:-1].rstrip()
    if before.endswith("+"):
        before = before[:-1].rstrip()
    if before in {"", "+"}:
        return "1"
    if before == "-":
        return "-1"
    return before


def _parse_coefficient(text: str) -> sp.Expr:
    names = sorted(set(_IDENT_RE.findall(text)))
    local_dict = {
        name: sp.Symbol(name)
        for name in names
        if name not in {"I", "E", "pi", "oo", "zoo", "nan"}
    }
    return parse_expr(
        text,
        local_dict=local_dict,
        transformations=_TRANSFORMS,
        evaluate=False,
    )


def main() -> None:
    print("QEDCalc Q01 saved projected-amplitude coefficient probe")
    print("mode: saved artifact only; projected trace is NOT recomputed")
    print("source:", SOURCE)

    if not SOURCE.exists():
        raise SystemExit(f"ERROR: saved Q01 projected-amplitude artifact not found: {SOURCE}")

    records: list[dict[str, object]] = []
    non_integral: list[dict[str, object]] = []
    parse_failures: list[dict[str, object]] = []
    coefficient_symbols: Counter[str] = Counter()

    for line_no, raw in enumerate(SOURCE.read_text(encoding="utf-8").splitlines(), 1):
        text = raw.strip()
        if not text:
            continue
        matches = list(_INTEGRAL_RE.finditer(text))
        if not matches:
            non_integral.append({"line": line_no, "text": text[:300]})
            continue
        if len(matches) != 1:
            parse_failures.append(
                {"line": line_no, "error": f"expected one I(...) token, got {len(matches)}", "text": text[:300]}
            )
            continue

        match = matches[0]
        indices = tuple(int(v.strip()) for v in match.group(1).split(","))
        try:
            coefficient_text = _extract_coefficient(text, match)
        except ValueError as exc:
            parse_failures.append({"line": line_no, "error": str(exc), "text": text[:300]})
            continue

        parsed_ok = True
        parsed_repr = ""
        try:
            coefficient = _parse_coefficient(coefficient_text)
            parsed_repr = str(coefficient)
            for symbol in coefficient.free_symbols:
                coefficient_symbols[str(symbol)] += 1
        except Exception as exc:
            parsed_ok = False
            parse_failures.append(
                {
                    "line": line_no,
                    "error": f"coefficient parse failed: {exc}",
                    "coefficient": coefficient_text[:300],
                }
            )

        records.append(
            {
                "line": line_no,
                "indices": list(indices),
                "coefficient_text": coefficient_text,
                "parsed_ok": parsed_ok,
                "parsed_repr": parsed_repr,
            }
        )

    unique_integrals = {tuple(item["indices"]) for item in records}
    duplicate_count = len(records) - len(unique_integrals)
    parsed_ok_count = sum(bool(item["parsed_ok"]) for item in records)

    summary = {
        "mode": "saved projected-amplitude artifact probe; no projected-trace recomputation",
        "source": str(SOURCE),
        "integral_lines": len(records),
        "unique_integrals": len(unique_integrals),
        "duplicate_integral_lines": duplicate_count,
        "expected_native": EXPECTED_NATIVE,
        "coefficient_parse_ok": parsed_ok_count,
        "coefficient_parse_failed": len(parse_failures),
        "non_integral_lines": len(non_integral),
        "coefficient_symbols": dict(sorted(coefficient_symbols.items())),
        "sample_records": records[:8],
        "parse_failures": parse_failures[:12],
        "non_integral_samples": non_integral[:12],
        "pass": (
            len(records) == EXPECTED_NATIVE
            and len(unique_integrals) == EXPECTED_NATIVE
            and duplicate_count == 0
            and len(parse_failures) == 0
            and parsed_ok_count == EXPECTED_NATIVE
        ),
    }
    OUTPUT_JSON.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print("integral lines:", len(records))
    print("unique native integrals:", len(unique_integrals))
    print("duplicate integral lines:", duplicate_count)
    print("coefficient parse OK:", parsed_ok_count)
    print("coefficient parse failed:", len(parse_failures))
    print("non-integral/header lines:", len(non_integral))
    print("coefficient symbols:", dict(sorted(coefficient_symbols.items())))
    print("probe JSON:", OUTPUT_JSON)

    for item in records[:5]:
        print(
            f"sample line {item['line']}: coeff={item['coefficient_text']!r} "
            f"I{tuple(item['indices'])}"
        )
    if parse_failures:
        print("first parse failures:")
        for item in parse_failures[:5]:
            print("  ", item)

    if not summary["pass"]:
        print("Q01 saved projected-amplitude coefficient probe FAIL")
        raise SystemExit(1)
    print("Q01 saved projected-amplitude coefficient probe PASS")


if __name__ == "__main__":
    main()
