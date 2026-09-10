from __future__ import annotations

import json
from pathlib import Path

from three_loop.kira_results import parse_kira_log


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "output" / "kira_q01_4line_smoke"
LOG = PROJECT / "kira_run.log"
OUTPUT = PROJECT / "qedcalc_kira_parsed_result.json"


def main() -> None:
    if not LOG.is_file():
        raise FileNotFoundError(
            f"Kira smoke log not found: {LOG}. Run run_three_loop_q01_kira_wsl_smoke.bat first."
        )

    result = parse_kira_log(LOG)
    OUTPUT.write_text(json.dumps(result, indent=2), encoding="utf-8", newline="\n")

    print("QEDCalc Q01 Kira result import smoke")
    print(f"log: {LOG}")
    print(f"IBP identities: {result['ibp_identity_count']}")
    print(f"LI identities: {result['li_identity_count']}")
    print(f"nontrivial sectors: {result['nontrivial_sector_count']}")
    print(f"trivial sectors: {result['trivial_sector_count']}")
    print(f"sector relations: {result['sector_relation_count']}")
    print(f"sector symmetries: {result['sector_symmetry_count']}")
    print(f"masters: {result['parsed_master_count']}")
    for master in result["masters"]:
        print(
            f"  {master['family']}[{','.join(str(v) for v in master['indices'])}] "
            f"# sector {master['sector']}"
        )
    print(f"triangular time: {result['triangular_seconds']} s")
    print(f"Kira total time: {result['total_seconds']} s")
    print(f"generated: {OUTPUT}")

    expected_masters = [
        [1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    ]
    actual_masters = [master["indices"] for master in result["masters"]]
    checks = {
        "ibp_15": result["ibp_identity_count"] == 15,
        "li_1": result["li_identity_count"] == 1,
        "master_count_2": result["parsed_master_count"] == 2,
        "master_count_consistent": result["master_count_consistent"] is True,
        "expected_master_basis": actual_masters == expected_masters,
        "triangular_completed": result["triangular_seconds"] is not None,
        "total_time_present": result["total_seconds"] is not None,
    }
    for name, passed in checks.items():
        print(f"check {name}: {'PASS' if passed else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit("Q01 Kira result import smoke FAIL")
    print("Q01 Kira result import smoke PASS")


if __name__ == "__main__":
    main()
