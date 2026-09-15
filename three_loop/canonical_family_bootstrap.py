"""Bootstrap a canonical 12-propagator family for an unresolved quenched class.

This module is intentionally algebraic and conservative. It does not claim a
new Kira family merely from graph topology. For a chosen representative it

1. derives the nine physical scalar denominators from the topology inventory;
2. checks whether those lines already map to Q01 under the currently allowed
   reflection + signed loop-relabel transform class;
3. if not, greedily selects three quadratic auxiliaries that complete the
   12-dimensional loop scalar-product basis;
4. proves every member of the same structural candidate class against the new
   P1..P12 basis by exact SymPy equality.

The resulting family is a canonical algebraic family candidate. A Kira project
and master basis are deliberately left for the next stage.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from itertools import permutations, product
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


def _rank(expressions: list[sp.Expr]) -> int:
    matrix = sp.Matrix([
        [sp.expand(expr).coeff(atom) for atom in SP_BASIS]
        for expr in expressions
    ])
    return int(matrix.rank())


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


def complete_with_quadratic_auxiliaries(physical: list[sp.Expr]) -> tuple[list[str], list[dict[str, sp.Expr]], list[sp.Expr]]:
    """Greedily add three quadratic auxiliaries until the SP rank reaches 12."""
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
    if rank != len(SP_BASIS) or len(selected_exprs) != 3:
        raise ValueError(
            f"failed to complete canonical basis: physical_rank={_rank(physical)}, "
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
    aux_names, aux_vecs, aux_exprs = complete_with_quadratic_auxiliaries(physical)
    family_id = "Q01_full" if q01_witness is not None else f"{representative_id}_full"

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
            "status": "confirmed" if witness is not None else "candidate_only",
            "witness": witness.to_dict() if witness is not None else None,
        })
        if witness is None:
            errors.append(f"{diagram_id}: no exact P1..P12 witness to {representative_id}")

    physical_rank = _rank(physical)
    full_rank = _rank(physical + aux_exprs)
    if len(physical) != 9:
        errors.append(f"{representative_id}: expected 9 physical propagators, got {len(physical)}")
    if full_rank != 12:
        errors.append(f"{representative_id}: canonical basis rank {full_rank}/12")

    return {
        "representative": representative_id,
        "canonical_family_id": family_id,
        "candidate_ids": class_ids,
        "q01_reuse_under_current_scope": q01_witness,
        "new_family_required_under_current_scope": q01_witness is None,
        "physical_propagator_count": len(physical),
        "physical_scalar_product_rank": physical_rank,
        "auxiliary_names": aux_names,
        "canonical_basis_rank": full_rank,
        "canonical_propagators": [str(expr) for expr in physical + aux_exprs],
        "records": records,
        "errors": errors,
        "audit_pass": not errors,
        "interpretation": (
            "This proves a canonical algebraic P1..P12 family under reflection + signed loop relabeling. "
            "A missing Q01 witness means only that Q01 reuse is absent within that explicit transform scope. "
            "It does not yet mean that a Kira reduction/master basis for the new family has been computed."
        ),
    }
