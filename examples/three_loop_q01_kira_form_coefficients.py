from __future__ import annotations

import json
from pathlib import Path

import sympy as sp

from three_loop.kira_form_coefficients import (
    coefficient_symbol_names,
    form_coefficient_to_sympy,
)
from three_loop.kira_form_parser import iter_kira_form_rules


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "output" / "kira_q01_4line_full_r6s2d2"
FORM_FILE = PROJECT / "results" / "Q01_4line" / "kira_Q01_4line.inc"
OUTPUT = PROJECT / "qedcalc_kira_form_coefficients_result.json"


def main() -> None:
    if not FORM_FILE.is_file():
        raise SystemExit(f"missing FORM reduction file: {FORM_FILE}")

    coefficient_count = 0
    unique_sources: set[str] = set()
    unique_sympy: set[str] = set()
    symbols_seen: set[str] = set()
    max_ops = 0
    failures: list[dict[str, str]] = []
    samples: list[dict[str, str]] = []

    for rule in iter_kira_form_rules(FORM_FILE, family="Q01_4line"):
        for term in rule.terms:
            coefficient_count += 1
            source = term.coefficient_form
            unique_sources.add(source)
            try:
                expr = form_coefficient_to_sympy(source)
            except Exception as exc:
                if len(failures) < 20:
                    failures.append({"source": source, "error": str(exc)})
                continue

            expr_text = sp.sstr(expr)
            unique_sympy.add(expr_text)
            symbols_seen.update(coefficient_symbol_names(expr))
            max_ops = max(max_ops, int(sp.count_ops(expr)))
            if len(samples) < 12:
                samples.append({"form": source, "sympy": expr_text})

    payload = {
        "form_file": str(FORM_FILE),
        "coefficient_count": coefficient_count,
        "unique_form_coefficients": len(unique_sources),
        "unique_sympy_coefficients": len(unique_sympy),
        "symbols_seen": sorted(symbols_seen),
        "max_sympy_ops": max_ops,
        "failure_count": len(failures),
        "failure_samples": failures,
        "samples": samples,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2), encoding="utf-8", newline="\n")

    print("QEDCalc Q01 Kira FORM coefficient import")
    print(f"FORM file: {FORM_FILE}")
    print(f"coefficients: {coefficient_count}")
    print(f"unique FORM coefficients: {len(unique_sources)}")
    print(f"unique SymPy coefficients: {len(unique_sympy)}")
    print(f"symbols seen: {', '.join(sorted(symbols_seen)) or '(none)'}")
    print(f"max SymPy op count: {max_ops}")
    print(f"conversion failures: {len(failures)}")
    print("samples:")
    for sample in samples:
        print(f"  FORM : {sample['form']}")
        print(f"  SymPy: {sample['sympy']}")
    print(f"generated: {OUTPUT}")

    if coefficient_count == 0:
        raise SystemExit("no Kira FORM coefficients were found")
    if failures:
        raise SystemExit("Kira FORM coefficient conversion failed; send the failure samples above")
    if not symbols_seen.issubset({"d", "z"}):
        raise SystemExit(f"unexpected coefficient symbols: {sorted(symbols_seen)}")

    # Exact sanity checks for the syntax constructs already observed in the
    # real Kira 3.1 export.  These protect against silently changing wrapper
    # semantics later.
    d, z = sp.symbols("d z")
    checks = {
        "+(1)": sp.Integer(1),
        "+(2*z+4)": 2 * z + 4,
        "+(num((4*d+4))*den(d))": (4 * d + 4) / d,
        "+(num(((4*d)*z+8*d+4))*den(d))": ((4 * d) * z + 8 * d + 4) / d,
    }
    for source, expected in checks.items():
        actual = form_coefficient_to_sympy(source, symbols={"d": d, "z": z})
        if sp.simplify(actual - expected) != 0:
            raise SystemExit(
                f"coefficient sanity check failed: {source}: {actual} != {expected}"
            )

    print("Q01 Kira FORM coefficient import PASS")


if __name__ == "__main__":
    main()
