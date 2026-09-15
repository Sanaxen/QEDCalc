"""Audit every member of Q01's structural candidate class for exact Q01_full reuse."""
from __future__ import annotations

import json

from three_loop.integral_family_classification import ROOT, load_topologies
from three_loop.q01_family_equivalence import audit_q01_family_equivalence

OUTPUT_DIR = ROOT / "output" / "three_loop_integral_family_audit"
OUTPUT_JSON = OUTPUT_DIR / "three_loop_q01_family_equivalence_audit.json"
OUTPUT_TXT = OUTPUT_DIR / "three_loop_q01_family_equivalence_audit.txt"


def main() -> None:
    audit = audit_q01_family_equivalence(load_topologies())
    errors = list(audit.get("errors", []))
    if "Q01" not in audit.get("confirmed_ids", []):
        errors.append("Q01 identity mapping was not confirmed")
    audit["errors"] = errors
    audit["audit_pass"] = not errors

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "QEDCalc Q01-family equivalence mapper / audit",
        "",
        f"candidate IDs: {audit.get('candidate_ids', [])}",
        f"confirmed Q01_full reuse: {audit.get('confirmed_ids', [])}",
        f"internal audit errors: {len(errors)}",
        "",
    ]
    for rec in audit.get("records", []):
        lines.append(f"{rec['diagram_id']}: {rec['status']}")
        witness = rec.get("witness")
        if witness:
            lines.extend([
                f"  reflection: {witness['reflection']}",
                f"  loop transform: {witness['loop_momentum_transform']}",
                f"  external transform: {witness['external_momentum_transform']}",
                f"  physical permutation: {witness['physical_propagator_permutation']}",
                f"  P1..P12 exact: {all(witness['propagator_exact_match'])}",
                f"  ISP bridge exact: {all(witness['isp_bridge_exact_match'])}",
            ])
    if errors:
        lines.extend(["", "Errors:"] + [f"  {error}" for error in errors])
    lines.extend([
        "",
        f"audit JSON: {OUTPUT_JSON}",
        f"audit TXT: {OUTPUT_TXT}",
        "",
        "Q01-family equivalence mapper / audit " + ("PASS" if not errors else "FAIL"),
    ])
    OUTPUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("QEDCalc Q01-family equivalence mapper / audit")
    print("candidate IDs:", audit.get("candidate_ids", []))
    print("confirmed Q01_full reuse:", audit.get("confirmed_ids", []))
    for rec in audit.get("records", []):
        witness = rec.get("witness")
        print(rec["diagram_id"], rec["status"])
        if witness:
            print("  reflection:", witness["reflection"])
            print("  loop transform:", witness["loop_momentum_transform"])
            print("  external transform:", witness["external_momentum_transform"])
            print("  physical permutation:", witness["physical_propagator_permutation"])
            print("  P1..P12 exact:", all(witness["propagator_exact_match"]))
            print("  ISP bridge exact:", all(witness["isp_bridge_exact_match"]))
    print("internal audit errors:", len(errors))
    print("audit JSON:", OUTPUT_JSON)
    print("audit TXT:", OUTPUT_TXT)
    if errors:
        for error in errors:
            print("ERROR:", error)
        raise SystemExit("Q01-family equivalence mapper / audit FAIL")
    print("Q01-family equivalence mapper / audit PASS")


if __name__ == "__main__":
    main()
