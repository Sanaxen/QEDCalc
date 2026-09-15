"""Automatic discovery of canonical families for all quenched three-loop diagrams.

The engine deliberately reuses the same conservative algebraic machinery as the
manual bootstrap/reuse workflow:

1. Q01/Q41 are established by the dedicated exact Q01 mapper.
2. The next unresolved structural class is bootstrapped algebraically.
3. The class is checked against every already-confirmed family representative.
4. If one existing family is reused, every class member must have an exact
   witness to that same family before promotion.
5. Otherwise the bootstrap candidate is promoted only when it is Kira-ready,
   full-rank, requires no partial-fraction/family split, and every member has an
   exact P1..P12 witness.
6. The loop repeats until all 50 quenched diagrams are classified or an
   exceptional case is encountered.

A negative reuse result is only with respect to the current conservative
transform scope implemented by ``existing_family_reuse``: open-line reflection
plus signed loop-momentum relabeling.  It does not exclude a more general
AFFINE/GL(Z) relation.
"""
from __future__ import annotations

from collections import Counter
from typing import Any

from three_loop.canonical_family_bootstrap import audit_next_quenched_family
from three_loop.existing_family_reuse import TRANSFORM_SCOPE, audit_existing_family_reuse
from three_loop.q01_family_equivalence import audit_q01_family_equivalence


def _all_quenched_ids(rows: list[dict[str, Any]]) -> set[str]:
    return {str(row["id"]) for row in rows if row.get("family") == "quenched"}


def _bootstrap_record_by_id(boot: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(rec["diagram_id"]): rec for rec in boot.get("records", [])}


def _validate_new_family_bootstrap(boot: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    rep = str(boot.get("representative"))
    if not boot.get("audit_pass"):
        errors.extend(str(item) for item in boot.get("errors", []))
        if not boot.get("errors"):
            errors.append(f"{rep}: bootstrap audit failed")
    if not boot.get("kira_ready"):
        errors.append(f"{rep}: bootstrap is not Kira-ready")
    if boot.get("requires_partial_fraction_or_family_split"):
        errors.append(f"{rep}: requires partial fraction or family split")
    if boot.get("canonical_denominator_count") != 12:
        errors.append(
            f"{rep}: canonical denominator count is {boot.get('canonical_denominator_count')}, expected 12"
        )
    if boot.get("canonical_scalar_product_rank") != 12:
        errors.append(
            f"{rep}: canonical scalar-product rank is {boot.get('canonical_scalar_product_rank')}, expected 12"
        )
    for rec in boot.get("records", []):
        did = str(rec.get("diagram_id"))
        witness = rec.get("witness")
        if rec.get("status") != "confirmed_algebraic_equivalence" or witness is None:
            errors.append(f"{did}: missing bootstrap canonical-family witness")
            continue
        exact = list(witness.get("propagator_exact_match", []))
        if not exact or not all(exact):
            errors.append(f"{did}: bootstrap P1..P12 witness is not exact")
    return errors


def _reuse_witnesses_for_family(
    reuse: dict[str, Any], family_id: str, candidate_ids: list[str]
) -> tuple[dict[str, dict[str, Any]], list[str]]:
    errors: list[str] = []
    witnesses: dict[str, dict[str, Any]] = {}
    records = {str(rec["diagram_id"]): rec for rec in reuse.get("records", [])}
    for did in candidate_ids:
        rec = records.get(did)
        witness = None if rec is None else rec.get("reuse", {}).get(family_id)
        if witness is None:
            errors.append(f"{did}: representative reused {family_id}, but this member has no exact witness")
            continue
        exact = witness.get("propagator_exact_match")
        if exact is not None and (not exact or not all(exact)):
            errors.append(f"{did}: reuse witness to {family_id} is not exact")
            continue
        witnesses[did] = witness
    return witnesses, errors


def audit_quenched_family_autodiscovery(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Discover/promote quenched canonical families until all 50 are classified."""
    by_id = {str(row["id"]): row for row in rows}
    quenched_ids = _all_quenched_ids(rows)
    errors: list[str] = []

    if len(quenched_ids) != 50:
        errors.append(f"expected 50 quenched diagrams, found {len(quenched_ids)}")

    q01 = audit_q01_family_equivalence(rows)
    if not q01.get("audit_pass"):
        errors.extend(str(item) for item in q01.get("errors", []))
        if not q01.get("errors"):
            errors.append("Q01-family equivalence audit failed")

    q01_confirmed = [str(did) for did in q01.get("confirmed_ids", [])]
    if set(q01_confirmed) != {"Q01", "Q41"}:
        errors.append(f"unexpected Q01 confirmed set: {q01_confirmed}")

    confirmed_ids: set[str] = set(q01_confirmed)
    representatives: list[str] = ["Q01"]
    family_order: list[str] = ["Q01_full"]
    registry: dict[str, dict[str, Any]] = {
        "Q01_full": {
            "representative": "Q01",
            "confirmed_diagrams": list(q01_confirmed),
            "master_basis_id": "Q01_final60",
            "kira_reusable": True,
            "equivalence_audit_pass": bool(q01.get("audit_pass")),
            "discovery_mode": "dedicated_q01_mapper",
        }
    }

    diagram_records: dict[str, dict[str, Any]] = {}
    q01_witness_by_id = {
        str(rec["diagram_id"]): rec.get("witness")
        for rec in q01.get("records", [])
        if rec.get("status") == "confirmed"
    }
    for did in q01_confirmed:
        diagram_records[did] = {
            "diagram_id": did,
            "canonical_integral_family_id": "Q01_full",
            "representative": "Q01",
            "promotion_mode": "dedicated_q01_mapper",
            "witness": q01_witness_by_id.get(did),
        }

    steps: list[dict[str, Any]] = []
    safety_limit = len(quenched_ids) + 1

    while not errors and confirmed_ids != quenched_ids:
        if len(steps) >= safety_limit:
            errors.append("autodiscovery exceeded safety iteration limit")
            break

        try:
            boot = audit_next_quenched_family(rows, confirmed_ids)
        except Exception as exc:
            errors.append(f"next-family bootstrap raised: {exc}")
            break

        candidate_ids = [str(did) for did in boot.get("candidate_ids", [])]
        representative = str(boot.get("representative"))
        if not candidate_ids or representative not in candidate_ids:
            errors.append(f"{representative}: invalid bootstrap candidate IDs {candidate_ids}")
            break
        if any(did in confirmed_ids for did in candidate_ids):
            errors.append(f"{representative}: bootstrap returned already-confirmed member(s): {candidate_ids}")
            break

        reuse = audit_existing_family_reuse(rows, candidate_ids, representatives)
        hits = list(reuse.get("representative_reuse_hits", []))
        step: dict[str, Any] = {
            "step": len(steps) + 1,
            "representative": representative,
            "candidate_ids": candidate_ids,
            "bootstrap_family_candidate_id": boot.get("family_candidate_id"),
            "bootstrap_kira_ready": bool(boot.get("kira_ready")),
            "duplicate_physical_groups": boot.get("duplicate_physical_groups"),
            "raw_physical_to_unique_mapping": boot.get("raw_physical_to_unique_mapping"),
            "auxiliary_names": boot.get("auxiliary_names"),
            "reuse_hits": hits,
        }

        if hits:
            if len(hits) != 1:
                errors.append(
                    f"{representative}: ambiguous reuse under current scope, hits={hits}"
                )
                step["status"] = "halted_ambiguous_reuse"
                steps.append(step)
                break
            family_id = hits[0]
            witnesses, witness_errors = _reuse_witnesses_for_family(
                reuse, family_id, candidate_ids
            )
            if witness_errors:
                errors.extend(witness_errors)
                step["status"] = "halted_incomplete_reuse_witness"
                steps.append(step)
                break
            if family_id not in registry:
                errors.append(f"{representative}: reuse target {family_id} is not registered")
                step["status"] = "halted_unknown_reuse_target"
                steps.append(step)
                break
            registry[family_id]["confirmed_diagrams"].extend(candidate_ids)
            for did in candidate_ids:
                diagram_records[did] = {
                    "diagram_id": did,
                    "canonical_integral_family_id": family_id,
                    "representative": registry[family_id]["representative"],
                    "promotion_mode": "reuse_existing_family",
                    "witness": witnesses[did],
                }
            step["status"] = "reused_existing_family"
            step["canonical_family_id"] = family_id
        else:
            new_errors = _validate_new_family_bootstrap(boot)
            if new_errors:
                errors.extend(new_errors)
                step["status"] = "halted_new_family_validation"
                steps.append(step)
                break

            family_id = str(boot.get("family_candidate_id"))
            expected_family_id = f"{representative}_full"
            if family_id != expected_family_id:
                errors.append(
                    f"{representative}: unexpected new family ID {family_id}, expected {expected_family_id}"
                )
                step["status"] = "halted_bad_family_id"
                steps.append(step)
                break
            if family_id in registry:
                errors.append(f"{representative}: new family ID already registered: {family_id}")
                step["status"] = "halted_duplicate_family_id"
                steps.append(step)
                break

            boot_records = _bootstrap_record_by_id(boot)
            registry[family_id] = {
                "representative": representative,
                "confirmed_diagrams": list(candidate_ids),
                "master_basis_id": None,
                "kira_reusable": True,
                "kira_ready": True,
                "duplicate_physical_groups": boot.get("duplicate_physical_groups"),
                "raw_physical_to_unique_mapping": boot.get("raw_physical_to_unique_mapping"),
                "auxiliary_names": boot.get("auxiliary_names"),
                "canonical_denominator_count": boot.get("canonical_denominator_count"),
                "canonical_scalar_product_rank": boot.get("canonical_scalar_product_rank"),
                "canonical_propagators": boot.get("canonical_propagators"),
                "equivalence_audit_pass": True,
                "discovery_mode": "bootstrap_new_family",
            }
            representatives.append(representative)
            family_order.append(family_id)
            for did in candidate_ids:
                diagram_records[did] = {
                    "diagram_id": did,
                    "canonical_integral_family_id": family_id,
                    "representative": representative,
                    "promotion_mode": "bootstrap_new_family",
                    "witness": boot_records[did]["witness"],
                }
            step["status"] = "promoted_new_family"
            step["canonical_family_id"] = family_id

        confirmed_ids.update(candidate_ids)
        step["confirmed_after_step"] = len(confirmed_ids)
        step["family_count_after_step"] = len(registry)
        steps.append(step)

    missing_quenched = sorted(quenched_ids - confirmed_ids, key=lambda x: int(x[1:]))
    extra_confirmed = sorted(confirmed_ids - quenched_ids)
    if missing_quenched:
        errors.append(f"unclassified quenched diagrams remain: {missing_quenched}")
    if extra_confirmed:
        errors.append(f"non-quenched IDs were promoted: {extra_confirmed}")

    family_members = [did for entry in registry.values() for did in entry["confirmed_diagrams"]]
    counts = Counter(family_members)
    duplicate_membership = sorted(did for did, count in counts.items() if count != 1)
    if duplicate_membership:
        errors.append(f"canonical-family membership is not unique: {duplicate_membership}")

    ordered_records = [
        diagram_records[did]
        for did in sorted(diagram_records, key=lambda x: int(x[1:]))
    ]

    return {
        "transform_scope": TRANSFORM_SCOPE,
        "quenched_diagram_count": len(quenched_ids),
        "confirmed_quenched_count": len(confirmed_ids & quenched_ids),
        "unresolved_quenched_count": len(missing_quenched),
        "canonical_family_count": len(registry),
        "family_order": family_order,
        "canonical_registry": registry,
        "steps": steps,
        "records": ordered_records,
        "errors": errors,
        "audit_pass": not errors,
        "interpretation": (
            "All promotions are backed by executable exact witnesses. New-family decisions are "
            "only with respect to the current transform scope; a broader affine/GL(Z) search may "
            "merge some families later without invalidating the present exact mappings."
        ),
    }
