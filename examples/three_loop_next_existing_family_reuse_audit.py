"""Audit the next unresolved quenched class against confirmed canonical families."""
from __future__ import annotations

import json

from three_loop.canonical_family_bootstrap import audit_next_quenched_family
from three_loop.existing_family_reuse import audit_existing_family_reuse
from three_loop.integral_family_classification import ROOT, load_topologies

OUTPUT_DIR = ROOT / "output" / "three_loop_integral_family_audit"
OUTPUT_JSON = OUTPUT_DIR / "three_loop_next_existing_family_reuse_audit.json"
OUTPUT_TXT = OUTPUT_DIR / "three_loop_next_existing_family_reuse_audit.txt"

# Canonical-family members already confirmed by the executable global registry.
CONFIRMED_QUENCHED_IDS = {
    "Q01", "Q41",
    "Q02", "Q45",
    "Q03", "Q43",
    "Q04", "Q46",
}
CONFIRMED_FAMILY_REPRESENTATIVES = ["Q01", "Q02", "Q03", "Q04"]


def main() -> None:
    rows = load_topologies()
    bootstrap = audit_next_quenched_family(rows, CONFIRMED_QUENCHED_IDS)
    candidate_ids = list(bootstrap["candidate_ids"])
    audit = audit_existing_family_reuse(
        rows,
        candidate_ids,
        CONFIRMED_FAMILY_REPRESENTATIVES,
    )
    audit["bootstrap_representative"] = bootstrap["representative"]
    audit["bootstrap_family_candidate_id"] = bootstrap["family_candidate_id"]
    audit["bootstrap_kira_ready"] = bootstrap["kira_ready"]
    audit["bootstrap_audit_pass"] = bootstrap["audit_pass"]
    if not bootstrap["audit_pass"]:
        audit["errors"] = list(audit["errors"]) + [
            f"bootstrap audit failed for {bootstrap['representative']}"
        ]
        audit["audit_pass"] = False

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "QEDCalc next existing-family reuse audit",
        f"transform scope: {audit['transform_scope']}",
        f"confirmed family representatives: {audit['confirmed_family_representatives']}",
        f"candidate IDs: {audit['candidate_ids']}",
        f"bootstrap representative: {audit['bootstrap_representative']}",
        f"bootstrap family candidate: {audit['bootstrap_family_candidate_id']}",
        f"bootstrap Kira ready: {audit['bootstrap_kira_ready']}",
    ]
    for rec in audit["records"]:
        bits = [
            f"{family_id} reuse={witness is not None}"
            for family_id, witness in rec["reuse"].items()
        ]
        lines.append(f"{rec['diagram_id']}: " + "; ".join(bits))
    lines.extend([
        f"representative reuse hits: {audit['representative_reuse_hits']}",
        f"new family required under current scope: {audit['new_family_required_under_current_scope']}",
        f"internal audit errors: {len(audit['errors'])}",
        f"audit JSON: {OUTPUT_JSON}",
        f"audit TXT: {OUTPUT_TXT}",
        "QEDCalc next existing-family reuse audit " + ("PASS" if audit["audit_pass"] else "FAIL"),
    ])
    OUTPUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    for line in lines:
        print(line)
    if audit["errors"]:
        for error in audit["errors"]:
            print("ERROR:", error)
        raise SystemExit("QEDCalc next existing-family reuse audit FAIL")


if __name__ == "__main__":
    main()
