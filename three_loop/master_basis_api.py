"""Reusable stage-2 master-basis identification API for three-loop families.

This module centralizes the routine parts of the 45-family master-basis stage:

- derive a canonical FamilySpec from the executable 72-diagram registry;
- regenerate the 12-entry Kira family from the representative topology;
- render Kira/Fermat or Kira/FireFly jobs;
- clean runtime state;
- parse ``masters.final``;
- build r/s/d one-axis boundary seeds;
- compare master sets and construct their union/intersection;
- derive the minimum seed envelope required by an explicit target set.

The API deliberately does not launch WSL/Kira itself. Windows/WSL execution
remains in the thin BAT/CLI layer so long calculations are restartable and easy
to inspect.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
import re
import shutil
from typing import Any, Iterable, Sequence

import sympy as sp

from three_loop.canonical_family_bootstrap import (
    complete_with_quadratic_auxiliaries,
    deduplicate_exact_denominators,
    topology_physical_denominators,
)
from three_loop.canonical_family_registry import apply_confirmed_family_registry
from three_loop.integral_family_classification import (
    build_global_classification,
    load_topologies,
    validate_global_audit,
)
from three_loop.q01_family_equivalence import _electron_momenta, _vec


@dataclass(frozen=True, order=True)
class Seed:
    r: int
    s: int = 0
    d: int = 0

    def __post_init__(self) -> None:
        if self.r < 0 or self.s < 0 or self.d < 0:
            raise ValueError(f"seed limits must be non-negative: {self}")

    @property
    def tag(self) -> str:
        return f"r{self.r}s{self.s}d{self.d}"

    def one_axis_extensions(self) -> tuple["Seed", "Seed", "Seed"]:
        return (
            Seed(self.r + 1, self.s, self.d),
            Seed(self.r, self.s + 1, self.d),
            Seed(self.r, self.s, self.d + 1),
        )


@dataclass(frozen=True)
class PropagatorSpec:
    momentum: str
    mass: str


@dataclass(frozen=True)
class FamilySpec:
    family_id: str
    representative: str
    diagrams: tuple[str, ...]
    topology_family: str
    propagators: tuple[PropagatorSpec, ...]
    top_sector: int
    unique_physical_count: int
    auxiliary_names: tuple[str, ...]
    raw_to_unique: tuple[int, ...]
    duplicate_groups: tuple[tuple[int, ...], ...]
    baseline_seed: Seed
    master_basis_id: str | None = None

    @property
    def auxiliary_count(self) -> int:
        return len(self.auxiliary_names)

    def to_dict(self) -> dict[str, Any]:
        out = asdict(self)
        out["baseline_seed"] = asdict(self.baseline_seed)
        return out


def _normalize_vector_sign(momentum: dict[str, sp.Expr]) -> dict[str, sp.Expr]:
    for name in ("k", "l", "r"):
        value = sp.expand(momentum.get(name, 0))
        if value == 0:
            continue
        if value.could_extract_minus_sign():
            return {key: sp.expand(-val) for key, val in momentum.items()}
        break
    return {key: sp.expand(val) for key, val in momentum.items()}


def _vector_to_kira(momentum: dict[str, sp.Expr]) -> str:
    momentum = _normalize_vector_sign(momentum)
    order = ("k", "l", "r", "p", "q")
    terms: list[str] = []
    for name in order:
        value = sp.expand(momentum.get(name, 0))
        if value == 0:
            continue
        if value == 1:
            token = name
        elif value == -1:
            token = f"-{name}"
        elif value.is_Integer:
            token = f"{int(value)}*{name}"
        else:
            token = f"({sp.sstr(value)})*{name}"
        terms.append(token)
    if not terms:
        return "0"
    text = terms[0]
    for token in terms[1:]:
        text += token if token.startswith("-") else f"+{token}"
    return text


def _aux_name_to_momentum(name: str) -> str:
    if not (name.startswith("(") and name.endswith(")^2")):
        raise ValueError(f"unsupported quadratic auxiliary name: {name}")
    return name[1:-3].replace(" ", "")


def _baseline_seed(unique_physical_count: int) -> Seed:
    return Seed(r=unique_physical_count, s=3, d=0)


def _global_registry() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows = load_topologies()
    audit = build_global_classification(rows)
    errors = validate_global_audit(audit)
    errors.extend(apply_confirmed_family_registry(rows, audit))
    if errors:
        raise ValueError("canonical registry validation failed: " + "; ".join(errors))
    if not audit.get("classification_complete"):
        raise ValueError("canonical registry is not complete")
    return rows, audit


def _raw_specs_and_auxiliaries(
    row: dict[str, Any],
) -> tuple[list[tuple[bool, dict[str, sp.Expr]]], list[sp.Expr], list[str]]:
    """Return raw physical specs/expressions and selected auxiliary names.

    The existing autodiscovery modules remain the source of truth for the
    non-quenched denominator formulae. This keeps stage-2 Kira generation
    algebraically aligned with the already-proven canonical registry.
    """
    topology = str(row.get("family"))
    representative = str(row.get("id"))

    if topology == "quenched":
        specs: list[tuple[bool, dict[str, sp.Expr]]] = []
        for vec in _electron_momenta(row):
            specs.append((True, vec))
        for edge in row.get("photon_edges", []):
            specs.append((False, _vec(**{str(edge["label"]): 1})))
        raw_exprs = topology_physical_denominators(row)
        unique, _, _ = deduplicate_exact_denominators(raw_exprs)
        aux_names, _, _ = complete_with_quadratic_auxiliaries(unique)
        return specs, raw_exprs, aux_names

    if topology == "vp1_insert":
        from three_loop.vp1_family_autodiscovery import (
            _complete_vp1_auxiliaries,
            _vp1_denominator_specs,
            vp1_physical_denominators,
        )

        specs = list(_vp1_denominator_specs(row))
        raw_exprs = vp1_physical_denominators(row)
        unique, _, _ = deduplicate_exact_denominators(raw_exprs)
        aux_names, _, _ = _complete_vp1_auxiliaries(unique)
        return specs, raw_exprs, aux_names

    if topology in {"vp2_insert", "vp1_double"}:
        from three_loop.vp2_double_family_autodiscovery import (
            _complete_auxiliaries,
            _formula_denominator_specs,
            physical_denominators,
        )

        specs = list(_formula_denominator_specs(representative))
        raw_exprs = physical_denominators(representative)
        unique, _, _ = deduplicate_exact_denominators(raw_exprs)
        aux_names, _, _ = _complete_auxiliaries(unique)
        return specs, raw_exprs, aux_names

    if topology == "external_lbl":
        from three_loop.lbl_family_autodiscovery import (
            _formula_denominator_specs,
            physical_denominators,
        )
        from three_loop.vp1_family_autodiscovery import _complete_vp1_auxiliaries

        specs = list(_formula_denominator_specs(representative))
        raw_exprs = physical_denominators(representative)
        unique, _, _ = deduplicate_exact_denominators(raw_exprs)
        aux_names, _, _ = _complete_vp1_auxiliaries(unique)
        return specs, raw_exprs, aux_names

    raise ValueError(f"{representative}: unsupported topology family {topology!r}")


def build_family_spec(family_id: str) -> FamilySpec:
    """Build a Kira-ready family spec from the exact canonical registry."""
    rows, audit = _global_registry()
    by_id = {str(row["id"]): row for row in rows}
    family = audit.get("canonical_registry", {}).get(family_id)
    if family is None:
        raise KeyError(f"unknown canonical family: {family_id}")

    representative = str(family["representative"])
    row = by_id[representative]
    topology = str(row.get("family"))
    raw_specs, raw_exprs, aux_names = _raw_specs_and_auxiliaries(row)
    unique_exprs, raw_to_unique, duplicate_groups = deduplicate_exact_denominators(raw_exprs)

    raw_pairs = [
        PropagatorSpec(_vector_to_kira(vec), "m2" if massive else "0")
        for massive, vec in raw_specs
    ]
    if len(raw_pairs) != len(raw_exprs):
        raise ValueError(
            f"{family_id}: raw pair/expression count mismatch "
            f"pairs={len(raw_pairs)} expressions={len(raw_exprs)}"
        )

    unique_pairs: list[PropagatorSpec] = []
    for original_index, unique_index in enumerate(raw_to_unique):
        if unique_index == len(unique_pairs) + 1:
            unique_pairs.append(raw_pairs[original_index])
    if len(unique_pairs) != len(unique_exprs):
        raise ValueError(
            f"{family_id}: pair/expression dedup mismatch "
            f"pairs={len(unique_pairs)} expressions={len(unique_exprs)}"
        )

    propagators = tuple(unique_pairs) + tuple(
        PropagatorSpec(_aux_name_to_momentum(name), "0") for name in aux_names
    )
    if len(propagators) != 12:
        raise ValueError(f"{family_id}: expected 12 propagators, got {len(propagators)}")

    physical_count = len(unique_pairs)
    top_sector = (1 << physical_count) - 1
    return FamilySpec(
        family_id=family_id,
        representative=representative,
        diagrams=tuple(str(x) for x in family.get("confirmed_diagrams", [])),
        topology_family=topology,
        propagators=propagators,
        top_sector=top_sector,
        unique_physical_count=physical_count,
        auxiliary_names=tuple(aux_names),
        raw_to_unique=tuple(int(x) for x in raw_to_unique),
        duplicate_groups=tuple(tuple(int(x) for x in group) for group in duplicate_groups),
        baseline_seed=_baseline_seed(physical_count),
        master_basis_id=family.get("master_basis_id"),
    )


def render_integralfamilies_yaml(spec: FamilySpec) -> str:
    lines = [
        "integralfamilies:",
        f'  - name: "{spec.family_id}"',
        "    loop_momenta: [k, l, r]",
        f"    top_level_sectors: [{spec.top_sector}]",
        "    propagators:",
    ]
    for prop in spec.propagators:
        mass = "0" if prop.mass == "0" else json.dumps(prop.mass)
        lines.append(f'      - ["{prop.momentum}", {mass}]')
    return "\n".join(lines) + "\n"


def render_kinematics_yaml() -> str:
    return """kinematics:
  outgoing_momenta: [p, q]
  kinematic_invariants:
    - [m2, 2]
    - [z, 0]
  scalarproduct_rules:
    - [[p,p], "m2"]
    - [[q,q], "z*m2"]
    - [[p,q], "-z*m2/2"]
  symbol_to_replace_by_one: m2
"""


def render_jobs_yaml(
    spec: FamilySpec,
    seed: Seed,
    *,
    solver: str = "ordinary",
    mandatory_file: str | None = None,
) -> str:
    if solver not in {"ordinary", "firefly"}:
        raise ValueError(f"unsupported solver: {solver}")
    if mandatory_file:
        selection = (
            "        select_mandatory_list:\n"
            f"          - [{spec.family_id},{mandatory_file}]"
        )
    else:
        selection = (
            "        select_mandatory_recursively:\n"
            f"          - {{topologies: [{spec.family_id}], sectors: [{spec.top_sector}], "
            f"r: {seed.r}, s: {seed.s}, d: {seed.d}}}"
        )
    triangular = "false" if solver == "firefly" else "sectorwise"
    back = "false" if solver == "firefly" else "true"
    firefly = "true" if solver == "firefly" else "false"
    return f"""jobs:
  - reduce_sectors:
      reduce:
        - {{topologies: [{spec.family_id}], sectors: [{spec.top_sector}], r: {seed.r}, s: {seed.s}, d: {seed.d}}}
      select_integrals:
{selection}
      run_symmetries: true
      run_initiate: true
      run_triangular: {triangular}
      run_back_substitution: {back}
      run_firefly: {firefly}
"""


def clean_runtime_outputs(project: str | Path) -> list[str]:
    project = Path(project)
    removed: list[str] = []
    for name in (
        "results", "sectormappings", "tmp", "firefly_saves", "ff_save",
        "firefly_saves_alt", "pyred",
    ):
        path = project / name
        if path.is_dir():
            shutil.rmtree(path)
            removed.append(str(path))
        elif path.exists():
            path.unlink()
            removed.append(str(path))
    for pattern in ("*.log", "*.log.gz"):
        for path in project.glob(pattern):
            path.unlink()
            removed.append(str(path))
    return removed


def export_kira_project(
    spec: FamilySpec,
    root: str | Path,
    *,
    seed: Seed | None = None,
    solver: str = "ordinary",
    mandatory_file: str | None = None,
    clean: bool = True,
) -> Path:
    root = Path(root)
    seed = seed or spec.baseline_seed
    root.mkdir(parents=True, exist_ok=True)
    if clean:
        clean_runtime_outputs(root)
    config = root / "config"
    config.mkdir(parents=True, exist_ok=True)
    (config / "integralfamilies.yaml").write_text(
        render_integralfamilies_yaml(spec), encoding="utf-8", newline="\n"
    )
    (config / "kinematics.yaml").write_text(
        render_kinematics_yaml(), encoding="utf-8", newline="\n"
    )
    (root / "jobs.yaml").write_text(
        render_jobs_yaml(spec, seed, solver=solver, mandatory_file=mandatory_file),
        encoding="utf-8", newline="\n",
    )
    manifest = {
        "schema_version": 1,
        "stage": "master_basis_identification",
        "family": spec.to_dict(),
        "seed": asdict(seed),
        "solver": solver,
        "mandatory_file": mandatory_file,
    }
    (root / "qedcalc_master_basis_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8", newline="\n"
    )
    return root


def parse_integral(text: str) -> tuple[str, tuple[int, ...]]:
    match = re.fullmatch(r"\s*([A-Za-z0-9_]+)\s*\[([^\]]+)\]\s*", text)
    if not match:
        raise ValueError(f"not a Kira integral: {text!r}")
    values = tuple(int(x.strip()) for x in match.group(2).split(","))
    return match.group(1), values


def parse_masters_final(path: str | Path, family_id: str) -> list[str]:
    path = Path(path)
    pattern = re.compile(rf"{re.escape(family_id)}\s*\[[^\]]+\]")
    out: list[str] = []
    seen: set[str] = set()
    for item in pattern.findall(path.read_text(encoding="utf-8", errors="replace")):
        item = re.sub(r"\s+", "", item)
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def find_single_masters_final(project: str | Path, family_id: str) -> tuple[Path, list[str]]:
    candidates = sorted(Path(project).rglob("masters.final"), key=lambda p: str(p))
    if len(candidates) != 1:
        raise ValueError(f"{family_id}: expected one masters.final, found {len(candidates)}")
    masters = parse_masters_final(candidates[0], family_id)
    if not masters:
        raise ValueError(f"{family_id}: no masters parsed from {candidates[0]}")
    return candidates[0], masters


def compare_master_sets(named_sets: dict[str, Iterable[str]]) -> dict[str, Any]:
    normalized = {name: set(values) for name, values in named_sets.items()}
    if not normalized:
        raise ValueError("no master sets supplied")
    values = list(normalized.values())
    union = set().union(*values)
    intersection = set.intersection(*values)
    pairs: dict[str, Any] = {}
    names = list(normalized)
    for i, left_name in enumerate(names):
        for right_name in names[i + 1:]:
            left = normalized[left_name]
            right = normalized[right_name]
            pairs[f"{left_name}__{right_name}"] = {
                "intersection": len(left & right),
                "left_only": len(left - right),
                "right_only": len(right - left),
            }
    return {
        "counts": {name: len(values) for name, values in normalized.items()},
        "intersection": sorted(intersection),
        "intersection_count": len(intersection),
        "union": sorted(union),
        "union_count": len(union),
        "pairs": pairs,
    }


def integral_complexity(indices: Sequence[int]) -> Seed:
    r = sum(max(int(a), 0) for a in indices)
    s = sum(max(-int(a), 0) for a in indices)
    d = sum(max(int(a) - 1, 0) for a in indices)
    return Seed(r=r, s=s, d=d)


def required_envelope(targets: Iterable[str], *, floor: Seed | None = None) -> Seed:
    max_r = floor.r if floor else 0
    max_s = floor.s if floor else 0
    max_d = floor.d if floor else 0
    for target in targets:
        _, indices = parse_integral(target)
        c = integral_complexity(indices)
        max_r = max(max_r, c.r)
        max_s = max(max_s, c.s)
        max_d = max(max_d, c.d)
    return Seed(max_r, max_s, max_d)
