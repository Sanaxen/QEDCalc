"""Final audit for the fully closed Q01 symmetry-relation probe.

This stage performs no Kira, FireFly, Fermat, or projected-trace recomputation.
It re-runs the saved wave-1..6 relation probe and accepts the mathematically
valid case in which every symmetry application closes to a trivial identity and
there are therefore zero nontrivial relation rows.
"""
from __future__ import annotations

import json
from pathlib import Path

from examples.three_loop_q01_kira_910_exact_closure1_firefly_export_audit import PROJECT
import examples.three_loop_q01_kira_symmetry_linear_relation_probe_wave6 as wave6

PROBE_JSON = PROJECT / "q01_kira_symmetry_linear_relation_probe.json"
OUTPUT_JSON = PROJECT / "q01_kira_symmetry_relation_final_audit.json"


def main() -> None:
    print("QEDCalc Q01 symmetry relation final audit")
    print("mode: saved wave-1..6 artifacts only; no reduction recomputation")

    probe_exit = 0
    try:
        wave6.main()
    except SystemExit as exc:
        probe_exit = int(exc.code) if isinstance(exc.code, int) else 1
        print("underlying probe exit code:", probe_exit)

    if not PROBE_JSON.exists():
        raise SystemExit(f"ERROR: probe JSON not found: {PROBE_JSON}")
    data = json.loads(PROBE_JSON.read_text(encoding="utf-8"))

    attempted = int(data.get("relation_building_applications_attempted", 0) or 0)
    unimodular = int(data.get("unimodular_applications", 0) or 0)
    expansion_failures = int(data.get("numerator_expansion_failures", 0) or 0)
    missing = int(data.get("expanded_integrals_missing_from_merged_reduction_graph", 0) or 0)
    outside = int(data.get("relations_closing_outside_displayed_final_basis", 0) or 0)
    trivial = int(data.get("trivial_identity_applications", 0) or 0)
    nontrivial = int(data.get("closed_nontrivial_relation_applications", 0) or 0)
    unique_rows = int(data.get("unique_exact_relation_rows", 0) or 0)
    rank_consistent = bool(data.get("generic_rank_consistent", False))
    generic_rank = data.get("generic_relation_rank")
    independent = data.get("generic_independent_master_directions")

    classified = trivial + nontrivial
    complete = (
        attempted > 0
        and unimodular == attempted
        and expansion_failures == 0
        and missing == 0
        and outside == 0
        and classified == attempted
        and rank_consistent
    )
    all_trivial = complete and trivial == attempted and nontrivial == 0 and unique_rows == 0

    summary = {
        "mode": "final saved-artifact audit of Q01 symmetry/momentum-map relations",
        "underlying_probe_exit_code": probe_exit,
        "applications_attempted": attempted,
        "unimodular_applications": unimodular,
        "numerator_expansion_failures": expansion_failures,
        "missing_reduction_integrals": missing,
        "relations_outside_displayed_basis": outside,
        "trivial_identity_applications": trivial,
        "closed_nontrivial_relation_applications": nontrivial,
        "unique_exact_relation_rows": unique_rows,
        "classified_applications": classified,
        "generic_rank_consistent": rank_consistent,
        "generic_relation_rank": generic_rank,
        "generic_independent_directions_within_this_relation_system": independent,
        "complete": complete,
        "all_symmetry_applications_are_trivial_identities": all_trivial,
        "interpretation": (
            "All tested saved Kira momentum/sector symmetry applications close exactly, "
            "but they generate no nontrivial linear relation among the 60 displayed forms. "
            "This does not prove that 60 is a globally minimal IBP master basis."
            if all_trivial
            else "The saved relation system is not in the all-trivial fully closed state."
        ),
        "pass": complete,
    }
    OUTPUT_JSON.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print("applications attempted:", attempted)
    print("classified applications:", classified)
    print("trivial identities:", trivial)
    print("nontrivial relation applications:", nontrivial)
    print("missing reduction integrals:", missing)
    print("outside displayed basis:", outside)
    print("unique exact relation rows:", unique_rows)
    print("generic relation rank:", generic_rank)
    print("independent directions within this relation system:", independent)
    print("all symmetry applications trivial:", all_trivial)
    print("final audit JSON:", OUTPUT_JSON)

    if not complete:
        raise SystemExit("Q01 symmetry relation final audit FAIL")
    print("Q01 symmetry relation final audit PASS")


if __name__ == "__main__":
    main()
