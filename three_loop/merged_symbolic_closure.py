"""Merge exact direct and reverse Q01 symbolic rules and audit their closure."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from qedcalc.operations.ibp import IntegralIndex
from .direct_symbolic_closure import DirectClosureProfile, audit_direct_symbolic_closure
from .direct_symbolic_reduction import DirectSymbolicRule


@dataclass(frozen=True)
class MergedSymbolicClosureProfile:
    direct_rule_count: int
    reverse_rule_count: int
    merged_rule_count: int
    closure: DirectClosureProfile


def merge_symbolic_rules(
    direct_rules: Iterable[DirectSymbolicRule],
    reverse_rules: Iterable[DirectSymbolicRule],
) -> tuple[DirectSymbolicRule, ...]:
    """Merge non-overlapping exact rule sets, rejecting conflicting targets."""
    merged: dict[tuple[int, ...], DirectSymbolicRule] = {}
    for rule in tuple(direct_rules) + tuple(reverse_rules):
        previous = merged.get(rule.target)
        if previous is not None and previous != rule:
            raise ValueError(f"Conflicting symbolic rules for target I{rule.target}")
        merged[rule.target] = rule
    return tuple(merged[key] for key in sorted(merged))


def audit_merged_symbolic_closure(
    targets: Iterable[IntegralIndex],
    direct_rules: Iterable[DirectSymbolicRule],
    reverse_rules: Iterable[DirectSymbolicRule],
) -> MergedSymbolicClosureProfile:
    direct_rules = tuple(direct_rules)
    reverse_rules = tuple(reverse_rules)
    merged = merge_symbolic_rules(direct_rules, reverse_rules)
    closure = audit_direct_symbolic_closure(targets, merged)
    return MergedSymbolicClosureProfile(
        direct_rule_count=len(direct_rules),
        reverse_rule_count=len(reverse_rules),
        merged_rule_count=len(merged),
        closure=closure,
    )
