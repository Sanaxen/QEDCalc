"""Re-run the Q01 symmetry relation probe with Fermat closure waves 1 and 2.

This wrapper leaves the validated relation-building implementation untouched.
It concatenates the two saved supplemental FORM exports into one parser input,
then temporarily redirects the existing probe to that combined supplement.
"""
from __future__ import annotations

from pathlib import Path

import examples.three_loop_q01_kira_symmetry_linear_relation_probe as probe
from examples.three_loop_q01_kira_symmetry_supplement_fermat import (
    _find_export as _find_wave1_export,
)
from examples.three_loop_q01_kira_symmetry_relation_closure2_fermat import (
    _find_export as _find_wave2_export,
)
from examples.three_loop_q01_kira_910_exact_closure1_firefly_export_audit import PROJECT

COMBINED_FORM = PROJECT / "q01_symmetry_supplement_fermat_wave1_wave2_merged.inc"


def main() -> None:
    wave1 = _find_wave1_export()
    wave2 = _find_wave2_export()
    text1 = wave1.read_text(encoding="utf-8", errors="strict")
    text2 = wave2.read_text(encoding="utf-8", errors="strict")
    COMBINED_FORM.write_text(text1.rstrip() + "\n" + text2.lstrip(), encoding="utf-8", newline="\n")

    print("QEDCalc Q01 symmetry relation probe with Fermat closure waves 1+2")
    print("wave-1 FORM export:", wave1)
    print("wave-2 FORM export:", wave2)
    print("combined supplemental FORM export:", COMBINED_FORM)

    probe._find_fermat_supplement_export = lambda: COMBINED_FORM
    probe.main()


if __name__ == "__main__":
    main()
