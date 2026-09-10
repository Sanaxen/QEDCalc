from __future__ import annotations

from pathlib import Path

from three_loop.kira_form_inspect import write_inspection_json


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "output" / "kira_q01_4line_full_r6s2d2"
FORM_FILE = PROJECT / "results" / "Q01_4line" / "kira_Q01_4line.inc"
OUTPUT = PROJECT / "qedcalc_kira_form_structure.json"


def main() -> None:
    if not FORM_FILE.is_file():
        raise SystemExit(f"FORM export not found: {FORM_FILE}")

    result = write_inspection_json(FORM_FILE, OUTPUT)
    print("QEDCalc Q01 Kira FORM structure inspection")
    print(f"file: {FORM_FILE}")
    print(f"size: {result['size_bytes']} bytes")
    print(f"lines: {result['line_count']}")
    print(f"semicolon statements: {result['semicolon_count']}")
    print(f"num(...) wrappers: {result['num_wrapper_count']}")
    print(f"Q01_4line tokens: {result['q01_token_count']}")
    print("prefix counts:")
    for key, value in result["prefix_counts"].items():
        print(f"  {key}: {value}")
    print("integral token samples:")
    for token in result["integral_token_samples"]:
        print(f"  {token}")
    print("interesting line samples:")
    for line in result["interesting_line_samples"]:
        print(f"  {line}")
    print(f"generated: {OUTPUT}")
    print("Q01 Kira FORM structure inspection PASS")


if __name__ == "__main__":
    main()
