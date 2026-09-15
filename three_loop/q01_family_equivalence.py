"""Exact Q01-family equivalence mapper for structural candidate diagrams.

A topology match is only a candidate generator.  Promotion to Q01_full requires
an explicit reflection / signed loop relabel witness and exact SymPy equality of
all twelve Kira inverse propagators, including the auxiliary ISP bridge.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from itertools import permutations, product
from typing import Any, Iterable

import sympy as sp

from qedcalc.operations.ibp import sp_atom
from three_loop.integral_family import q01_denominator_expressions
from three_loop.kira_backend import (
    Q01_KIRA_TO_QED_PHYSICAL,
    q01_kira_inverse_propagator_expressions,
)

LOOPS = ("k", "l", "r")
VARS = ("k", "l", "r", "p", "q")


@dataclass(frozen=True)
class EquivalenceWitness:
    diagram_id: str
    representative: str
    reflection: bool
    loop_momentum_transform: dict[str, str]
    external_momentum_transform: dict[str, str]
    physical_propagator_permutation: list[int]
    kira_propagator_permutation: list[int]
    propagator_exact_match: list[bool]
    isp_bridge_exact_match: list[bool]
    canonical_family_id: str = "Q01_full"
    kira_reusable: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _vec(**coeffs: int) -> dict[str, sp.Expr]:
    return {name: sp.Integer(coeffs.get(name, 0)) for name in VARS}


def _add(*vectors: dict[str, sp.Expr]) -> dict[str, sp.Expr]:
    return {name: sp.expand(sum(v.get(name, 0) for v in vectors)) for name in VARS}


def _scale(c: sp.Expr, v: dict[str, sp.Expr]) -> dict[str, sp.Expr]:
    return {name: sp.expand(c * v.get(name, 0)) for name in VARS}


def _dot(a: dict[str, sp.Expr], b: dict[str, sp.Expr]) -> sp.Expr:
    m2, z = sp.symbols("m2 z")
    out = sp.Integer(0)
    for i, x in enumerate(VARS):
        for y in VARS[i:]:
            coeff = a[x] * b[y]
            if x != y:
                coeff += a[y] * b[x]
            if coeff == 0:
                continue
            if x == y == "p":
                atom = m2
            elif x == y == "q":
                atom = z * m2
            elif {x, y} == {"p", "q"}:
                atom = -z * m2 / 2
            else:
                atom = sp_atom(x, y)
            out += coeff * atom
    return sp.expand(out)


def _square(v: dict[str, sp.Expr]) -> sp.Expr:
    return _dot(v, v)


def _electron_momenta(row: dict[str, Any]) -> list[dict[str, sp.Expr]]:
    ext = int(row["external_vertex"])
    n = int(row["open_vertices"])
    edges = row.get("photon_edges", [])
    momenta: list[dict[str, sp.Expr]] = []
    for segment in range(1, n):
        side = _add(_vec(p=1), _vec(q=1)) if segment < ext else _vec(p=1)
        active = []
        for edge in edges:
            a, b = sorted((int(edge["a"]), int(edge["b"])))
            if a <= segment < b:
                active.append(_vec(**{str(edge["label"]): -1}))
        momenta.append(_add(side, *active))
    return momenta


def _physical_denominators(row: dict[str, Any]) -> list[sp.Expr]:
    m2 = sp.Symbol("m2")
    electron = [sp.expand(m2 - _square(v)) for v in _electron_momenta(row)]
    photon = [sp.expand(-_square(_vec(**{str(edge["label"]): 1}))) for edge in row.get("photon_edges", [])]
    return electron + photon


def _transform_vector(
    v: dict[str, sp.Expr],
    *,
    loop_map: dict[str, tuple[str, int]],
    reflected: bool,
) -> dict[str, sp.Expr]:
    out = _vec()
    for source in LOOPS:
        target, sign = loop_map[source]
        out[target] += v[source] * sign
    if reflected:
        # Open-line reflection interchanges p and p'=p+q, hence
        # candidate p -> canonical p+q and candidate q -> -canonical q.
        out["p"] += v["p"]
        out["q"] += v["p"] - v["q"]
    else:
        out["p"] += v["p"]
        out["q"] += v["q"]
    return {name: sp.expand(value) for name, value in out.items()}


def _transform_expr_from_vector(v: dict[str, sp.Expr], *, loop_map: dict[str, tuple[str, int]], reflected: bool) -> sp.Expr:
    return sp.expand(_square(_transform_vector(v, loop_map=loop_map, reflected=reflected)))


def _topology_loop_maps(candidate: dict[str, Any], reference: dict[str, Any]) -> Iterable[tuple[bool, dict[str, tuple[str, int]]]]:
    n = int(candidate["open_vertices"])
    if n != int(reference["open_vertices"]):
        return
    ref_ext = int(reference["external_vertex"])
    ref_edges = sorted((min(int(e["a"]), int(e["b"])), max(int(e["a"]), int(e["b"])), str(e["label"])) for e in reference["photon_edges"])
    cand_edges = candidate["photon_edges"]
    for reflected in (False, True):
        ext = n + 1 - int(candidate["external_vertex"]) if reflected else int(candidate["external_vertex"])
        if ext != ref_ext:
            continue
        endpoints: dict[str, tuple[int, int]] = {}
        for edge in cand_edges:
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


def _transform_denominator(expr_vec: dict[str, sp.Expr], *, electron: bool, loop_map: dict[str, tuple[str, int]], reflected: bool) -> sp.Expr:
    m2 = sp.Symbol("m2")
    sq = _transform_expr_from_vector(expr_vec, loop_map=loop_map, reflected=reflected)
    return sp.expand(m2 - sq if electron else -sq)


def _candidate_physical_transformed(row: dict[str, Any], *, loop_map: dict[str, tuple[str, int]], reflected: bool) -> list[sp.Expr]:
    electron_vecs = _electron_momenta(row)
    result = [_transform_denominator(v, electron=True, loop_map=loop_map, reflected=reflected) for v in electron_vecs]
    for edge in row["photon_edges"]:
        v = _vec(**{str(edge["label"]): 1})
        result.append(_transform_denominator(v, electron=False, loop_map=loop_map, reflected=reflected))
    return result


def _exact_permutation(source: list[sp.Expr], target: list[sp.Expr]) -> list[int] | None:
    used: set[int] = set()
    mapping: list[int] = []
    for expr in source:
        matches = [j for j, ref in enumerate(target) if j not in used and sp.expand(expr - ref) == 0]
        if len(matches) != 1:
            return None
        j = matches[0]
        used.add(j)
        mapping.append(j + 1)
    return mapping if len(used) == len(target) else None


def _inverse_aux_vectors(loop_map: dict[str, tuple[str, int]], reflected: bool) -> list[dict[str, sp.Expr]]:
    inverse: dict[str, tuple[str, int]] = {}
    for source, (target, sign) in loop_map.items():
        inverse[target] = (source, sign)
    qsign = -1 if reflected else 1

    def pull(loop_coeffs: dict[str, int], qcoeff: int = 0) -> dict[str, sp.Expr]:
        v = _vec(q=qcoeff * qsign)
        for canonical, coeff in loop_coeffs.items():
            source, sign = inverse[canonical]
            v[source] += coeff * sign
        return v

    return [
        pull({"k": 1, "r": -1}),
        pull({"l": 1}, qcoeff=1),
        pull({"r": 1}, qcoeff=1),
    ]


def _isp_bridge_matches(loop_map: dict[str, tuple[str, int]], reflected: bool) -> list[bool]:
    inverse: dict[str, tuple[str, int]] = {target: (source, sign) for source, (target, sign) in loop_map.items()}
    qsign = -1 if reflected else 1

    def loop_vec(canonical: str) -> dict[str, sp.Expr]:
        source, sign = inverse[canonical]
        return _vec(**{source: sign})

    candidate_pairs = [
        (loop_vec("k"), loop_vec("r")),
        (loop_vec("l"), _vec(q=qsign)),
        (_vec(q=qsign), loop_vec("r")),
    ]
    targets = [sp_atom("k", "r"), sp_atom("l", "q"), sp_atom("q", "r")]
    out: list[bool] = []
    for (a, b), target in zip(candidate_pairs, targets):
        ta = _transform_vector(a, loop_map=loop_map, reflected=reflected)
        tb = _transform_vector(b, loop_map=loop_map, reflected=reflected)
        out.append(sp.expand(_dot(ta, tb) - target) == 0)
    return out


def find_q01_equivalence_witness(candidate: dict[str, Any], reference: dict[str, Any]) -> EquivalenceWitness | None:
    reference_physical = list(q01_denominator_expressions()[:9])
    generated_reference = _physical_denominators(reference)
    if len(generated_reference) != 9 or any(sp.expand(a - b) != 0 for a, b in zip(generated_reference, reference_physical)):
        raise ValueError("topology-derived Q01 physical propagators no longer match q01_denominator_expressions()")

    canonical_kira = list(q01_kira_inverse_propagator_expressions())
    for reflected, loop_map in _topology_loop_maps(candidate, reference):
        transformed_physical = _candidate_physical_transformed(candidate, loop_map=loop_map, reflected=reflected)
        physical_perm = _exact_permutation(transformed_physical, reference_physical)
        if physical_perm is None:
            continue

        # Reorder the candidate physical lines into Q01 Kira P1..P9 order.
        transformed_kira: list[sp.Expr] = []
        for qed_index in Q01_KIRA_TO_QED_PHYSICAL:
            source_index = physical_perm.index(qed_index)
            transformed_kira.append(sp.expand(-transformed_physical[source_index]))

        aux_vectors = _inverse_aux_vectors(loop_map, reflected)
        transformed_kira.extend(
            sp.expand(_transform_expr_from_vector(v, loop_map=loop_map, reflected=reflected))
            for v in aux_vectors
        )
        exact = [sp.expand(a - b) == 0 for a, b in zip(transformed_kira, canonical_kira)]
        isp = _isp_bridge_matches(loop_map, reflected)
        if not all(exact) or not all(isp):
            continue

        transform_text = {
            source: (("-" if sign < 0 else "") + target)
            for source, (target, sign) in loop_map.items()
        }
        external = {"p": "p+q", "q": "-q"} if reflected else {"p": "p", "q": "q"}
        return EquivalenceWitness(
            diagram_id=str(candidate["id"]),
            representative=str(reference["id"]),
            reflection=reflected,
            loop_momentum_transform=transform_text,
            external_momentum_transform=external,
            physical_propagator_permutation=physical_perm,
            kira_propagator_permutation=list(range(1, 13)),
            propagator_exact_match=exact,
            isp_bridge_exact_match=isp,
        )
    return None


def audit_q01_family_equivalence(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_id = {str(row["id"]): row for row in rows}
    reference = by_id.get("Q01")
    if reference is None:
        return {"candidate_ids": [], "confirmed_ids": [], "records": [], "errors": ["Q01 missing from topology inventory"], "audit_pass": False}

    # Import locally to avoid a module cycle: classification imports this mapper.
    from three_loop.integral_family_classification import structural_candidate_key

    key = structural_candidate_key(reference)
    candidates = [row for row in rows if structural_candidate_key(row) == key]
    records: list[dict[str, Any]] = []
    errors: list[str] = []
    confirmed: list[str] = []
    for row in sorted(candidates, key=lambda item: str(item["id"])):
        try:
            witness = find_q01_equivalence_witness(row, reference)
        except Exception as exc:
            errors.append(f"{row['id']}: equivalence audit failed: {exc}")
            witness = None
        if witness is None:
            records.append({"diagram_id": str(row["id"]), "status": "candidate_only", "witness": None})
        else:
            confirmed.append(str(row["id"]))
            records.append({"diagram_id": str(row["id"]), "status": "confirmed", "witness": witness.to_dict()})

    return {
        "representative": "Q01",
        "canonical_family_id": "Q01_full",
        "candidate_ids": [str(row["id"]) for row in sorted(candidates, key=lambda item: str(item["id"]))],
        "confirmed_ids": confirmed,
        "records": records,
        "errors": errors,
        "audit_pass": not errors,
    }
