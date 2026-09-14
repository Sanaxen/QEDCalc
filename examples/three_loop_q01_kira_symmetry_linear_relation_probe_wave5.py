"""Re-run the Q01 symmetry relation probe with Fermat closure waves 1 through 5."""
from __future__ import annotations

import sympy as sp

import examples.three_loop_q01_kira_symmetry_linear_relation_probe as probe
from examples.three_loop_q01_kira_symmetry_supplement_fermat import _find_export as _find_wave1_export
from examples.three_loop_q01_kira_symmetry_relation_closure2_fermat import _find_export as _find_wave2_export
from examples.three_loop_q01_kira_symmetry_relation_closure3_fermat import _find_export as _find_wave3_export
from examples.three_loop_q01_kira_symmetry_relation_closure4_fermat import _find_export as _find_wave4_export
from examples.three_loop_q01_kira_symmetry_relation_closure5_fermat import _find_export as _find_wave5_export
from examples.three_loop_q01_kira_910_exact_closure1_firefly_export_audit import PROJECT

COMBINED_FORM = PROJECT / "q01_symmetry_supplement_fermat_wave1_wave2_wave3_wave4_wave5_merged.inc"


def _fixed_generic_rank(relations, basis, point):
    rows = []
    for relation in relations:
        row = []
        valid = True
        for key in basis:
            try:
                value = sp.cancel(sp.sympify(relation.get(key, sp.Integer(0))).subs(point))
            except Exception:
                valid = False
                break
            if value.has(sp.zoo, sp.nan, sp.oo, -sp.oo):
                valid = False
                break
            row.append(value)
        if valid:
            rows.append(row)
    if not rows:
        return 0
    return int(sp.Matrix(rows).rank())


def main() -> None:
    waves = (
        _find_wave1_export(),
        _find_wave2_export(),
        _find_wave3_export(),
        _find_wave4_export(),
        _find_wave5_export(),
    )
    combined = "\n".join(path.read_text(encoding="utf-8", errors="strict").strip() for path in waves) + "\n"
    COMBINED_FORM.write_text(combined, encoding="utf-8", newline="\n")

    print("QEDCalc Q01 symmetry relation probe with Fermat closure waves 1+2+3+4+5")
    for i, path in enumerate(waves, 1):
        print(f"wave-{i} FORM export:", path)
    print("combined supplemental FORM export:", COMBINED_FORM)
    print("generic-rank zero-fill bugfix: enabled")

    probe._find_fermat_supplement_export = lambda: COMBINED_FORM
    probe._generic_rank = _fixed_generic_rank
    probe.main()


if __name__ == "__main__":
    main()
