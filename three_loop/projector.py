"""Unified magnetic-projector interface for the three-loop vertex program.

This module does not introduce a new projector convention.  It exposes the
D-dimensional Pauli-projector coefficients already used by QEDCalc's
ordinary-ladder calculation and connects them to the existing Gordon-basis
F2 extractor.

The finite-q projector coefficients are singular at z=q^2/m^2=0.  Therefore
``q_zero_limit`` deliberately returns Laurent data rather than substituting
z=0 term by term.  A physical q->0 limit must be taken only after the
projected amplitude has been assembled and the singular terms have cancelled.
"""
from __future__ import annotations

from dataclasses import dataclass
import sympy as sp

from qedcalc.operations.ladder import ladder_projector_coefficients
from qedcalc.operations.projector import project_f2_gordon_basis


@dataclass(frozen=True)
class MagneticProjector:
    """D-dimensional Pauli projector metadata.

    Convention:

        P_mu = (1/m^2) (/p' + m)
               [a gamma_mu + b r_mu/m]
               (/p + m),

    where z=q^2/m^2 and ``a`` and ``b`` are the QEDCalc ordinary-ladder
    coefficients.  ``r_mu`` follows the same convention as that existing
    implementation.
    """

    D: sp.Expr
    z: sp.Expr
    a: sp.Expr
    b: sp.Expr

    @classmethod
    def finite_q(cls, D=None, z=None) -> "MagneticProjector":
        D = sp.Symbol("D") if D is None else sp.sympify(D)
        z = sp.Symbol("z") if z is None else sp.sympify(z)
        a, b = ladder_projector_coefficients(D=D, z=z)
        return cls(D=D, z=z, a=sp.factor(a), b=sp.factor(b))

    def q_zero_laurent(self, order: int = 2) -> dict[str, sp.Expr]:
        """Return Laurent expansions about z=0 without illegal direct substitution.

        The returned expressions are diagnostics for cancellation checks.  They
        are *not* by themselves the physical F2(0) projector.
        """
        if order < 1:
            raise ValueError("order must be at least 1")
        return {
            "a": sp.series(self.a, self.z, 0, order).removeO(),
            "b": sp.series(self.b, self.z, 0, order).removeO(),
        }

    def q_zero_pole_coefficients(self) -> dict[str, sp.Expr]:
        """Return the 1/z residues of the finite-q projector coefficients."""
        return {
            "a_residue": sp.simplify(sp.limit(self.z * self.a, self.z, 0)),
            "b_residue": sp.simplify(sp.limit(self.z * self.b, self.z, 0)),
        }


def three_loop_magnetic_projector(D=None, z=None) -> MagneticProjector:
    """Construct the shared finite-q D-dimensional magnetic projector."""
    return MagneticProjector.finite_q(D=D, z=z)


def project_f2_from_reduced_current(expr, index="mu", outgoing="p'", incoming="p", mass="m"):
    """Extract F2 from a current already reduced to the supported Gordon basis.

    This is intentionally a thin three-loop-facing adapter around QEDCalc's
    existing ``project_f2_gordon_basis`` implementation.  It rejects currents
    that have not yet been reduced to ``gamma_mu`` and ``(p'+p)_mu``.
    """
    return project_f2_gordon_basis(
        expr,
        index=index,
        outgoing=outgoing,
        incoming=incoming,
        mass=mass,
    )


def schwinger_gordon_checkpoint(alpha=None, mass=None) -> sp.Expr:
    """Algebraic one-loop normalization checkpoint for the Gordon extractor.

    If the coefficient of (p'+p)_mu is

        B = -alpha/(4*pi*m),

    then QEDCalc's convention F2=-2m B gives Schwinger's alpha/(2*pi).
    This function checks the normalization only; it does not replace the
    one-loop integral calculation.
    """
    alpha = sp.Symbol("alpha", nonzero=True) if alpha is None else sp.sympify(alpha)
    mass = sp.Symbol("m", nonzero=True) if mass is None else sp.sympify(mass)
    B = -alpha / (4 * sp.pi * mass)
    return sp.simplify(-2 * mass * B)
