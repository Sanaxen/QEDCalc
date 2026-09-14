"""Construct exact Q01 master-form relations from saved Kira momentum symmetries.

This stage performs no Kira, FireFly, or projected-trace recomputation.  It
combines three already-validated ingredients:

* the 60 master forms used by the saved projected amplitude;
* Kira's saved sectorRelations / sectorSymmetries momentum transformations;
* the saved FireFly FORM reduction graph.

For every relevant momentum map, positive denominator powers must map to a
single inverse propagator, while negative indices (numerators/ISPs) are allowed
to become affine linear combinations of P1..P12.  Those numerator polynomials
are expanded exactly, every resulting integral is recursively reduced through
the saved FireFly graph, and a linear relation among the 60 displayed master
forms is recorded whenever the transformed side closes on that set.

The probe then estimates the rank of the exact relation system at several exact
rational (d,z) points.  Agreement of the generic ranks is a strong diagnostic
of the number of independent master directions, but this script deliberately
does not yet rewrite the projected amplitude onto a chosen canonical basis.
"""
from __future__ import annotations

from collections import defaultdict
import json
from pathlib import Path
from typing import Iterable

import sympy as sp

from examples.three_loop_q01_kira_910_exact_closure1_firefly_export_audit import (
    FAMILY,
    PROJECT,
    _find_export_files,
)
from examples.three_loop_q01_kira_momentum_map_isp_probe import (
    FILES,
    P_SYMBOLS,
    _build_p_basis_solution,
    _integral_text,
    _load_final_forms,
    _parse_mapping_line,
    _sector,
    _single_p_image,
    _transformed_propagators,
)
from examples.three_loop_q01_projected_amplitude_firefly_reduce import (
    _load_weighted_form_graph,
    _make_recursive_reducer,
)

OUTPUT_JSON = PROJECT / "q01_kira_symmetry_linear_relation_probe.json"

IndexTuple = tuple[int, ...]
BasisVector = dict[IndexTuple, sp.Expr]

D = sp.Symbol("d")
Z = sp.Symbol("z")
GENERIC_POINTS = (
    {D: sp.Integer(5), Z: sp.Integer(2)},
    {D: sp.Integer(7), Z: sp.Integer(3)},
    {D: sp.Integer(11), Z: sp.Integer(5)},
)


def _loop_matrix(momentum_map: dict[str, dict[str, sp.Expr]]) -> sp.Matrix:
    loops = ("k", "l", "r")
    return sp.Matrix(
        [
            [sp.sympify(momentum_map[row].get(col, 0)) for col in loops]
            for row in loops
        ]
    )


def _expand_transformed_integral(
    source: IndexTuple,
    images: tuple[sp.Expr, ...],
) -> tuple[tuple[sp.Expr, IndexTuple], ...] | None:
    """Apply one momentum map to an indexed integral and expand numerator ISPs.

    Positive powers are denominators.  Negative powers are polynomial
    numerators.  The returned coefficient includes constant factors from mapped
    denominators and from the expanded numerator polynomial.
    """
    target = [0] * 12
    prefactor = sp.Integer(1)
    numerator = sp.Integer(1)

    for i, exponent in enumerate(source):
        if exponent == 0:
            continue
        image = sp.expand(images[i])
        if exponent > 0:
            single = _single_p_image(image)
            if single is None:
                return None
            target_pos, scale = single
            if scale == 0:
                return None
            target[target_pos] += exponent
            prefactor *= scale ** (-exponent)
        else:
            numerator *= image ** (-exponent)

    numerator = sp.Poly(sp.expand(numerator), *P_SYMBOLS)
    terms: list[tuple[sp.Expr, IndexTuple]] = []
    for monomial, coefficient in numerator.terms():
        indices = list(target)
        for j, power in enumerate(monomial):
            indices[j] -= int(power)
        terms.append((sp.expand(prefactor * coefficient), tuple(indices)))
    return tuple(terms)


def _accumulate(target: BasisVector, source: BasisVector, factor: sp.Expr) -> None:
    if factor == 0:
        return
    for key, coefficient in source.items():
        value = target.get(key, 0) + factor * coefficient
        target[key] = value


def _normalize_relation(vector: BasisVector) -> BasisVector:
    out = {key: sp.cancel(value) for key, value in vector.items() if value != 0}
    out = {key: value for key, value in out.items() if value != 0}
    if not out:
        return {}
    # Normalize by the first nonzero coefficient so duplicate proportional rows
    # can be recognized without a full symbolic row-reduction.
    first_key = sorted(out)[0]
    pivot = out[first_key]
    return {key: sp.cancel(value / pivot) for key, value in out.items()}


def _relation_signature(vector: BasisVector) -> tuple[tuple[IndexTuple, str], ...]:
    return tuple((key, str(vector[key])) for key in sorted(vector))


def _generic_rank(
    relations: list[BasisVector], basis: tuple[IndexTuple, ...], point: dict[sp.Symbol, sp.Expr]
) -> int:
    rows: list[list[sp.Expr]] = []
    for relation in relations:
        row = []
        valid = True
        for key in basis:
            try:
                value = sp.cancel(relation.get(key, 0).subs(point))
            except Exception:
                valid = False
                break
            if value.has(sp.zoo, sp.nan, sp.oo, -sp.oo):
                valid = False
                break
            row.append(value)
        if valid:
            rows.append(row)
    if not rows:
        return 0
    return int(sp.Matrix(rows).rank())


def main() -> None:
    print("QEDCalc Q01 Kira symmetry linear-relation probe")
    print("mode: saved sectormappings + saved FireFly graph only; no recomputation")

    final_forms = _load_final_forms()
    basis = tuple(sorted(final_forms))
    basis_solution = _build_p_basis_solution()
    print("final master forms:", len(basis))
    print("Q01 Kira P-basis round trip: PASS")

    mappings_by_sector: dict[
        int,
        list[tuple[str, int, dict[str, dict[str, sp.Expr]], tuple[int, ...], int]],
    ] = defaultdict(list)
    parsed = 0
    for path in FILES:
        if not path.exists():
            raise SystemExit(f"ERROR: Kira sectormapping file not found: {path}")
        local = 0
        for line_no, line in enumerate(path.read_text(encoding="utf-8", errors="strict").splitlines(), 1):
            item = _parse_mapping_line(line, source_file=path, line_no=line_no)
            if item is None:
                continue
            source_sector, target_sector, momentum_map, direct_map = item
            mappings_by_sector[source_sector].append(
                (path.name, target_sector, momentum_map, direct_map, line_no)
            )
            parsed += 1
            local += 1
        print(f"parsed {path.name} momentum mappings:", local)

    form_file, masters_file = _find_export_files()
    rules, zero_rules, masters, terminal_rhs, _ = _load_weighted_form_graph(
        form_file, masters_file
    )
    reduce_one, memo = _make_recursive_reducer(
        rules=rules,
        zero_rules=zero_rules,
        masters=masters,
        terminal_rhs=terminal_rhs,
    )
    print("saved FORM reduction rules:", len(rules))
    print("saved FORM zero rules:", len(zero_rules))
    print("saved terminal/master leaves:", len(masters | terminal_rhs))

    transform_cache: dict[tuple[str, int], tuple[sp.Expr, ...]] = {}
    attempted = 0
    unimodular = 0
    expansion_failures = 0
    reduction_missing = 0
    out_of_final_basis = 0
    trivial_relations = 0
    closed_relations = 0
    unique_relations: list[BasisVector] = []
    signatures: set[tuple[tuple[IndexTuple, str], ...]] = set()
    samples: list[dict[str, object]] = []

    for source in basis:
        source_sector = _sector(source)
        for file_name, target_sector, momentum_map, _direct_map, line_no in mappings_by_sector.get(source_sector, []):
            attempted += 1
            loop_matrix = _loop_matrix(momentum_map)
            determinant = sp.expand(loop_matrix.det())
            if determinant not in (sp.Integer(1), sp.Integer(-1)):
                # Kira symmetry maps used here should be unimodular.  Do not use
                # any map with a non-unit loop Jacobian in an integral identity.
                continue
            unimodular += 1

            cache_key = (file_name, line_no)
            images = transform_cache.get(cache_key)
            if images is None:
                images = _transformed_propagators(momentum_map, basis_solution)
                transform_cache[cache_key] = images

            expanded = _expand_transformed_integral(source, images)
            if expanded is None:
                expansion_failures += 1
                continue

            rhs: BasisVector = {}
            failed = False
            for coefficient, target in expanded:
                try:
                    reduced = reduce_one(target)
                except KeyError:
                    reduction_missing += 1
                    failed = True
                    break
                _accumulate(rhs, reduced, coefficient)
            if failed:
                continue

            outside = set(rhs) - final_forms
            if outside:
                out_of_final_basis += 1
                continue

            relation: BasisVector = {source: sp.Integer(1)}
            for key, coefficient in rhs.items():
                relation[key] = relation.get(key, 0) - coefficient
            relation = _normalize_relation(relation)
            if not relation:
                trivial_relations += 1
                continue

            closed_relations += 1
            signature = _relation_signature(relation)
            if signature in signatures:
                continue
            signatures.add(signature)
            unique_relations.append(relation)

            if len(samples) < 12:
                samples.append(
                    {
                        "source": _integral_text(source),
                        "mapping_file": file_name,
                        "mapping_line": line_no,
                        "source_sector": source_sector,
                        "target_sector": target_sector,
                        "loop_det": str(determinant),
                        "expanded_integrals": len(expanded),
                        "relation_terms": [
                            {
                                "integral": _integral_text(key),
                                "coefficient": str(relation[key]),
                            }
                            for key in sorted(relation)
                        ],
                    }
                )

    print("relation-building applications attempted:", attempted)
    print("unimodular applications:", unimodular)
    print("numerator expansion failures:", expansion_failures)
    print("expanded integrals missing from saved reduction graph:", reduction_missing)
    print("relations closing outside displayed 60-form set:", out_of_final_basis)
    print("exact trivial identities:", trivial_relations)
    print("closed nontrivial relation applications:", closed_relations)
    print("unique exact relation rows:", len(unique_relations))
    print("memoized FireFly reduction nodes:", len(memo))

    ranks: list[int] = []
    point_rows: list[dict[str, object]] = []
    for point in GENERIC_POINTS:
        rank = _generic_rank(unique_relations, basis, point)
        ranks.append(rank)
        point_rows.append(
            {
                "d": int(point[D]),
                "z": int(point[Z]),
                "rank": rank,
                "independent_directions": len(basis) - rank,
            }
        )
        print(
            f"generic exact rank at d={point[D]}, z={point[Z]}: {rank}; "
            f"independent directions={len(basis) - rank}"
        )

    consistent_rank = len(set(ranks)) == 1 if ranks else False
    generic_rank = ranks[0] if consistent_rank and ranks else None
    independent = len(basis) - generic_rank if generic_rank is not None else None

    summary = {
        "mode": "exact symmetry relations from saved Kira momentum maps plus saved FireFly graph",
        "final_master_forms": len(basis),
        "parsed_mapping_lines": parsed,
        "relation_building_applications_attempted": attempted,
        "unimodular_applications": unimodular,
        "numerator_expansion_failures": expansion_failures,
        "expanded_integrals_missing_from_saved_reduction_graph": reduction_missing,
        "relations_closing_outside_displayed_final_basis": out_of_final_basis,
        "trivial_identity_applications": trivial_relations,
        "closed_nontrivial_relation_applications": closed_relations,
        "unique_exact_relation_rows": len(unique_relations),
        "generic_rank_points": point_rows,
        "generic_rank_consistent": consistent_rank,
        "generic_relation_rank": generic_rank,
        "generic_independent_master_directions": independent,
        "samples": samples,
        "pass": (
            parsed > 0
            and attempted > 0
            and unimodular > 0
            and expansion_failures == 0
            and len(unique_relations) > 0
            and consistent_rank
        ),
    }
    OUTPUT_JSON.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print("probe JSON:", OUTPUT_JSON)

    for sample in samples[:5]:
        print(
            "  relation sample:",
            sample["source"],
            f"({sample['mapping_file']}:{sample['mapping_line']})",
            "terms=",
            len(sample["relation_terms"]),
        )
        for term in sample["relation_terms"][:6]:
            coeff = str(term["coefficient"])
            if len(coeff) > 140:
                coeff = coeff[:137] + "..."
            print("    ", coeff, "*", term["integral"])

    if not summary["pass"]:
        raise SystemExit("Q01 Kira symmetry linear-relation probe FAIL")
    print("Q01 Kira symmetry linear-relation probe PASS")


if __name__ == "__main__":
    main()
