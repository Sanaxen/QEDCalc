"""Reusable exact master-coefficient synthesis API for three-loop diagrams.

The API deliberately separates diagram-specific preparation from the common
algebraic pipeline.  A caller supplies projected-amplitude terms, a native to
Kira bridge, the selected Kira reduction artifact, and the finalized master
basis.  This module then performs the common steps:

1. expand native integrals to Kira-family targets;
2. load and recursively resolve the Kira FORM reduction graph;
3. collect all projected-amplitude contributions by master integral;
4. canonicalize exact rational functions with Fermat through WSL;
5. audit closure onto the requested final master basis.

No projected trace and no Kira/FireFly solve are launched here.  Those stages
remain separate producers of artifacts and can be selected per integral family.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
import gc
from pathlib import Path
import re
import subprocess
from typing import Callable, Iterable, Sequence

import sympy as sp

from three_loop.kira_form_coefficients import form_coefficient_to_sympy
from three_loop.kira_form_parser import iter_kira_form_rules
from three_loop.kira_reducer import load_master_indices

IndexTuple = tuple[int, ...]
ProjectedTerm = tuple[IndexTuple, sp.Expr]
BridgeFunction = Callable[[IndexTuple], object]
ProgressFunction = Callable[[str], None]


@dataclass(frozen=True)
class MasterCoefficientConfig:
    family: str
    form_export: Path
    masters_file: Path
    final_basis: frozenset[IndexTuple]
    expected_kira_targets: frozenset[IndexTuple] | None = None
    expected_native_terms: int | None = None
    fermat_group_size: int = 128
    fermat_executable: str = "$HOME/fermat/Ferl7/fer64"


@dataclass(frozen=True)
class MasterCoefficientRow:
    indices: IndexTuple
    coefficient: str
    source_contributions: int
    symbols: tuple[str, ...]

    @property
    def nonzero(self) -> bool:
        return not fermat_text_is_zero(self.coefficient)


@dataclass(frozen=True)
class MasterCoefficientResult:
    family: str
    native_terms: int
    bridge_terms_total: int
    bridge_unique_targets: int
    reduction_masters: int
    raw_master_forms: int
    unresolved_integrals: tuple[IndexTuple, ...]
    extra_nonzero_masters: tuple[MasterCoefficientRow, ...]
    rows: tuple[MasterCoefficientRow, ...]

    @property
    def nonzero_final_coefficients(self) -> int:
        return sum(row.nonzero for row in self.rows)

    @property
    def passed(self) -> bool:
        return not self.unresolved_integrals and not self.extra_nonzero_masters


def _indices(values: Iterable[int]) -> IndexTuple:
    return tuple(int(v) for v in values)


def _fmt(family: str, indices: IndexTuple) -> str:
    return f"{family}[{','.join(str(x) for x in indices)}]"


def _sympy_to_fermat(expr: sp.Expr) -> str:
    return sp.sstr(expr).replace("**", "^")


def _strip_fermat_status(block: str) -> str:
    cleaned = " ".join(line.strip() for line in block.splitlines() if line.strip())
    # Depending on terminal buffering Fermat can prepend the previous timing and
    # prompt to the next captured block.  Remove that noise repeatedly.
    cleaned = re.sub(r"^(?:Elapsed CPU time:\s*[0-9.]+\s*>\s*)+", "", cleaned)
    return cleaned.strip()


def fermat_text_is_zero(text: str) -> bool:
    compact = "".join(text.split())
    while compact.startswith("(") and compact.endswith(")"):
        compact = compact[1:-1]
    return compact == "0"


class FermatExactBackend:
    """Exact rational-function canonicalizer using the user's WSL Fermat."""

    def __init__(self, executable: str = "$HOME/fermat/Ferl7/fer64", group_size: int = 128):
        if group_size < 2:
            raise ValueError("Fermat group_size must be >= 2")
        self.executable = executable
        self.group_size = group_size

    def _run_sum(self, parts: Sequence[str], symbols: set[str]) -> str:
        if not parts:
            return "0"
        lines: list[str] = []
        for symbol in sorted(symbols):
            if not symbol.replace("_", "").isalnum() or symbol[0].isdigit():
                raise RuntimeError(f"unsafe Fermat symbol name: {symbol!r}")
            lines.append(f"&(J={symbol});")
        lines.extend([
            "q := " + "+".join(f"({part})" for part in parts) + ";",
            "q;",
            "&q",
        ])
        script = "\n".join(lines) + "\n"
        command = f"cd $(dirname {self.executable}) && {self.executable}"
        proc = subprocess.run(
            ["wsl.exe", "bash", "-lc", command],
            input=script,
            text=True,
            capture_output=True,
            check=False,
        )
        if proc.returncode != 0:
            raise RuntimeError(
                f"Fermat failed with exit code {proc.returncode}; "
                f"stdout tail={proc.stdout[-3000:]!r}; stderr tail={proc.stderr[-3000:]!r}"
            )
        blocks = re.findall(r">\s*(.*?)\n\s*Elapsed CPU time:", proc.stdout, flags=re.S)
        candidates: list[str] = []
        for block in blocks:
            cleaned = _strip_fermat_status(block)
            if not cleaned or cleaned.startswith("Change of polynomial variable:"):
                continue
            candidates.append(cleaned)
        if not candidates:
            raise RuntimeError("could not parse Fermat result; tail:\n" + proc.stdout[-3000:])
        return candidates[-1]

    def self_test(self) -> None:
        result = self._run_sum(["(d+z)/(d-z)", "(d-z)/(d+z)"], {"d", "z"})
        expected = "2*(d^2+z^2)/(d^2-z^2)"
        difference = self._run_sum([result, f"-({expected})"], {"d", "z"})
        if not fermat_text_is_zero(difference):
            raise RuntimeError(
                f"Fermat self-test mismatch: result={result!r}, difference={difference!r}"
            )

    def canonical_sum(
        self,
        parts: Sequence[sp.Expr],
        progress: ProgressFunction | None = None,
    ) -> tuple[str, tuple[str, ...]]:
        if not parts:
            return "0", ()
        symbols: set[str] = set()
        work: list[str] = []
        for expr in parts:
            symbols.update(str(s) for s in expr.free_symbols)
            work.append(_sympy_to_fermat(expr))
        round_no = 0
        while len(work) > 1:
            round_no += 1
            reduced: list[str] = []
            groups = (len(work) + self.group_size - 1) // self.group_size
            for start in range(0, len(work), self.group_size):
                group = work[start : start + self.group_size]
                if len(group) == 1:
                    reduced.append(group[0])
                    continue
                if progress is not None and groups > 1:
                    progress(
                        f"    Fermat round {round_no}: group {start // self.group_size + 1}/{groups} "
                        f"terms={len(group)}"
                    )
                reduced.append(self._run_sum(group, symbols))
            work = reduced
        if len(parts) == 1:
            work[0] = self._run_sum(work, symbols)
        return work[0], tuple(sorted(symbols))


def load_reduction_graph(form_export: Path, masters_file: Path, family: str):
    masters = set(load_master_indices(masters_file, family=family))
    rules: dict[IndexTuple, tuple[tuple[sp.Expr, IndexTuple], ...]] = {}
    zeros: set[IndexTuple] = set()
    for rule in iter_kira_form_rules(form_export, family=family):
        lhs = _indices(rule.lhs.indices)
        if lhs in rules or lhs in zeros:
            raise RuntimeError(f"duplicate FORM rule for {_fmt(family, lhs)}")
        if rule.terms:
            rules[lhs] = tuple(
                (form_coefficient_to_sympy(term.coefficient_form), _indices(term.integral.indices))
                for term in rule.terms
            )
        elif rule.is_zero:
            zeros.add(lhs)
        else:
            raise RuntimeError(f"invalid FORM rule for {_fmt(family, lhs)}")
    return masters, rules, zeros


def make_resolver(masters, rules, zeros, family: str):
    memo: dict[IndexTuple, dict[IndexTuple, sp.Expr] | None] = {}
    active: set[IndexTuple] = set()
    missing: set[IndexTuple] = set()

    def resolve(key: IndexTuple) -> dict[IndexTuple, sp.Expr] | None:
        if key in memo:
            return memo[key]
        if key in masters:
            memo[key] = {key: sp.Integer(1)}
            return memo[key]
        if key in zeros:
            memo[key] = {}
            return memo[key]
        children = rules.get(key)
        if children is None:
            missing.add(key)
            memo[key] = None
            return None
        if key in active:
            raise RuntimeError(f"cycle while resolving {_fmt(family, key)}")
        active.add(key)
        parts: dict[IndexTuple, list[sp.Expr]] = defaultdict(list)
        for coeff, child in children:
            child_map = resolve(child)
            if child_map is None:
                active.remove(key)
                memo[key] = None
                return None
            for master, child_coeff in child_map.items():
                parts[master].append(coeff * child_coeff)
        active.remove(key)
        combined = {master: sp.Add(*values) for master, values in parts.items() if values}
        memo[key] = combined
        return combined

    return resolve, missing


def synthesize_master_coefficients(
    projected_terms: Sequence[ProjectedTerm],
    bridge: BridgeFunction,
    config: MasterCoefficientConfig,
    *,
    progress: ProgressFunction | None = print,
    backend: FermatExactBackend | None = None,
) -> MasterCoefficientResult:
    """Reduce one projected amplitude exactly onto a requested master basis."""
    if config.expected_native_terms is not None and len(projected_terms) != config.expected_native_terms:
        raise RuntimeError(
            f"expected {config.expected_native_terms} projected terms, got {len(projected_terms)}"
        )
    backend = backend or FermatExactBackend(
        executable=config.fermat_executable,
        group_size=config.fermat_group_size,
    )
    backend.self_test()
    if progress is not None:
        progress("Fermat backend self-test: PASS")

    bridge_records: list[tuple[sp.Expr, IndexTuple]] = []
    expanded_unique: set[IndexTuple] = set()
    for native, amplitude_coeff in projected_terms:
        expansion = bridge(native)
        for term in expansion.terms:
            target = _indices(term.kira_indices)
            expanded_unique.add(target)
            bridge_records.append((amplitude_coeff * term.coefficient, target))

    if config.expected_kira_targets is not None and expanded_unique != set(config.expected_kira_targets):
        missing = expanded_unique - set(config.expected_kira_targets)
        extra = set(config.expected_kira_targets) - expanded_unique
        raise RuntimeError(
            f"bridge/target mismatch: bridge-only={len(missing)} target-only={len(extra)}"
        )

    masters, rules, zeros = load_reduction_graph(
        config.form_export, config.masters_file, config.family
    )
    resolve, unresolved = make_resolver(masters, rules, zeros, config.family)
    master_parts: dict[IndexTuple, list[sp.Expr]] = defaultdict(list)
    for amplitude_coeff, target in bridge_records:
        resolved = resolve(target)
        if resolved is None:
            continue
        for master, reduction_coeff in resolved.items():
            master_parts[master].append(amplitude_coeff * reduction_coeff)

    unresolved_tuple = tuple(sorted(unresolved))
    if unresolved_tuple:
        return MasterCoefficientResult(
            family=config.family,
            native_terms=len(projected_terms),
            bridge_terms_total=len(bridge_records),
            bridge_unique_targets=len(expanded_unique),
            reduction_masters=len(masters),
            raw_master_forms=len(master_parts),
            unresolved_integrals=unresolved_tuple,
            extra_nonzero_masters=(),
            rows=(),
        )

    del resolve, rules, zeros, bridge_records
    gc.collect()

    rows_by_master: dict[IndexTuple, MasterCoefficientRow] = {}
    ordered = sorted(master_parts)
    total = len(ordered)
    for pos, master in enumerate(ordered, 1):
        parts = master_parts.pop(master)
        if progress is not None:
            progress(
                f"canonicalizing {pos}/{total}: {_fmt(config.family, master)} "
                f"contributions={len(parts)} final_basis={master in config.final_basis}"
            )
        coefficient, symbols = backend.canonical_sum(parts, progress=progress)
        rows_by_master[master] = MasterCoefficientRow(
            indices=master,
            coefficient=coefficient,
            source_contributions=len(parts),
            symbols=symbols,
        )
        del parts
        gc.collect()

    final_rows: list[MasterCoefficientRow] = []
    for master in sorted(config.final_basis):
        final_rows.append(
            rows_by_master.get(
                master,
                MasterCoefficientRow(master, "0", 0, ()),
            )
        )
    extras = tuple(
        row
        for master, row in sorted(rows_by_master.items())
        if master not in config.final_basis and row.nonzero
    )
    return MasterCoefficientResult(
        family=config.family,
        native_terms=len(projected_terms),
        bridge_terms_total=sum(row.source_contributions for row in rows_by_master.values()),
        bridge_unique_targets=len(expanded_unique),
        reduction_masters=len(masters),
        raw_master_forms=len(rows_by_master),
        unresolved_integrals=(),
        extra_nonzero_masters=extras,
        rows=tuple(final_rows),
    )
