"""Re-run the Q01 symmetry relation probe with Fermat closure waves 1, 2 and 3."""
from __future__ import annotations

import examples.three_loop_q01_kira_symmetry_linear_relation_probe as probe
from examples.three_loop_q01_kira_symmetry_supplement_fermat import _find_export as _find_wave1_export
from examples.three_loop_q01_kira_symmetry_relation_closure2_fermat import _find_export as _find_wave2_export
from examples.three_loop_q01_kira_symmetry_relation_closure3_fermat import _find_export as _find_wave3_export
from examples.three_loop_q01_kira_910_exact_closure1_firefly_export_audit import PROJECT

COMBINED_FORM = PROJECT / "q01_symmetry_supplement_fermat_wave1_wave2_wave3_merged.inc"


def main() -> None:
    waves = (_find_wave1_export(), _find_wave2_export(), _find_wave3_export())
    combined = "\n".join(path.read_text(encoding="utf-8", errors="strict").strip() for path in waves) + "\n"
    COMBINED_FORM.write_text(combined, encoding="utf-8", newline="\n")

    print("QEDCalc Q01 symmetry relation probe with Fermat closure waves 1+2+3")
    for i, path in enumerate(waves, 1):
        print(f"wave-{i} FORM export:", path)
    print("combined supplemental FORM export:", COMBINED_FORM)

    probe._find_fermat_supplement_export = lambda: COMBINED_FORM
    probe.main()


if __name__ == "__main__":
    main()
