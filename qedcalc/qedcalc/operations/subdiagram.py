from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Iterable, Tuple, FrozenSet


@dataclass(frozen=True)
class Subdiagram:
    """Topology metadata for a UV/IR subdiagram.

    QEDCalc intentionally does not infer this object from a bare algebraic
    expression.  The caller supplies the factor/edge identifiers that belong
    to the subdiagram, preserving graph-topology information that is absent
    from a plain formula.
    """
    name: str
    kind: str
    loop_order: int
    members: FrozenSet[str]
    divergence: str = "UV"
    superficial_degree: int | None = None

    def __init__(self, name: str, kind: str, loop_order: int,
                 members: Iterable[str], divergence: str = "UV",
                 superficial_degree: int | None = None):
        if loop_order < 1:
            raise ValueError("loop_order must be at least 1.")
        mem = frozenset(str(x) for x in members)
        if not mem:
            raise ValueError("members must contain at least one topology identifier.")
        div = divergence.upper()
        if div not in {"UV", "IR", "UVIR"}:
            raise ValueError("divergence must be 'UV', 'IR', or 'UVIR'.")
        object.__setattr__(self, "name", str(name))
        object.__setattr__(self, "kind", str(kind))
        object.__setattr__(self, "loop_order", int(loop_order))
        object.__setattr__(self, "members", mem)
        object.__setattr__(self, "divergence", div)
        object.__setattr__(self, "superficial_degree", superficial_degree)


def relation(a: Subdiagram, b: Subdiagram) -> str:
    """Return disjoint, nested, equal, or overlapping for two subdiagrams."""
    if a.members == b.members:
        return "equal"
    inter = a.members & b.members
    if not inter:
        return "disjoint"
    if a.members < b.members or b.members < a.members:
        return "nested"
    return "overlapping"


def forest_compatible(a: Subdiagram, b: Subdiagram) -> bool:
    """A Zimmermann forest may contain disjoint or nested subdiagrams."""
    return relation(a, b) in {"disjoint", "nested"}


def is_forest(items: Iterable[Subdiagram]) -> bool:
    seq = tuple(items)
    return all(forest_compatible(a, b) for a, b in combinations(seq, 2))


def enumerate_forests(subdiagrams: Iterable[Subdiagram], include_empty=True) -> Tuple[Tuple[Subdiagram, ...], ...]:
    """Enumerate all compatible subdiagram sets.

    This enumerates topology-compatible forests only.  It does not evaluate
    subtraction operators or contracted graphs by itself.
    """
    subs = tuple(subdiagrams)
    result = []
    if include_empty:
        result.append(tuple())
    for r in range(1, len(subs) + 1):
        for combo in combinations(subs, r):
            if is_forest(combo):
                result.append(combo)
    return tuple(result)
