"""Run automatic canonical-family discovery for all 50 quenched diagrams."""
from __future__ import annotations

import json

from three_loop.integral_family_classification import ROOT, load_topologies
from three_loop.quenched_family_autodiscovery import audit_quenched_family_autodiscovery

OUTPUT_DIR = ROOT / "output" / "three_loop_integral_family_audit"
OUTPUT_JSON = OUTPUT_DIR / "three_loop_quenched_family_autodiscovery_audit.json"
OUTPUT_TXT = OUTPUT_DIR / "three_loop_quenched_family_autodiscovery_audit.txt"

KNOWN_MANUAL_MAPPING = {
    "Q01": "Q01_full", "Q41": "Q01_full",
    "Q02": "Q02_full", "Q45": "Q02_full",
    "Q03": "Q03_full", "Q43": "Q03_full",
    "Q04": "Q04_full", "Q46": "Q04_full",
    "Q05": "Q05_full", "Q42": "Q05_full",
    "Q06": "Q06_full", "Q44": "Q06_full",
    "Q07": "Q07_full", "Q47": "Q07_full",
    "Q08": "Q08_full", "Q48": "Q08_full",
    "Q09": "Q09_full", "Q49": "Q09_full",
    "Q10": "Q10_full", "Q50": "Q10_full",
    "Q11": "Q11_full", "Q31": "Q11_full",
}
KNOWN_MANUAL_FAMILY_PREFIX = [f"Q{i:02d}_full" for i in range(1, 12)]


def _apply_manual_regression_guard(audit: dict) -> list[str]:
    errors: list[str] = []
    discovered = {
        str(rec["diagram_id"]): str(rec["canonical_integral_family_id"])
        for rec in audit.get("records", [])
    }
    for did, expected_family in KNOWN_MANUAL_MAPPING.items():
        actual = discovered.get(did)
        if actual != expected_family:
            errors.append(
                f"manual-regression mismatch: {did} -> {actual}, expected {expected_family}"
            )
    actual_prefix = list(audit.get("family_order", []))[: len(KNOWN_MANUAL_FAMILY_PREFIX)]
    if actual_prefix != KNOWN_MANUAL_FAMILY_PREFIX:
        errors.append(
            "manual-regression family-order mismatch: "
            f"actual={actual_prefix}, expected={KNOWN_MANUAL_FAMILY_PREFIX}"
        )
    return errors


def main() -> None:
    rows = load_topologies()
    audit = audit_quenched_family_autodiscovery(rows)

    regression_errors = _apply_manual_regression_guard(audit)
    if regression_errors:
        audit["errors"] = list(audit.get("errors", [])) + regression_errors
        audit["audit_pass"] = False
    audit["manual_regression_checked_diagrams"] = len(KNOWN_MANUAL_MAPPING)
    audit["manual_regression_pass"] = not regression_errors

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "QEDCalc quenched canonical-family autodiscovery audit",
        f"transform scope: {audit['transform_scope']}",
        f"quenched diagrams: {audit['quenched_diagram_count']}",
        f"confirmed quenched: {audit['confirmed_quenched_count']}",
        f"unresolved quenched: {audit['unresolved_quenched_count']}",
        f"canonical families: {audit['canonical_family_count']}",
        f"manual regression checked diagrams: {audit['manual_regression_checked_diagrams']}",
        f"manual regression pass: {audit['manual_regression_pass']}",
        "",
        "Discovery steps:",
    ]
    for step in audit["steps"]:
        lines.append(
            "  step {step}: rep={rep} candidates={candidates} status={status} "
            "family={family} reuse_hits={hits} confirmed={confirmed} families={families}".format(
                step=step["step"],
                rep=step["representative"],
                candidates=step["candidate_ids"],
                status=step["status"],
                family=step.get("canonical_family_id"),
                hits=step.get("reuse_hits", []),
                confirmed=step.get("confirmed_after_step", "-"),
                families=step.get("family_count_after_step", "-"),
            )
        )

    lines.extend(["", "Canonical registry:"])
    for family_id in audit["family_order"]:
        entry = audit["canonical_registry"][family_id]
        lines.append(
            f"  {family_id}: representative={entry['representative']} "
            f"confirmed={entry['confirmed_diagrams']} master_basis={entry['master_basis_id']} "
            f"mode={entry['discovery_mode']}"
        )

    lines.extend([
        "",
        f"internal audit errors: {len(audit['errors'])}",
        f"audit JSON: {OUTPUT_JSON}",
        f"audit TXT: {OUTPUT_TXT}",
        "QEDCalc quenched canonical-family autodiscovery audit "
        + ("PASS" if audit["audit_pass"] else "FAIL"),
    ])
    OUTPUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    for line in lines:
        print(line)
    if audit["errors"]:
        for error in audit["errors"]:
            print("ERROR:", error)
        raise SystemExit("QEDCalc quenched canonical-family autodiscovery audit FAIL")


if __name__ == "__main__":
    main()
