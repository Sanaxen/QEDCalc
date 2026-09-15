"""Canonical-family autodiscovery for VP4A/VP4B/VP4C and VP22.

The raw denominator lists are transcribed from the complete three-loop vertex
formula sheet.  Repeated photon/electron denominators are retained in the raw
list and collapsed only when constructing the canonical Kira family, so their
multiplicity becomes a propagator power rather than a fake extra denominator.

Equivalence search is intentionally conservative: open-line reflection plus a
signed permutation of the three loop momenta.  Every promoted mapping requires
exact SymPy equality and a 12-entry full-rank scalar-product basis.
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
from three_loop.q01_family_equivalence import _square, _transform_vector, _vec

TRANSFORM_SCOPE = "open-line reflection + signed loop-momentum permutation"
SUPPORTED_IDS = ("VP4A", "VP4B", "VP4C", "VP22")


@dataclass(frozen=True)
class VPRemainingWitness:
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


def _m(v: dict[str, sp.Expr]) -> tuple[bool, dict[str, sp.Expr]]:
    return True, v


def _g(v: dict[str, sp.Expr]) -> tuple[bool, dict[str, sp.Expr]]:
    return False, v


def _formula_denominator_specs(diagram_id: str) -> list[tuple[bool, dict[str, sp.Expr]]]:
    """Return raw propagators in the order they occur in the formula sheet."""
    ppk = _vec(p=1, q=1, k=-1)
    pk = _vec(p=1, k=-1)
    k = _vec(k=1)
    r = _vec(r=1)

    if diagram_id == "VP4A":
        return [
            _m(ppk), _m(pk), _g(k),
            _m(_vec(l=1, k=1)),
            _m(_vec(l=1, k=1, r=1)),
            _m(_vec(l=1, k=1)),
            _m(_vec(l=1)),
            _g(r), _g(k),
        ]
    if diagram_id == "VP4B":
        return [
            _m(ppk), _m(pk), _g(k),
            _m(_vec(l=1, k=1)),
            _m(_vec(l=1, k=1, r=1)),
            _m(_vec(l=1, r=1)),
            _m(_vec(l=1)),
            _g(r), _g(k),
        ]
    if diagram_id == "VP4C":
        return [
            _m(ppk), _m(pk), _g(k),
            _m(_vec(l=1, k=1)),
            _m(_vec(l=1)),
            _m(_vec(l=1, r=1)),
            _m(_vec(l=1)),
            _g(r), _g(k),
        ]
    if diagram_id == "VP22":
        return [
            _m(ppk), _m(pk), _g(k),
            _m(_vec(l=1, k=1)), _m(_vec(l=1)),
            _g(k),
            _m(_vec(r=1, k=1)), _m(_vec(r=1)),
            _g(k),
        ]
    raise ValueError(f"unsupported VP remainder diagram: {diagram_id}")


def _spec_expr(spec: tuple[bool, dict[str, sp.Expr]]) -> sp.Expr:
    massive, vec = spec
    m2 = sp.Symbol("m2")
    return sp.expand((m2 if massive else 0) - _square(vec))


def physical_denominators(diagram_id: str) -> list[sp.Expr]:
    return [_spec_expr(spec) for spec in _formula_denominator_specs(diagram_id)]


def _transform_specs(
    diagram_id: str,
    loop_map: dict[str, tuple[str, int]],
    reflected: bool,
) -> list[sp.Expr]:
    m2 = sp.Symbol("m2")
    out: list[sp.Expr] = []
    for massive, vec in _formula_denominator_specs(diagram_id):
        transformed = _transform_vector(vec, loop_map=loop_map, reflected=reflected)
        out.append(sp.expand((m2 if massive else 0) - _square(transformed)))
    return out


def _auxiliary_candidates() -> list[tuple[str, dict[str, sp.Expr], sp.Expr]]:
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


def _complete_auxiliaries(
    physical: list[sp.Expr],
) -> tuple[list[str], list[dict[str, sp.Expr]], list[sp.Expr]]:
    names: list[str] = []
    vecs: list[dict[str, sp.Expr]] = []
    exprs: list[sp.Expr] = []
    rank = _rank(physical)
    for name, vec, expr in _auxiliary_candidates():
        new_rank = _rank(physical + exprs + [expr])
        if new_rank > rank:
            names.append(name)
            vecs.append(vec)
            exprs.append(expr)
            rank = new_rank
        if rank == 12:
            break
    if rank != 12:
        raise ValueError(
            f"failed to span VP2/VP22 scalar-product space: "
            f"physical_rank={_rank(physical)} final_rank={rank} auxiliaries={names}"
        )
    return names, vecs, exprs


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
    return mapping if used == set(range(len(target_unique))) else None


def _basis(diagram_id: str):
    raw = physical_denominators(diagram_id)
    unique, mapping, duplicates = deduplicate_exact_denominators(raw)
    aux_names, aux_vecs, aux_exprs = _complete_auxiliaries(unique)
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


def find_family_witness(
    candidate_id: str,
    reference_id: str,
    reference_unique: list[sp.Expr],
    auxiliary_vecs: list[dict[str, sp.Expr]],
    auxiliary_exprs: list[sp.Expr],
) -> VPRemainingWitness | None:
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
                loops = {
                    src: (("-" if sign < 0 else "") + dst)
                    for src, (dst, sign) in loop_map.items()
                }
                external = {"p": "p+q", "q": "-q"} if reflected else {"p": "p", "q": "q"}
                return VPRemainingWitness(
                    diagram_id=candidate_id,
                    representative=reference_id,
                    reflection=reflected,
                    loop_momentum_transform=loops,
                    external_momentum_transform=external,
                    physical_to_canonical_mapping=mapping,
                    propagator_exact_match=exact,
                )
    return None


def audit_vp2_double_family_autodiscovery(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_id = {str(row["id"]): row for row in rows}
    expected = [did for did in SUPPORTED_IDS if did in by_id]
    errors: list[str] = []
    if set(expected) != set(SUPPORTED_IDS):
        errors.append(f"missing VP2/VP22 topology IDs: {sorted(set(SUPPORTED_IDS) - set(expected))}")

    representatives: list[str] = []
    registry: dict[str, dict[str, Any]] = {}
    records: list[dict[str, Any]] = []
    steps: list[dict[str, Any]] = []

    for did in expected:
        if errors:
            break
        unique, aux_vecs, aux_exprs, info = _basis(did)
        if info["unique_physical_propagator_count"] != info["unique_physical_scalar_product_rank"]:
            errors.append(
                f"{did}: residual non-duplicate dependence: "
                f"unique={info['unique_physical_propagator_count']} "
                f"rank={info['unique_physical_scalar_product_rank']}"
            )
            break
        if info["canonical_denominator_count"] != 12 or info["canonical_scalar_product_rank"] != 12:
            errors.append(
                f"{did}: canonical basis is not 12-entry full rank: "
                f"count={info['canonical_denominator_count']} rank={info['canonical_scalar_product_rank']}"
            )
            break

        hits: list[tuple[str, VPRemainingWitness]] = []
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
                "discovery_mode": "vp2_double_bootstrap_new_family",
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

    confirmed_ids = {str(rec["diagram_id"]) for rec in records}
    missing = [did for did in SUPPORTED_IDS if did not in confirmed_ids]
    if missing and not errors:
        errors.append(f"unclassified VP2/VP22 diagrams remain: {missing}")

    return {
        "transform_scope": TRANSFORM_SCOPE,
        "diagram_count": len(SUPPORTED_IDS),
        "confirmed_count": len(confirmed_ids),
        "unresolved_count": len(missing),
        "canonical_family_count": len(registry),
        "canonical_registry": registry,
        "steps": steps,
        "records": records,
        "errors": errors,
        "audit_pass": not errors,
        "formula_source": "3loop_vertex_72_complete_equations.md sections VP4A-VP4C and VP22",
    }
