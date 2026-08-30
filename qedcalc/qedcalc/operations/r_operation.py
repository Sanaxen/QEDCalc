from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Tuple
import sympy as sp

from qedcalc.operations.renormalization import pole_part
from qedcalc.operations.subdiagram import Subdiagram, enumerate_forests


@dataclass(frozen=True)
class CountertermAssignment:
    """Explicit counterterm contribution assigned to one declared subdiagram.

    contribution is an already constructed amplitude contribution.  This is
    deliberate: for a two-loop vertex graph the counterterm graph is often a
    separate amplitude rather than a literal textual replacement in the bare
    expression.
    """
    subdiagram: Subdiagram
    contribution: object
    label: str = ""


@dataclass(frozen=True)
class RenormalizationResult:
    bare: object
    counterterms: Tuple[CountertermAssignment, ...]
    total: object
    pole_part: object
    finite_or_regular: object


def assemble_renormalized_amplitude(bare, assignments: Iterable[CountertermAssignment],
                                    epsilon=None, max_pole_order=8) -> RenormalizationResult:
    """Add explicitly assigned counterterm amplitudes and inspect remaining poles."""
    eps = sp.Symbol("epsilon") if epsilon is None else sp.sympify(epsilon)
    assignments = tuple(assignments)
    total = sp.expand(sp.sympify(bare) + sum((sp.sympify(x.contribution) for x in assignments), sp.Integer(0)))
    poles = pole_part(total, eps, max_pole_order)
    regular = sp.simplify(total - poles)
    return RenormalizationResult(
        bare=sp.sympify(bare),
        counterterms=assignments,
        total=sp.simplify(total),
        pole_part=sp.simplify(poles),
        finite_or_regular=regular,
    )


def validate_counterterm_coverage(subdiagrams: Iterable[Subdiagram],
                                  assignments: Iterable[CountertermAssignment]):
    """Return missing and duplicate counterterm assignments by subdiagram name."""
    subs = tuple(subdiagrams)
    assigns = tuple(assignments)
    counts = {s.name: 0 for s in subs}
    unknown = []
    for a in assigns:
        if a.subdiagram.name in counts:
            counts[a.subdiagram.name] += 1
        else:
            unknown.append(a.subdiagram.name)
    missing = tuple(name for name, count in counts.items() if count == 0)
    duplicate = tuple(name for name, count in counts.items() if count > 1)
    return {
        "missing": missing,
        "duplicate": duplicate,
        "unknown": tuple(unknown),
        "complete": not missing and not duplicate and not unknown,
    }


def renormalization_plan(subdiagrams: Iterable[Subdiagram],
                         assignments: Iterable[CountertermAssignment]):
    """Build non-evaluating topology/bookkeeping information for an R-operation workflow."""
    subs = tuple(subdiagrams)
    assigns = tuple(assignments)
    return {
        "subdiagrams": subs,
        "forests": enumerate_forests(subs),
        "coverage": validate_counterterm_coverage(subs, assigns),
        "assignments": assigns,
    }

@dataclass(frozen=True)
class MinimalRResult:
    """MS-style R operation after explicit subdivergence counterterms are known."""
    subdivergence_result: RenormalizationResult
    overall_counterterm: object
    renormalized: object
    remaining_pole: object


def minimal_counterterm_from_poles(amplitude, epsilon=None, max_pole_order=8):
    """Return the MS-style counterterm amplitude -Pole[amplitude].

    This determines only the pole subtraction.  It must not be used as a
    substitute for finite on-shell renormalization conditions.
    """
    eps = sp.Symbol("epsilon") if epsilon is None else sp.sympify(epsilon)
    return sp.simplify(-pole_part(sp.sympify(amplitude), eps, max_pole_order))


def minimal_r_operation(bare, assignments: Iterable[CountertermAssignment],
                        epsilon=None, max_pole_order=8) -> MinimalRResult:
    """Apply explicit subdivergence counterterms, then subtract the overall MS pole.

    The subdiagram topology/counterterm matching remains explicit.  Once the
    R-prime amplitude is assembled, the remaining overall Laurent pole is
    subtracted automatically in an MS-style scheme.
    """
    eps = sp.Symbol("epsilon") if epsilon is None else sp.sympify(epsilon)
    rprime = assemble_renormalized_amplitude(bare, assignments, eps, max_pole_order)
    overall_ct = minimal_counterterm_from_poles(rprime.total, eps, max_pole_order)
    ren = sp.simplify(sp.expand(rprime.total + overall_ct))
    remaining = pole_part(ren, eps, max_pole_order)
    return MinimalRResult(rprime, overall_ct, ren, sp.simplify(remaining))
