"""Compare sparse-discovery master sets across levels without recomputation."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from three_loop.integral_family_classification import ROOT

AUDIT_DIR = ROOT / "output" / "three_loop_integral_family_audit"


def _path(family: str, level: int) -> Path:
    return AUDIT_DIR / f"three_loop_{family.lower()}_firefly_sparse_l{level}_audit.json"


def _load(family: str, level: int) -> dict:
    path = _path(family, level)
    if not path.exists():
        raise FileNotFoundError(path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("stage") != "master_basis_sparse_discovery":
        raise ValueError(f"unexpected audit stage in {path}")
    if payload.get("family") != family:
        raise ValueError(f"family mismatch in {path}")
    if not payload.get("audit_pass"):
        raise ValueError(f"sparse audit did not pass: {path}")
    return payload


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--family", required=True)
    p.add_argument("--levels", nargs="+", type=int, default=[0, 1])
    args = p.parse_args()

    levels = sorted(set(args.levels))
    if len(levels) < 2:
        raise SystemExit("ERROR: supply at least two completed sparse levels")

    rows = [(level, _load(args.family, level)) for level in levels]
    print("QEDCalc sparse master-set comparison")
    print(f"family: {args.family}")

    previous = None
    all_stable = True
    for level, payload in rows:
        current = set(payload.get("masters", []))
        print(
            f"L{level}: targets={payload.get('target_count')} "
            f"envelope={payload.get('envelope', {}).get('tag')} "
            f"masters={len(current)}"
        )
        if previous is not None:
            p_level, p_set = previous
            missing = p_set - current
            added = current - p_set
            equal = p_set == current
            retained = len(p_set & current)
            print(
                f"  L{p_level}->L{level}: retained={retained}/{len(p_set)} "
                f"missing={len(missing)} added={len(added)} equal={equal}"
            )
            if missing:
                print("  WARNING: higher sparse level does not retain all prior masters")
            if not equal:
                all_stable = False
        previous = (level, current)

    print()
    if all_stable:
        print(
            "RESULT: sparse master sets are identical across the tested levels. "
            "This is strong evidence for using the highest tested sparse level "
            "as the candidate basis, but promotion still requires closure validation."
        )
    else:
        print(
            "RESULT: sparse master set is still changing. Run the next sparse level "
            "or enter mandatory-union/closure refinement before promotion."
        )


if __name__ == "__main__":
    main()
