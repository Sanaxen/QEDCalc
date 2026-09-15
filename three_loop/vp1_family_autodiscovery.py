"""Automatic canonical-family discovery for the 12 one-loop vacuum-polarization insertions.

This is the first non-quenched family builder. A VP1 diagram contains

* the open-line electron propagators,
* the two open-line photon propagators, and
* the two massive electron propagators of the one-loop VP bubble.

The bubble loop is routed with the remaining loop momentum ``r`` and, for an
insertion on photon momentum ``a``, contributes denominators based on ``r`` and
``r+a``. Exact family equivalence is searched under open-line reflection plus
signed permutations of the three loop momenta. Every promotion is verified by
exact SymPy equality and a full-rank 12-denominator canonical basis.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from itertools import permutations, product
from typing import Any

import sympy as sp

from three_loop.canonical_family_bootstrap import (
    LOOPS,
    _pullback_aux_vector,
    deduplicate_exact_denominators,
    physical_denominator_relations,
)
from three_loop.integral_family_classification import candidate_classes
from three_loop.q01_family_equivalence import _electron_momenta, _square, _transform_vector, _vec

TRANSFORM_SCOPE = "open-line reflection + signed loop-momentum permutation"


@dataclass(frozen=True)
class VP1Witness:
    diagram_id: str
    representative: str
    reflection: bool
    loop_momentum_transform: dict[str, str]
    external_momentum_transform: dict[str, str]
    physical_to_canonical_mapping: list[int]
    propagator_exact_match: list[bool]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _rank(expressions: list[sp.Expr]) -> int:
    from three_loop.canonical_family_bootstrap import _rank as bootstrap_rank
    return int(bootstrap_rank(expressions))


def _vp1_denominator_specs(row: dict[str, Any]) -> list[tuple[bool, dict[str, sp.Expr]]]:
    """Return ``(massive, momentum-vector)`` physical denominator specifications."""
    if row.get("family") != "vp1_insert":
        raise ValueError(f"{row.get('id')}: expected family=vp1_insert")
    insert_on = str(row.get("insert_on"))
    edge_labels = [str(edge.get("label")) for edge in row.get("photon_edges", [])]
    if len(edge_labels) != 2 or insert_on not in edge_labels:
        raise ValueError(
            f"{row.get('id')}: VP1 topology must contain two photon edges and a valid insert_on"
        )

    specs: list[tuple[bool, dict[str, sp.Expr]]] = []
    for vec in _electron_momenta(row):
        specs.append((True, vec))
    for label in edge_labels:
        specs.append((False, _vec(**{label: 1})))

    specs.append((True, _vec(r=1)))
    bubble_shift = _vec(r=1)
    bubble_shift[insert_on] += 1
    specs.append((True, bubble_shift))
    return specs


def _spec_expr(spec: tuple[bool, dict[str, sp.Expr]]) -> sp.Expr:
    massive, vec = spec
    m2 = sp.Symbol("m2")
    return sp.expand((m2 if massive else 0) - _square(vec))


def vp1_physical_denominators(row: dict[str, Any]) -> list[sp.Expr]:
    return [_spec_expr(spec) for spec in _vp1_denominator_specs(row)]


def _transform_specs(
    row: dict[str, Any],
    loop_map: dict[str, tuple[str, int]],
    reflected: bool,
) -> list[sp.Expr]:
    out: list[sp.Expr] = []
    m2 = sp.Symbol("m2")
    for massive, vec in _vp1_denominator_specs(row):
        transformed = _transform_vector(vec, loop_map=loop_map, reflected=reflected)
        out.append(sp.expand((m2 if massive else 0) - _square(transformed)))
    return out


def _vp1_auxiliary_candidates() -> list[tuple[str, dict[str, sp.Expr], sp.Expr]]:
    """Quadratic auxiliary candidates spanning the full VP1 scalar-product space.

    The quenched candidate set is insufficient for VP insertions because the
    explicit bubble can leave an independent loop.p scalar product. Include
    loop+p as well as loop+q and loop-loop combinations in deterministic order.
    """
    specs = [
        ("(k-l)^2", _vec(k=1, l=-1)),
        ("(k-r)^2", _vec(k=1, r=-1)),
        ("(l-r)^2", _vec(l=1, r=-1)),
        ("(k+p)^2", _vec(k=1, p=1)),
        ("(l+p)^2", _vec(l=1, p=1)),
        ("(r+p)^2", _vec(r=1, p=1)),
        ("(k+q)^2", _vec(k=1, q=1)),
        ("(l+q)^2", _vec(l=1, q=1)),
        ("(r+q)^2", _vec(r=1, q=1)),
        ("(k+l)^2", _vec(k=1, l=1)),
        ("(k+r)^2", _vec(k=1, r=1)),
        ("(l+r)^2", _vec(l=1, r=1)),
    ]
    return [(name, vec, sp.expand(_square(vec))) for name, vec in specs]


def _complete_vp1_auxiliaries(
    physical: list[sp.Expr],
) -> tuple[list[str], list[dict[str, sp.Expr]], list[sp.Expr]]:
    selected_names: list[str] = []
    selected_vecs: list[dict[str, sp.Expr]] = []
    selected_exprs: list[sp.Expr] = []
    rank = _rank(physical)
    for name, vec, expr in _vp1_auxiliary_candidates():
        new_rank = _rank(physical + selected_exprs + [expr])
        if new_rank > rank:
            selected_names.append(name)
            selected_vecs.append(vec)
            selected_exprs.append(expr)
            rank = new_rank
        if rank == 12:
            break
    if rank != 12:
        raise ValueError(
            f"failed to span VP1 scalar-product space: physical_rank={_rank(physical)}, "
            f"final_rank={rank}, auxiliaries={selected_names}"
        )
    return selected_names, selected_vecs, selected_exprs


def _exact_mapping_allow_duplicates(
    source: list[sp.Expr], target_unique: list[sp.Expr]
) -> list[int] | None:
    mapping: list[int] = []
    used: set[int] = set()
    for expr in source:
        matches = [j for j, target in enumerate(target_unique) if sp.expand(expr - target) == 0]
        if len(matches) != 1:
            return None
        mapping.append(matches[0] + 1)
        used.add(matches[0])
    if used != set(range(len(target_unique))):
        return None
    return mapping


def find_vp1_family_witness(
    candidate: dict[str, Any], reference: dict[str, Any],
    reference_unique_physical: list[sp.Expr],
    auxiliary_vecs: list[dict[str, sp.Expr]], auxiliary_exprs: list[sp.Expr],
) -> VP1Witness | None:
    """Find an exact VP1 family map within the conservative transform scope."""
    for reflected in (False, True):
        for perm in permutations(LOOPS):
            relabel = dict(zip(LOOPS, perm))
            for signs in product((-1, 1), repeat=3):
                loop_map = {src: (relabel[src], signs[i]) for i, src in enumerate(LOOPS)}
                transformed = _transform_specs(candidate, loop_map, reflected)
                mapping = _exact_mapping_allow_duplicates(transformed, reference_unique_physical)
                if mapping is None:
                    continue
                exact = [True] * len(reference_unique_physical)
                for vec, target in zip(auxiliary_vecs, auxiliary_exprs):
                    pulled = _pullback_aux_vector(vec, loop_map, reflected)
                    check = _transform_vector(pulled, loop_map=loop_map, reflected=reflected)
                    exact.append(sp.expand(_square(check) - target) == 0)
                if not all(exact):
                    continue
                loops = {
                    src: (("-" if sign < 0 else "") + dst)
                    for src, (dst, sign) in loop_map.items()
                }
                external = {"p": "p+q", "q": "-q"} if reflected else {"p": "p", "q": "q"}
                return VP1Witness(
                    diagram_id=str(candidate["id"]), representative=str(reference["id"]),
                    reflection=reflected, loop_momentum_transform=loops,
                    external_momentum_transform=external,
                    physical_to_canonical_mapping=mapping,
                    propagator_exact_match=exact,
                )
    return None


def _vp1_structural_groups(rows: list[dict[str, Any]]) -> list[list[str]]:
    by_id = {str(row["id"]): row for row in rows}
    groups: list[list[str]] = []
    for ids in candidate_classes(rows).values():
        vpids = [did for did in ids if by_id[did].get("family") == "vp1_insert"]
        if vpids:
            groups.append(sorted(vpids, key=lambda x: int(x[2:])))
    return sorted(groups, key=lambda ids: int(ids[0][2:]))


def _basis_for_reference(reference: dict[str, Any]):
    physical = vp1_physical_denominators(reference)
    unique, mapping, duplicates = deduplicate_exact_denominators(physical)
    aux_names, aux_vecs, aux_exprs = _complete_vp1_auxiliaries(unique)
    canonical = unique + aux_exprs
    info = {
        "raw_physical_propagator_count": len(physical),
        "raw_physical_scalar_product_rank": _rank(physical),
        "physical_denominator_relations": physical_denominator_relations(physical),
        "duplicate_physical_groups": duplicates,
        "raw_physical_to_unique_mapping": mapping,
        "unique_physical_propagator_count": len(unique),
        "unique_physical_scalar_product_rank": _rank(unique),
        "auxiliary_names": aux_names,
        "canonical_denominator_count": len(canonical),
        "canonical_scalar_product_rank": _rank(canonical),
        "canonical_propagators": [str(expr) for expr in canonical],
    }
    return unique, aux_vecs, aux_exprs, info


def audit_vp1_family_autodiscovery(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_id = {str(row["id"]): row for row in rows}
    groups = _vp1_structural_groups(rows)
    expected_ids = {str(row["id"]) for row in rows if row.get("family") == "vp1_insert"}
    errors: list[str] = []
    confirmed: set[str] = set()
    representatives: list[str] = []
    registry: dict[str, dict[str, Any]] = {}
    records: dict[str, dict[str, Any]] = {}
    steps: list[dict[str, Any]] = []
    if len(expected_ids) != 12:
        errors.append(f"expected 12 vp1_insert diagrams, found {len(expected_ids)}")

    unresolved_groups = [list(group) for group in groups]
    while unresolved_groups and not errors:
        group = unresolved_groups.pop(0)
        if any(did in confirmed for did in group):
            continue
        rep_id = group[0]
        rep = by_id[rep_id]
        unique, aux_vecs, aux_exprs, basis = _basis_for_reference(rep)
        if basis["unique_physical_propagator_count"] != basis["unique_physical_scalar_product_rank"]:
            errors.append(f"{rep_id}: residual non-duplicate dependence in physical denominators")
            break
        if basis["canonical_denominator_count"] != 12 or basis["canonical_scalar_product_rank"] != 12:
            errors.append(
                f"{rep_id}: canonical basis is not 12-entry full rank: "
                f"count={basis['canonical_denominator_count']} rank={basis['canonical_scalar_product_rank']}"
            )
            break

        reuse_hits: list[tuple[str, VP1Witness]] = []
        for old_rep in representatives:
            old_unique, old_aux_vecs, old_aux_exprs, _ = _basis_for_reference(by_id[old_rep])
            witness = find_vp1_family_witness(rep, by_id[old_rep], old_unique, old_aux_vecs, old_aux_exprs)
            if witness is not None:
                reuse_hits.append((f"{old_rep}_full", witness))
        if len(reuse_hits) > 1:
            errors.append(f"{rep_id}: ambiguous reuse under current scope: {[f for f, _ in reuse_hits]}")
            break

        if reuse_hits:
            family_id, _ = reuse_hits[0]
            reference_id = str(registry[family_id]["representative"])
            ref_unique, ref_aux_vecs, ref_aux_exprs, _ = _basis_for_reference(by_id[reference_id])
            witnesses: dict[str, VP1Witness] = {}
            for did in group:
                witness = find_vp1_family_witness(by_id[did], by_id[reference_id], ref_unique, ref_aux_vecs, ref_aux_exprs)
                if witness is None:
                    errors.append(f"{did}: class representative reuses {family_id}, but member has no exact witness")
                    break
                witnesses[did] = witness
            if errors:
                break
            registry[family_id]["confirmed_diagrams"].extend(group)
            status = "reused_existing_family"
        else:
            family_id = f"{rep_id}_full"
            representatives.append(rep_id)
            witnesses = {}
            for did in group:
                witness = find_vp1_family_witness(by_id[did], rep, unique, aux_vecs, aux_exprs)
                if witness is None:
                    errors.append(f"{did}: no exact VP1 witness to {rep_id}")
                    break
                witnesses[did] = witness
            if errors:
                break
            registry[family_id] = {
                "representative": rep_id,
                "confirmed_diagrams": list(group),
                "master_basis_id": None,
                "kira_reusable": True,
                "kira_ready": True,
                "duplicate_physical_groups": basis["duplicate_physical_groups"],
                "raw_physical_to_unique_mapping": basis["raw_physical_to_unique_mapping"],
                "auxiliary_names": basis["auxiliary_names"],
                "canonical_denominator_count": basis["canonical_denominator_count"],
                "canonical_scalar_product_rank": basis["canonical_scalar_product_rank"],
                "canonical_propagators": basis["canonical_propagators"],
                "equivalence_audit_pass": True,
                "discovery_mode": "vp1_bootstrap_new_family",
            }
            status = "promoted_new_family"

        for did in group:
            witness = witnesses[did]
            if not all(witness.propagator_exact_match):
                errors.append(f"{did}: VP1 P1..P12 witness is not exact")
                break
            records[did] = {
                "diagram_id": did,
                "canonical_integral_family_id": family_id,
                "representative": str(registry[family_id]["representative"]),
                "promotion_mode": status,
                "witness": witness.to_dict(),
            }
        if errors:
            break
        confirmed.update(group)
        steps.append({
            "representative": rep_id,
            "candidate_ids": list(group),
            "status": status,
            "canonical_family_id": family_id,
            "confirmed_after_step": len(confirmed),
            "family_count_after_step": len(registry),
        })

    missing = sorted(expected_ids - confirmed, key=lambda x: int(x[2:]))
    if missing:
        errors.append(f"unclassified vp1_insert diagrams remain: {missing}")
    return {
        "transform_scope": TRANSFORM_SCOPE,
        "vp1_diagram_count": len(expected_ids),
        "confirmed_vp1_count": len(confirmed & expected_ids),
        "unresolved_vp1_count": len(missing),
        "canonical_family_count": len(registry),
        "canonical_registry": registry,
        "steps": steps,
        "records": [records[did] for did in sorted(records, key=lambda x: int(x[2:]))],
        "errors": errors,
        "audit_pass": not errors,
        "interpretation": (
            "VP1 physical denominators include the explicit two-line massive fermion bubble. "
            "The VP1-specific auxiliary search spans loop-loop, loop.p, and loop.q scalar products. "
            "Family equivalence is proven only within reflection plus signed loop-permutation scope."
        ),
    }
