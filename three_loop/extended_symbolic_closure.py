"""Merge direct, reverse, and dot-boundary exact Q01 symbolic rules."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from qedcalc.operations.ibp import IntegralIndex
from .direct_symbolic_closure import DirectClosureProfile, audit_direct_symbolic_closure
from .direct_symbolic_reduction import DirectSymbolicRule
from .merged_symbolic_closure import merge_symbolic_rules


@dataclass(frozen=True)
class ExtendedSymbolicClosureProfile:
    direct_rule_count: int
    reverse_rule_count: int
    dot_boundary_rule_count: int
    merged_rule_count: int
    closure: DirectClosureProfile


def audit_extended_symbolic_closure(
    targets: Iterable[IntegralIndex],
    direct_rules: Iterable[DirectSymbolicRule],
    reverse_rules: Iterable[DirectSymbolicRule],
    dot_boundary_rules: Iterable[DirectSymbolicRule],
) -> ExtendedSymbolicClosureProfile:
    direct_rules = tuple(direct_rules)
    reverse_rules = tuple(reverse_rules)
    dot_boundary_rules = tuple(dot_boundary_rules)
    base = merge_symbolic_rules(direct_rules, reverse_rules)
    merged = merge_symbolic_rules(base, dot_boundary_rules)
    closure = audit_direct_symbolic_closure(targets, merged)
    return ExtendedSymbolicClosureProfile(
        direct_rule_count=len(direct_rules),
        reverse_rule_count=len(reverse_rules),
        dot_boundary_rule_count=len(dot_boundary_rules),
        merged_rule_count=len(merged),
        closure=closure,
    )
