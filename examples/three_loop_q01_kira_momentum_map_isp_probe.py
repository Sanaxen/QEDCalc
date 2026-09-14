"""Probe full Q01 Kira momentum mappings beyond direct propagator permutations.

This helper performs no Kira/FireFly/projected-trace recomputation.  It reads
saved ``sectorRelations`` / ``sectorSymmetries`` momentum maps, reconstructs how
all twelve Q01 Kira inverse propagators transform, and expresses every image
back in the original P1..P12 basis.

The purpose is diagnostic: the earlier pure-index probe rejected mappings when a
nonzero numerator/ISP index had no direct propagator target.  Here we test
whether those cases are explained by finite linear combinations of Kira inverse
propagators (plus z-dependent constants).  No master forms are merged in this
stage.
"""
from __future__ import annotations

from collections import defaultdict
import json
from pathlib import Path
from typing import Iterable

import sympy as sp

from examples.three_loop_q01_kira_910_exact_closure1_firefly_export_audit import (
    ALT_ROOT,
    FAMILY,
    PROJECT,
)
from qedcalc.operations.ibp import sp_atom
from three_loop.kira_backend import (
    _q01_sp_basis,
    q01_kira_inverse_propagator_expressions,
)

MASTER_JSON = PROJECT / "q01_projected_amplitude_kira_master_basis.json"
OUTPUT_JSON = PROJECT / "q01_kira_momentum_map_isp_probe.json"
SECTOR_DIR = ALT_ROOT / "sectormappings" / FAMILY
FILES = (SECTOR_DIR / "sectorRelations", SECTOR_DIR / "sectorSymmetries")

IndexTuple = tuple[int, ...]
Vector = dict[str, sp.Expr]

VEC_NAMES = ("k", "l", "r", "p", "q")
VEC_SYMBOLS = {name: sp.Symbol(name) for name in VEC_NAMES}
P_SYMBOLS = sp.symbols("P1:13")
M2 = sp.Symbol("m2")
Z = sp.Symbol("z")

# Q01 Kira propagator momenta in the exact order used by kira_backend.py.
PROPAGATOR_VECTORS: tuple[Vector, ...] = (
    {"k": 1, "p": -1, "q": -1},
    {"k": 1, "l": 1, "p": -1},
    {"l": 1, "r": 1, "p": -1},
    {"r": 1, "p": -1},
    {"k": 1, "p": -1},
    {"l": 1, "p": -1},
    {"k": 1},
    {"l": 1},
    {"r": 1},
    {"k": 1, "r": -1},
    {"l": 1, "q": 1},
    {"r": 1, "q": 1},
)
PROPAGATOR_MASSES = (M2, M2, M2, M2, M2, M2, 0, 0, 0, 0, 0, 0)


def _sector(indices: IndexTuple) -> int:
    value = 0
    for i, exponent in enumerate(indices):
        if exponent > 0:
            value |= 1 << i
    return value


def _integral_text(values: IndexTuple) -> str:
    return f"{FAMILY}[{','.join(str(v) for v in values)}]"


def _load_final_forms() -> set[IndexTuple]:
    if not MASTER_JSON.exists():
        raise SystemExit(f"ERROR: master-basis JSON not found: {MASTER_JSON}")
    data = json.loads(MASTER_JSON.read_text(encoding="utf-8"))
    forms: set[IndexTuple] = set()
    for row in data.get("basis_terms", []):
        raw = row.get("indices")
        if not isinstance(raw, list) or len(raw) != 12:
            raise SystemExit(f"ERROR: malformed basis row: {row!r}")
        forms.add(tuple(int(v) for v in raw))
    if not forms:
        raise SystemExit("ERROR: no final master forms in master-basis JSON")
    return forms


def _parse_vector(text: str) -> Vector:
    try:
        expr = sp.expand(sp.sympify(text, locals=VEC_SYMBOLS))
    except Exception as exc:
        raise ValueError(f"could not parse vector expression {text!r}: {exc}") from exc
    out: Vector = {}
    residual = expr
    for name, symbol in VEC_SYMBOLS.items():
        coeff = sp.expand(expr).coeff(symbol)
        if coeff != 0:
            out[name] = coeff
            residual -= coeff * symbol
    if sp.expand(residual) != 0:
        raise ValueError(f"nonlinear/non-vector residual in {text!r}: {sp.expand(residual)}")
    return out


def _parse_mapping_line(
    line: str, *, source_file: Path, line_no: int
) -> tuple[int, int, dict[str, Vector], tuple[int, ...]] | None:
    text = line.strip()
    if not text:
        return None
    marker = "{place==holder} {place==holder}"
    if marker not in text:
        return None
    before, after = text.split(marker, 1)
    tokens = before.split()
    after_tokens = after.split()
    if len(tokens) < 11 or len(after_tokens) < 12:
        return None
    if tokens[1] != "k" or tokens[3] != "l" or tokens[5] != "r":
        return None
    try:
        source_sector = int(tokens[0])
        target_sector = int(tokens[-3])
        direct_map = tuple(int(v) for v in after_tokens[:12])
        momentum_map = {
            "k": _parse_vector(tokens[2]),
            "l": _parse_vector(tokens[4]),
            "r": _parse_vector(tokens[6]),
        }
    except (ValueError, IndexError) as exc:
        raise SystemExit(
            f"ERROR: malformed Kira momentum mapping in {source_file} line {line_no}: {exc}"
        ) from exc
    return source_sector, target_sector, momentum_map, direct_map


def _add_scaled(target: Vector, source: Vector, factor: sp.Expr) -> None:
    for name, coefficient in source.items():
        value = sp.expand(factor * coefficient)
        target[name] = sp.expand(target.get(name, 0) + value)
        if target[name] == 0:
            del target[name]


def _map_vector(vector: Vector, momentum_map: dict[str, Vector]) -> Vector:
    out: Vector = {}
    for name, coefficient in vector.items():
        image = momentum_map.get(name, {name: sp.Integer(1)})
        _add_scaled(out, image, coefficient)
    return out


def _dot(left: Vector, right: Vector) -> sp.Expr:
    result = sp.Integer(0)
    for a, ca in left.items():
        for b, cb in right.items():
            if a == "p" and b == "p":
                atom = M2
            elif a == "q" and b == "q":
                atom = Z * M2
            elif {a, b} == {"p", "q"}:
                atom = -Z * M2 / 2
            else:
                atom = sp_atom(a, b)
            result += ca * cb * atom
    return sp.expand(result)


def _build_p_basis_solution() -> dict[sp.Symbol, sp.Expr]:
    sp_basis = _q01_sp_basis()
    inverse = q01_kira_inverse_propagator_expressions()
    equations = [sp.Eq(P_SYMBOLS[i], inverse[i]) for i in range(12)]
    solved = sp.solve(equations, sp_basis, dict=True, simplify=False)
    if len(solved) != 1 or any(atom not in solved[0] for atom in sp_basis):
        raise SystemExit("ERROR: could not invert the 12-dimensional Q01 Kira P basis")
    solution = solved[0]
    # Independent exact round-trip check before using the solution on Kira maps.
    for i, expr in enumerate(inverse):
        back = sp.expand(expr.subs(solution) - P_SYMBOLS[i])
        if back != 0:
            raise SystemExit(f"ERROR: Q01 Kira P-basis round trip failed for P{i + 1}: {back}")
    return solution


def _transformed_propagators(
    momentum_map: dict[str, Vector], basis_solution: dict[sp.Symbol, sp.Expr]
) -> tuple[sp.Expr, ...]:
    out: list[sp.Expr] = []
    for vector, mass in zip(PROPAGATOR_VECTORS, PROPAGATOR_MASSES):
        mapped = _map_vector(vector, momentum_map)
        expr = sp.expand(_dot(mapped, mapped) - mass)
        expr = sp.expand(expr.subs(basis_solution).subs(M2, 1))
        out.append(expr)
    return tuple(out)


def _single_p_image(expr: sp.Expr) -> tuple[int, sp.Expr] | None:
    expanded = sp.expand(expr)
    constant = expanded.subs({symbol: 0 for symbol in P_SYMBOLS})
    if sp.expand(constant) != 0:
        return None
    hits: list[tuple[int, sp.Expr]] = []
    for i, symbol in enumerate(P_SYMBOLS):
        coeff = sp.expand(expanded.coeff(symbol))
        if coeff != 0:
            hits.append((i, coeff))
    if len(hits) != 1:
        return None
    i, coeff = hits[0]
    if sp.expand(expanded - coeff * P_SYMBOLS[i]) != 0:
        return None
    return i, coeff


def _direct_map_reject(indices: IndexTuple, direct_map: tuple[int, ...]) -> bool:
    return any(exponent != 0 and direct_map[i] < 0 for i, exponent in enumerate(indices))


def main() -> None:
    print("QEDCalc Q01 Kira momentum-map / ISP transformation probe")
    print("mode: saved sectormapping metadata only; no Kira/FireFly/projected-trace recomputation")

    forms = _load_final_forms()
    basis_solution = _build_p_basis_solution()
    print("final master forms:", len(forms))
    print("Q01 Kira P-basis round trip: PASS")

    mappings_by_sector: dict[int, list[tuple[str, int, dict[str, Vector], tuple[int, ...], int]]] = defaultdict(list)
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

    transform_cache: dict[tuple[str, int], tuple[sp.Expr, ...]] = {}
    relevant_applications = 0
    direct_rejects = 0
    general_compatible = 0
    general_compatible_direct_rejects = 0
    positive_sector_mismatches = 0
    mixed_numerator_occurrences = 0
    mixed_samples: list[dict[str, object]] = []
    compatible_samples: list[dict[str, object]] = []

    for source in sorted(forms):
        source_sector = _sector(source)
        for file_name, target_sector, momentum_map, direct_map, line_no in mappings_by_sector.get(source_sector, []):
            relevant_applications += 1
            cache_key = (file_name, line_no)
            images = transform_cache.get(cache_key)
            if images is None:
                images = _transformed_propagators(momentum_map, basis_solution)
                transform_cache[cache_key] = images

            was_direct_reject = _direct_map_reject(source, direct_map)
            if was_direct_reject:
                direct_rejects += 1

            target_positive = 0
            compatible = True
            mixed_rows: list[dict[str, object]] = []
            for i, exponent in enumerate(source):
                if exponent == 0:
                    continue
                image = images[i]
                single = _single_p_image(image)
                if exponent > 0:
                    if single is None:
                        compatible = False
                        break
                    target_positive |= 1 << single[0]
                else:
                    if image == 0:
                        compatible = False
                        break
                    if single is None:
                        mixed_numerator_occurrences += 1
                        mixed_rows.append(
                            {
                                "source_P": i + 1,
                                "power": -exponent,
                                "image": str(image),
                            }
                        )

            if compatible and target_positive != target_sector:
                positive_sector_mismatches += 1
                compatible = False

            if compatible:
                general_compatible += 1
                if was_direct_reject:
                    general_compatible_direct_rejects += 1
                if len(compatible_samples) < 20 and (was_direct_reject or mixed_rows):
                    compatible_samples.append(
                        {
                            "source": _integral_text(source),
                            "mapping_file": file_name,
                            "mapping_line": line_no,
                            "source_sector": source_sector,
                            "target_sector": target_sector,
                            "direct_map_rejected": was_direct_reject,
                            "momentum_map": {
                                key: {name: str(value) for name, value in vec.items()}
                                for key, vec in momentum_map.items()
                            },
                            "mixed_numerators": mixed_rows,
                        }
                    )
            for row in mixed_rows:
                if len(mixed_samples) >= 30:
                    break
                mixed_samples.append(
                    {
                        "source": _integral_text(source),
                        "mapping_file": file_name,
                        "mapping_line": line_no,
                        **row,
                    }
                )

    summary = {
        "mode": "saved Kira momentum-map diagnostic; no recomputation and no master merging",
        "final_master_forms": len(forms),
        "parsed_mapping_lines": parsed,
        "relevant_master_mapping_applications": relevant_applications,
        "direct_map_rejected_applications": direct_rejects,
        "general_momentum_map_compatible_applications": general_compatible,
        "direct_rejects_explained_by_general_momentum_map": general_compatible_direct_rejects,
        "remaining_direct_rejects_not_yet_compatible": direct_rejects - general_compatible_direct_rejects,
        "positive_sector_mismatches_after_general_map": positive_sector_mismatches,
        "mixed_numerator_isp_occurrences": mixed_numerator_occurrences,
        "mixed_numerator_samples": mixed_samples,
        "compatible_samples": compatible_samples,
        "pass": parsed > 0 and relevant_applications > 0,
    }
    OUTPUT_JSON.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print("parsed mapping lines:", parsed)
    print("relevant master-form mapping applications:", relevant_applications)
    print("direct-map rejected applications:", direct_rejects)
    print("general momentum-map compatible applications:", general_compatible)
    print("direct rejects explained by general momentum map:", general_compatible_direct_rejects)
    print("remaining direct rejects not yet compatible:", direct_rejects - general_compatible_direct_rejects)
    print("positive-sector mismatches after general map:", positive_sector_mismatches)
    print("mixed numerator/ISP transformation occurrences:", mixed_numerator_occurrences)
    print("probe JSON:", OUTPUT_JSON)

    for row in mixed_samples[:8]:
        print(
            "  mixed:",
            row["source"],
            f"P{row['source_P']}^{row['power']} -> {row['image']}",
            f"({row['mapping_file']}:{row['mapping_line']})",
        )

    if not summary["pass"]:
        raise SystemExit("Q01 Kira momentum-map / ISP transformation probe FAIL")
    print("Q01 Kira momentum-map / ISP transformation probe PASS")


if __name__ == "__main__":
    main()
