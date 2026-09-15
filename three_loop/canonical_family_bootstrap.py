"""Bootstrap the next unresolved quenched integral-family candidate.

This module is intentionally algebraic and conservative. It does not claim a
new Kira family merely from graph topology. For a chosen representative it

1. derives the nine physical scalar denominators from the topology inventory;
2. checks whether those lines already map to Q01 under the currently allowed
   reflection + signed loop-relabel transform class;
3. measures the physical scalar-product rank and records any left-null
   relations among the physical denominators;
4. greedily selects as many quadratic auxiliaries as are actually required to
   span the 12-dimensional loop scalar-product space;
5. proves every member of the same structural candidate class against the full
   generated denominator set by exact SymPy equality.

A rank-deficient physical set is deliberately *not* forced into a fake
"9 physical + 3 auxiliary = 12" Kira family.  Such a case is reported as an
overcomplete algebraic candidate that requires a partial-fraction/family-split
step before a Kira-ready canonical family is registered.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from itertools import permutations, product
from math import gcd
from functools import reduce
from typing import Any, Iterable

import sympy as sp

from qedcalc.operations.ibp import sp_atom
from three_loop.integral_family import q01_denominator_expressions
from three_loop.integral_family_classification import candidate_classes
from three_loop.q01_family_equivalence import _electron_momenta, _vec, _square, _transform_vector

LOOPS = ("k", "l", "r")
SP_BASIS = (
    sp_atom("k", "k"), sp_atom("l", "l"), sp_atom("r", "r"),
    sp_atom("k", "l"), sp_atom("k", "r"), sp_atom("l", "r"),
    sp_atom("k", "p"), sp_atom("l", "p"), sp_atom("p", "r"),
    sp_atom("k", "q"), sp_atom("l", "q"), sp_atom("q", "r"),
)


@dataclass(frozen=True)
class FamilyWitness:
    diagram_id: str
    representative: str
    reflection: bool
    loop_momentum_transform: dict[str, str]
    external_momentum_transform: dict[str, str]
    physical_propagator_permutation: list[int]
    propagator_exact_match: list[bool]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def topology_physical_denominators(row: dict[str, Any]) -> list[sp.Expr]:
    """Return open-line electron denominators followed by photon denominators."""
    m2 = sp.Symbol("m2")
    electron = [sp.expand(m2 - _square(v)) for v in _electron_momenta(row)]
    photon = [
        sp.expand(-_square(_vec(**{str(edge["label"]): 1})))
        for edge in row.get("photon_edges", [])
    ]
    return electron + photon


def _sp_matrix(expressions: list[sp.Expr]) -> sp.Matrix:
    return sp.Matrix([
        [sp.expand(expr).coeff(atom) for atom in SP_BASIS]
        for expr in expressions
    ])


def _rank(expressions: list[sp.Expr]) -> int:
    return int(_sp_matrix(expressions).rank())


def _normalize_null_vector(vec: sp.Matrix) -> list[sp.Expr]:
    vals = [sp.Rational(v) for v in list(vec)]
    denoms = [int(v.q) for v in vals]
    lcm = 1
    for d in denoms:
        lcm = sp.ilcm(lcm, d)
    ints = [int(v * lcm) for v in vals]
    nonzero = [abs(v) for v in ints if v]
    if nonzero:
        common = reduce(gcd, nonzero)
        ints = [v // common for v in ints]
    first = next((v for v in ints if v), 1)
    if first < 0:
        ints = [-v for v in ints]
    return [sp.Integer(v) for v in ints]


def physical_denominator_relations(physical: list[sp.Expr]) -> list[dict[str, Any]]:
    """Return left-null SP relations, including their affine residuals.

    A coefficient vector c satisfies sum_i c_i * coeff_SP(D_i) = 0.  The full
    denominator combination may leave a scalar residual depending on m2 and z;
    that residual is retained because it determines the later partial-fraction
    identity rather than being silently discarded.
    """
    relations: list[dict[str, Any]] = []
    for raw in _sp_matrix(physical).T.nullspace():
        coeffs = _normalize_null_vector(raw)
        residual = sp.expand(sum(c * d for c, d in zip(coeffs, physical)))
        relations.append({
            "coefficients": [int(c) for c in coeffs],
            "relation": " + ".join(
                f"({int(c)})*D{i}"
                for i, c in enumerate(coeffs, start=1)
                if c != 0
            ),
            "affine_residual": str(residual),
            "exact_zero_relation": residual == 0,
        })
    return relations


def _quadratic_auxiliary_candidates() -> list[tuple[str, dict[str, sp.Expr], sp.Expr]]:
    """Return stable quadratic auxiliary candidates in a deterministic order."""
    specs = [
        ("(k-l)^2", _vec(k=1, l=-1)),
        ("(k-r)^2", _vec(k=1, r=-1)),
        ("(l-r)^2", _vec(l=1, r=-1)),
        ("(k+q)^2", _vec(k=1, q=1)),
        ("(l+q)^2", _vec(l=1, q=1)),
        ("(r+q)^2", _vec(r=1, q=1)),
        ("(k+l)^2", _vec(k=1, l=1)),
        ("(k+r)^2", _vec(k=1, r=1)),
        ("(l+r)^2", _vec(l=1, r=1)),
    ]
    return [(name, vec, sp.expand(_square(vec))) for name, vec in specs]


def complete_with_quadratic_auxiliaries(
    physical: list[sp.Expr],
) -> tuple[list[str], list[dict[str, sp.Expr]], list[sp.Expr]]:
    """Add exactly as many quadratic auxiliaries as needed to reach SP rank 12."""
    selected_names: list[str] = []
    selected_vecs: list[dict[str, sp.Expr]] = []
    selected_exprs: list[sp.Expr] = []
    rank = _rank(physical)
    for name, vec, expr in _quadratic_auxiliary_candidates():
        new_rank = _rank(physical + selected_exprs + [expr])
        if new_rank > rank:
            selected_names.append(name)
            selected_vecs.append(vec)
            selected_exprs.append(expr)
            rank = new_rank
        if rank == len(SP_BASIS):
            break
    if rank != len(SP_BASIS):
        raise ValueError(
            f"failed to span scalar-product space: physical_rank={_rank(physical)}, "
            f"final_rank={rank}, auxiliaries={selected_names}"
        )
    return selected_names, selected_vecs, selected_exprs


def _topology_loop_maps(candidate: dict[str, Any], reference: dict[str, Any]) -> Iterable[tuple[bool, dict[str, tuple[str, int]]]]:
    n = int(candidate["open_vertices"])
    if n != int(reference["open_vertices"]):
        return
    ref_ext = int(reference["external_vertex"])
    ref_edges = sorted(
        (min(int(e["a"]), int(e["b"])), max(int(e["a"]), int(e["b"])), str(e["label"]))
        for e in reference["photon_edges"]
    )
    for reflected in (False, True):
        ext = n + 1 - int(candidate["external_vertex"]) if reflected else int(candidate["external_vertex"])
        if ext != ref_ext:
            continue
        endpoints: dict[str, tuple[int, int]] = {}
        for edge in candidate["photon_edges"]:
            a, b = int(edge["a"]), int(edge["b"])
            if reflected:
                a, b = n + 1 - a, n + 1 - b
            endpoints[str(edge["label"])] = (min(a, b), max(a, b))
        for perm in permutations(LOOPS):
            relabel = dict(zip(LOOPS, perm))
            mapped = sorted((a, b, relabel[label]) for label, (a, b) in endpoints.items())
            if mapped != ref_edges:
                continue
            for signs in product((-1, 1), repeat=3):
                yield reflected, {src: (relabel[src], signs[i]) for i, src in enumerate(LOOPS)}


def _transform_denominators(row: dict[str, Any], loop_map: dict[str, tuple[str, int]], reflected: bool) -> list[sp.Expr]:
    m2 = sp.Symbol("m2")
    result: list[sp.Expr] = []
    for vec in _electron_momenta(row):
        tvec = _transform_vector(vec, loop_map=loop_map, reflected=reflected)
        result.append(sp.expand(m2 - _square(tvec)))
    for edge in row["photon_edges"]:
        vec = _vec(**{str(edge["label"]): 1})
        tvec = _transform_vector(vec, loop_map=loop_map, reflected=reflected)
        result.append(sp.expand(-_square(tvec)))
    return result


def _exact_permutation(source: list[sp.Expr], target: list[sp.Expr]) -> list[int] | None:
    used: set[int] = set()
    mapping: list[int] = []
    for expr in source:
        matches = [j for j, ref in enumerate(target) if j not in used and sp.expand(expr - ref) == 0]
        if len(matches) != 1:
            return None
        used.add(matches[0])
        mapping.append(matches[0] + 1)
    return mapping if len(used) == len(target) else None


def q01_reuse_witness(candidate: dict[str, Any], q01: dict[str, Any]) -> dict[str, Any] | None:
    """Check exact physical Q01 reuse within the current transform scope."""
    q01_physical = list(q01_denominator_expressions()[:9])
    for reflected, loop_map in _topology_loop_maps(candidate, q01):
        transformed = _transform_denominators(candidate, loop_map, reflected)
        permutation = _exact_permutation(transformed, q01_physical)
        if permutation is None:
            continue
        return {
            "reflection": reflected,
            "loop_momentum_transform": {
                src: (("-" if sign < 0 else "") + target)
                for src, (target, sign) in loop_map.items()
            },
            "external_momentum_transform": (
                {"p": "p+q", "q": "-q"} if reflected else {"p": "p", "q": "q"}
            ),
            "physical_propagator_permutation": permutation,
        }
    return None


def _pullback_aux_vector(canonical_vec: dict[str, sp.Expr], loop_map: dict[str, tuple[str, int]], reflected: bool) -> dict[str, sp.Expr]:
    inverse = {target: (source, sign) for source, (target, sign) in loop_map.items()}
    out = _vec()
    for canonical in LOOPS:
        coeff = canonical_vec.get(canonical, 0)
        if coeff:
            source, sign = inverse[canonical]
            out[source] += coeff * sign
    qcoeff = canonical_vec.get("q", 0)
    if qcoeff:
        out["q"] += -qcoeff if reflected else qcoeff
    pcoeff = canonical_vec.get("p", 0)
    if pcoeff:
        out["p"] += pcoeff
        if reflected:
            out["q"] += pcoeff
    return {name: sp.expand(value) for name, value in out.items()}


def find_family_witness(
    candidate: dict[str, Any],
    reference: dict[str, Any],
    reference_physical: list[sp.Expr],
    auxiliary_vecs: list[dict[str, sp.Expr]],
    auxiliary_exprs: list[sp.Expr],
) -> FamilyWitness | None:
    for reflected, loop_map in _topology_loop_maps(candidate, reference):
        transformed_physical = _transform_denominators(candidate, loop_map, reflected)
        permutation = _exact_permutation(transformed_physical, reference_physical)
        if permutation is None:
            continue
        exact = [True] * len(reference_physical)
        for vec, target in zip(auxiliary_vecs, auxiliary_exprs):
            pulled = _pullback_aux_vector(vec, loop_map, reflected)
            transformed = _transform_vector(pulled, loop_map=loop_map, reflected=reflected)
            exact.append(sp.expand(_square(transformed) - target) == 0)
        if not all(exact):
            continue
        loops = {
            src: (("-" if sign < 0 else "") + target)
            for src, (target, sign) in loop_map.items()
        }
        external = {"p": "p+q", "q": "-q"} if reflected else {"p": "p", "q": "q"}
        return FamilyWitness(
            diagram_id=str(candidate["id"]),
            representative=str(reference["id"]),
            reflection=reflected,
            loop_momentum_transform=loops,
            external_momentum_transform=external,
            physical_propagator_permutation=permutation,
            propagator_exact_match=exact,
        )
    return None


def choose_next_unresolved_quenched_class(rows: list[dict[str, Any]], confirmed_ids: set[str]) -> list[str]:
    """Choose the first unresolved quenched structural class by diagram number."""
    by_id = {str(row["id"]): row for row in rows}
    classes = candidate_classes(rows)
    groups: list[list[str]] = []
    for ids in classes.values():
        qids = [did for did in ids if by_id[did].get("family") == "quenched"]
        if qids and not any(did in confirmed_ids for did in qids):
            groups.append(sorted(qids, key=lambda x: int(x[1:])))
    if not groups:
        raise ValueError("no unresolved quenched structural class remains")
    return min(groups, key=lambda ids: int(ids[0][1:]))


def audit_next_quenched_family(rows: list[dict[str, Any]], confirmed_ids: set[str] | None = None) -> dict[str, Any]:
    confirmed_ids = set(confirmed_ids or {"Q01", "Q41"})
    by_id = {str(row["id"]): row for row in rows}
    class_ids = choose_next_unresolved_quenched_class(rows, confirmed_ids)
    representative_id = class_ids[0]
    representative = by_id[representative_id]
    q01 = by_id["Q01"]
    q01_witness = q01_reuse_witness(representative, q01)

    physical = topology_physical_denominators(representative)
    physical_rank = _rank(physical)
    relations = physical_denominator_relations(physical)
    aux_names, aux_vecs, aux_exprs = complete_with_quadratic_auxiliaries(physical)
    full_rank = _rank(physical + aux_exprs)
    generated_count = len(physical) + len(aux_exprs)
    overcomplete = generated_count > len(SP_BASIS)
    family_id = (
        "Q01_full"
        if q01_witness is not None
        else (f"{representative_id}_overcomplete_candidate" if overcomplete else f"{representative_id}_full")
    )

    records: list[dict[str, Any]] = []
    errors: list[str] = []
    if q01_witness is not None:
        errors.append(
            f"{representative_id}: unexpectedly maps to Q01_full under the current transform scope; "
            "do not bootstrap a new family"
        )

    for diagram_id in class_ids:
        try:
            witness = find_family_witness(by_id[diagram_id], representative, physical, aux_vecs, aux_exprs)
        except Exception as exc:
            witness = None
            errors.append(f"{diagram_id}: {exc}")
        records.append({
            "diagram_id": diagram_id,
            "status": "confirmed_algebraic_equivalence" if witness is not None else "candidate_only",
            "witness": witness.to_dict() if witness is not None else None,
        })
        if witness is None:
            errors.append(f"{diagram_id}: no exact generated-denominator witness to {representative_id}")

    if len(physical) != 9:
        errors.append(f"{representative_id}: expected 9 physical propagators, got {len(physical)}")
    if full_rank != 12:
        errors.append(f"{representative_id}: generated denominator rank {full_rank}/12")
    if physical_rank < len(physical) and not relations:
        errors.append(f"{representative_id}: rank deficiency detected but no left-null relation was recovered")

    kira_ready = (
        not errors
        and q01_witness is None
        and not overcomplete
        and physical_rank == len(physical)
        and generated_count == len(SP_BASIS)
    )

    return {
        "representative": representative_id,
        "family_candidate_id": family_id,
        "candidate_ids": class_ids,
        "q01_reuse_under_current_scope": q01_witness,
        "new_family_required_under_current_scope": q01_witness is None,
        "physical_propagator_count": len(physical),
        "physical_scalar_product_rank": physical_rank,
        "physical_rank_deficiency": len(physical) - physical_rank,
        "physical_denominator_relations": relations,
        "selected_auxiliary_count": len(aux_names),
        "auxiliary_names": aux_names,
        "generated_denominator_count": generated_count,
        "generated_scalar_product_rank": full_rank,
        "overcomplete_generated_set": overcomplete,
        "kira_ready": kira_ready,
        "requires_partial_fraction_or_family_split": overcomplete or physical_rank < len(physical),
        "generated_propagators": [str(expr) for expr in physical + aux_exprs],
        "records": records,
        "errors": errors,
        "audit_pass": not errors,
        "interpretation": (
            "PASS proves the topology-derived class is algebraically self-consistent under the recorded "
            "reflection/signed-loop maps and that the generated denominator set spans all 12 loop scalar "
            "products. If the physical rank is below the physical denominator count, the generated set is "
            "overcomplete and must be partial-fractioned or split into Kira-ready independent families before "
            "a canonical Kira family/master basis is registered."
        ),
    }
