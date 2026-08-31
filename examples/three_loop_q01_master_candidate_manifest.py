from __future__ import annotations

import json
from pathlib import Path

from qedcalc.operations.ibp import IntegralIndex
from three_loop.q01_master_candidate_manifest import build_q01_master_candidate_manifest

ROOT = Path(__file__).resolve().parents[1]
REMAINING = ROOT / "output" / "3loop_q01_remaining_target_profile.json"
FACTORIZATION = ROOT / "output" / "3loop_q01_scalar_subtopology_factorization.json"
OUTPUT = ROOT / "output" / "3loop_q01_master_candidate_manifest.json"


def main() -> None:
    remaining_data = json.loads(REMAINING.read_text(encoding="utf-8"))
    factorization_data = json.loads(FACTORIZATION.read_text(encoding="utf-8"))
    remaining = tuple(IntegralIndex(tuple(record["index"])) for record in remaining_data["records"])
    factorization_by_index = {
        tuple(record["index"]): record["factorization"]
        for record in factorization_data["records"]
    }
    manifest = build_q01_master_candidate_manifest(remaining, factorization_by_index)
    data = {
        "remaining_count": manifest.remaining_count,
        "lower_loop_factorized_count": manifest.lower_loop_factorized_count,
        "connected_scalar_count": manifest.connected_scalar_count,
        "nonscalar_count": manifest.nonscalar_count,
        "genuine_three_loop_candidate_count": manifest.genuine_three_loop_candidate_count,
        "entries": [entry.__dict__ for entry in manifest.entries],
    }
    OUTPUT.write_text(json.dumps(data, indent=2), encoding="utf-8")

    print("QEDCalc Q01 master candidate manifest")
    print(f"remaining finite-system candidates: {manifest.remaining_count}")
    print(f"lower-loop factorized: {manifest.lower_loop_factorized_count}")
    print(f"connected scalar three-loop candidates: {manifest.connected_scalar_count}")
    print(f"nonscalar three-loop candidates: {manifest.nonscalar_count}")
    print(f"genuine three-loop candidates: {manifest.genuine_three_loop_candidate_count}")
    print("entries:")
    for entry in manifest.entries:
        print(f"  I{entry.index} category={entry.category} sector={entry.sector}")
    print(f"generated: {OUTPUT}")
    print("Q01 master candidate manifest PASS")


if __name__ == "__main__":
    main()
