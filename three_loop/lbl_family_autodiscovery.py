"""Canonical-family autodiscovery for the six external light-by-light diagrams.

The denominator routing is transcribed from 3loop_vertex_72_complete_equations.md.
All six diagrams share the open electron line and three exchanged photons
K1=k, K2=l, K3=q-k-l.  They differ only by the order in which K1,K2,K3 enter
the closed electron loop.  For order (Ka,Kb,Kc), the four massive closed-loop
momenta are r, r+Ka, r+Ka+Kb, r+q.

Promotion is conservative: exact SymPy denominator equality under open-line
reflection plus signed permutations of k,l,r, followed by a full-rank
12-denominator canonical basis check.
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
from three_loop.q01_family_equivalence import _add, _square, _transform_vector, _vec
from three_loop.vp1_family_autodiscovery import _complete_vp1_auxiliaries

TRANSFORM_SCOPE = "open-line reflection + signed loop-momentum permutation"
SUPPORTED_IDS = tuple(f"LBL{i:02d}" for i in range(1, 7))

ORDERS = {
    "LBL01": ("K1", "K2", "K3"),
    "LBL02": ("K1", "K3", "K2"),
    "LBL03": ("K2", "K1", "K3"),
    "LBL04": ("K2", "K3", "K1"),
    "LBL05": ("K3", "K1", "K2"),
    "LBL06": ("K3", "K2", "K1"),
}


@dataclass(frozen=True)
class LBLWitness:
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


def _m(v):
    return True, v


def _g(v):
    return False, v


def _kvecs() -> dict[str, dict[str, sp.Expr]]:
    return {
        "K1": _vec(k=1),
        "K2": _vec(l=1),
        "K3": _vec(q=1, k=-1, l=-1),
    }


def _formula_denominator_specs(diagram_id: str):
    if diagram_id not in ORDERS:
        raise ValueError(f"unsupported LBL diagram: {diagram_id}")
    K = _kvecs()
    a, b, _ = ORDERS[diagram_id]

    # Open line: p'-k and p'-k-l; exchanged photons k,l,q-k-l.
    specs = [
        _m(_vec(p=1, q=1, k=-1)),
        _m(_vec(p=1, q=1, k=-1, l=-1)),
        _g(K["K1"]), _g(K["K2"]), _g(K["K3"]),
    ]

    # Closed loop: r, r+Ka, r+Ka+Kb, r+q.
    r = _vec(r=1)
    specs.extend([
        _m(r),
        _m(_add(r, K[a])),
        _m(_add(r, K[a], K[b])),
        _m(_vec(r=1, q=1)),
    ])
    return specs


def _spec_expr(spec):
    massive, vec = spec
    m2 = sp.Symbol("m2")
    return sp.expand((m2 if massive else 0) - _square(vec))


def physical_denominators(diagram_id: str) -> list[sp.Expr]:
    return [_spec_expr(spec) for spec in _formula_denominator_specs(diagram_id)]


def _transform_specs(diagram_id: str, loop_map, reflected: bool) -> list[sp.Expr]:
    m2 = sp.Symbol("m2")
    out = []
    for massive, vec in _formula_denominator_specs(diagram_id):
        t = _transform_vector(vec, loop_map=loop_map, reflected=reflected)
        out.append(sp.expand((m2 if massive else 0) - _square(t)))
    return out


def _exact_mapping_allow_duplicates(source, target_unique):
    mapping = []
    used = set()
    for expr in source:
        matches = [j for j, target in enumerate(target_unique) if sp.expand(expr - target) == 0]
        if len(matches) != 1:
            return None
        mapping.append(matches[0] + 1)
        used.add(matches[0])
    return mapping if used == set(range(len(target_unique))) else None


def _basis(diagram_id: str):
    raw = physical_denominators(diagram_id)
    unique, mapping, duplicates = deduplicate_exact_denominators(raw)
    aux_names, aux_vecs, aux_exprs = _complete_vp1_auxiliaries(unique)
    canonical = unique + aux_exprs
    info = {
        "raw_physical_propagator_count": len(raw),
        "raw_physical_scalar_product_rank": _rank(raw),
        "physical_denominator_relations": physical_denominator_relations(raw),
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


def find_family_witness(candidate_id, reference_id, reference_unique, auxiliary_vecs, auxiliary_exprs):
    for reflected in (False, True):
        for perm in permutations(LOOPS):
            relabel = dict(zip(LOOPS, perm))
            for signs in product((-1, 1), repeat=3):
                loop_map = {src: (relabel[src], signs[i]) for i, src in enumerate(LOOPS)}
                transformed = _transform_specs(candidate_id, loop_map, reflected)
                mapping = _exact_mapping_allow_duplicates(transformed, reference_unique)
                if mapping is None:
                    continue
                exact = [True] * len(reference_unique)
                for vec, target in zip(auxiliary_vecs, auxiliary_exprs):
                    pulled = _pullback_aux_vector(vec, loop_map, reflected)
                    check = _transform_vector(pulled, loop_map=loop_map, reflected=reflected)
                    exact.append(sp.expand(_square(check) - target) == 0)
                if not all(exact):
                    continue
                loops = {src: (("-" if sign < 0 else "") + dst) for src, (dst, sign) in loop_map.items()}
                external = {"p": "p+q", "q": "-q"} if reflected else {"p": "p", "q": "q"}
                return LBLWitness(
                    diagram_id=candidate_id,
                    representative=reference_id,
                    reflection=reflected,
                    loop_momentum_transform=loops,
                    external_momentum_transform=external,
                    physical_to_canonical_mapping=mapping,
                    propagator_exact_match=exact,
                )
    return None


def audit_lbl_family_autodiscovery(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_id = {str(row["id"]): row for row in rows}
    errors: list[str] = []
    missing_inventory = [did for did in SUPPORTED_IDS if did not in by_id]
    if missing_inventory:
        errors.append(f"missing LBL topology IDs: {missing_inventory}")

    representatives: list[str] = []
    registry: dict[str, dict[str, Any]] = {}
    records: list[dict[str, Any]] = []
    steps: list[dict[str, Any]] = []

    for did in SUPPORTED_IDS:
        if errors:
            break
        unique, aux_vecs, aux_exprs, info = _basis(did)
        if info["unique_physical_propagator_count"] != info["unique_physical_scalar_product_rank"]:
            errors.append(
                f"{did}: residual non-duplicate dependence: unique={info['unique_physical_propagator_count']} "
                f"rank={info['unique_physical_scalar_product_rank']}"
            )
            break
        if info["canonical_denominator_count"] != 12 or info["canonical_scalar_product_rank"] != 12:
            errors.append(
                f"{did}: canonical basis is not 12-entry full rank: "
                f"count={info['canonical_denominator_count']} rank={info['canonical_scalar_product_rank']}"
            )
            break

        hits = []
        for rep in representatives:
            old_unique, old_aux_vecs, old_aux_exprs, _ = _basis(rep)
            witness = find_family_witness(did, rep, old_unique, old_aux_vecs, old_aux_exprs)
            if witness is not None:
                hits.append((f"{rep}_full", witness))
        if len(hits) > 1:
            errors.append(f"{did}: ambiguous reuse hits {[family for family, _ in hits]}")
            break

        if hits:
            family_id, witness = hits[0]
            registry[family_id]["confirmed_diagrams"].append(did)
            status = "reused_existing_family"
        else:
            family_id = f"{did}_full"
            witness = find_family_witness(did, did, unique, aux_vecs, aux_exprs)
            if witness is None:
                errors.append(f"{did}: identity family witness failed")
                break
            representatives.append(did)
            registry[family_id] = {
                "representative": did,
                "confirmed_diagrams": [did],
                "master_basis_id": None,
                "kira_reusable": True,
                "kira_ready": True,
                "duplicate_physical_groups": info["duplicate_physical_groups"],
                "raw_physical_to_unique_mapping": info["raw_physical_to_unique_mapping"],
                "auxiliary_names": info["auxiliary_names"],
                "canonical_denominator_count": info["canonical_denominator_count"],
                "canonical_scalar_product_rank": info["canonical_scalar_product_rank"],
                "canonical_propagators": info["canonical_propagators"],
                "equivalence_audit_pass": True,
                "discovery_mode": "lbl_bootstrap_new_family",
            }
            status = "promoted_new_family"

        if not all(witness.propagator_exact_match):
            errors.append(f"{did}: non-exact P1..P12 witness")
            break
        records.append({
            "diagram_id": did,
            "canonical_integral_family_id": family_id,
            "representative": str(registry[family_id]["representative"]),
            "promotion_mode": status,
            "witness": witness.to_dict(),
        })
        steps.append({
            "representative": did,
            "candidate_ids": [did],
            "status": status,
            "canonical_family_id": family_id,
            "confirmed_after_step": len(records),
            "family_count_after_step": len(registry),
        })

    confirmed = {str(rec["diagram_id"]) for rec in records}
    unresolved = [did for did in SUPPORTED_IDS if did not in confirmed]
    if unresolved and not errors:
        errors.append(f"unclassified LBL diagrams remain: {unresolved}")

    return {
        "transform_scope": TRANSFORM_SCOPE,
        "diagram_count": len(SUPPORTED_IDS),
        "confirmed_count": len(confirmed),
        "unresolved_count": len(unresolved),
        "canonical_family_count": len(registry),
        "canonical_registry": registry,
        "steps": steps,
        "records": records,
        "errors": errors,
        "audit_pass": not errors,
        "formula_source": "3loop_vertex_72_complete_equations.md LBL01-LBL06",
    }
