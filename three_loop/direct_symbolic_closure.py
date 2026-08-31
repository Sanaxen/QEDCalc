"""Recursive dependency closure over exact direct symbolic Q01 reduction rules.

The input rules are exact finite-q one-step IBP reductions.  This module follows
those rules transitively without doing any new symbolic Gaussian elimination.
It classifies terminals into unresolved integrals and zero rules, and records
which targets are fully closed within the direct-rule graph.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

from qedcalc.operations.ibp import IntegralIndex, sector_rank
from .direct_symbolic_reduction import DirectSymbolicRule


@dataclass(frozen=True)
class DirectClosureRecord:
    target: tuple[int, ...]
    pivot_nodes: tuple[tuple[int, ...], ...]
    terminal_integrals: tuple[tuple[int, ...], ...]
    zero_terminal_count: int

    @property
    def pivot_node_count(self) -> int:
        return len(self.pivot_nodes)

    @property
    def terminal_count(self) -> int:
        return len(self.terminal_integrals)

    @property
    def fully_closed(self) -> bool:
        return self.terminal_count == 0


@dataclass(frozen=True)
class DirectClosureProfile:
    target_count: int
    rule_count: int
    fully_closed_target_count: int
    target_with_unresolved_terminals_count: int
    max_pivot_node_count: int
    max_terminal_count: int
    records: tuple[DirectClosureRecord, ...]


def _rule_map(rules: Iterable[DirectSymbolicRule]) -> dict[IntegralIndex, DirectSymbolicRule]:
    return {IntegralIndex(rule.target): rule for rule in rules}


def direct_rule_dependency_closure(
    target: IntegralIndex,
    rules: Mapping[IntegralIndex, DirectSymbolicRule] | Iterable[DirectSymbolicRule],
) -> DirectClosureRecord:
    """Follow exact direct rules until only non-rule terminal integrals remain."""
    if not isinstance(rules, Mapping):
        rules = _rule_map(rules)

    pivot_nodes: set[IntegralIndex] = set()
    terminals: set[IntegralIndex] = set()
    zero_terminal_count = 0
    visiting: set[IntegralIndex] = set()

    def visit(index: IntegralIndex) -> None:
        nonlocal zero_terminal_count
        if index in pivot_nodes or index in terminals:
            return
        rule = rules.get(index)
        if rule is None:
            terminals.add(index)
            return
        if index in visiting:
            # The direct-pivot ordering should be acyclic. Treat any unexpected
            # cycle conservatively as an unresolved terminal rather than loop.
            terminals.add(index)
            return
        visiting.add(index)
        pivot_nodes.add(index)
        if not rule.rhs:
            zero_terminal_count += 1
        else:
            for powers, _coeff in rule.rhs:
                visit(IntegralIndex(powers))
        visiting.remove(index)

    visit(target)
    return DirectClosureRecord(
        target=target.powers,
        pivot_nodes=tuple(idx.powers for idx in sorted(pivot_nodes, key=sector_rank, reverse=True)),
        terminal_integrals=tuple(idx.powers for idx in sorted(terminals, key=sector_rank, reverse=True)),
        zero_terminal_count=zero_terminal_count,
    )


def audit_direct_symbolic_closure(
    targets: Iterable[IntegralIndex],
    rules: Iterable[DirectSymbolicRule],
) -> DirectClosureProfile:
    targets = tuple(dict.fromkeys(targets))
    rules = tuple(rules)
    mapping = _rule_map(rules)
    records = tuple(direct_rule_dependency_closure(target, mapping) for target in targets)
    closed = sum(record.fully_closed for record in records)
    return DirectClosureProfile(
        target_count=len(targets),
        rule_count=len(rules),
        fully_closed_target_count=closed,
        target_with_unresolved_terminals_count=len(records) - closed,
        max_pivot_node_count=max((record.pivot_node_count for record in records), default=0),
        max_terminal_count=max((record.terminal_count for record in records), default=0),
        records=records,
    )
