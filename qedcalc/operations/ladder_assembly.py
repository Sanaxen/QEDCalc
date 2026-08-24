from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping
import csv
import ast
import sympy as sp

from qedcalc.operations.ibp import IntegralIndex
from qedcalc.operations.ladder import (
    LadderIntegralIndex,
    canonicalize_ordinary_ladder_integral,
    load_ladder_coefficient_table,
)
from qedcalc.operations.master_integrals import (
    ordinary_ladder_basis_z0_evaluations,
    ordinary_ladder_basis_z_derivative_evaluations,
)


@dataclass(frozen=True)
class LadderBasisAssembly:
    """Projector coefficients composed with the 40->12 symbolic IBP matrix."""

    canonical_target_coefficients: Mapping[IntegralIndex, sp.Expr]
    basis_coefficients: tuple[sp.Expr, ...]


def canonicalize_ladder_coefficient_table(
    table: Mapping[LadderIntegralIndex, sp.Expr],
) -> dict[IntegralIndex, sp.Expr]:
    """Combine a raw ladder coefficient table on graph-symmetry orbits."""
    out: dict[IntegralIndex, sp.Expr] = {}
    for idx, coeff in table.items():
        cidx = canonicalize_ordinary_ladder_integral(IntegralIndex(idx.as_tuple()))
        out[cidx] = sp.cancel(out.get(cidx, 0) + sp.sympify(coeff))
    return out


def load_ladder_symbolic_reduction_matrix(path) -> dict[tuple[IntegralIndex, int], sp.Expr]:
    """Load the v0.41 40-target x 12-basis exact symbolic reduction matrix."""
    D, z = sp.symbols("D z")
    out: dict[tuple[IntegralIndex, int], sp.Expr] = {}
    with Path(path).open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            powers = ast.literal_eval(row["target"])
            target = IntegralIndex(tuple(int(x) for x in powers))
            bi = int(row["basis_index"])
            out[(target, bi)] = sp.sympify(row["coefficient"], locals={"D": D, "z": z})
    return out


def compose_ladder_projector_with_reduction(
    coefficient_table_path,
    reduction_matrix_path,
    basis_size: int = 12,
) -> LadderBasisAssembly:
    """Compose the corrected raw projector table with the exact IBP reduction.

    This operation is deliberately performed at generic z.  Setting z=0 before
    composition is unsafe because the magnetic projector introduces 1/z terms.
    """
    table = load_ladder_coefficient_table(coefficient_table_path)
    targets = canonicalize_ladder_coefficient_table(table)
    matrix = load_ladder_symbolic_reduction_matrix(reduction_matrix_path)
    basis = []
    for bi in range(int(basis_size)):
        expr = sp.Add(*(coeff * matrix[(target, bi)] for target, coeff in targets.items()), evaluate=False)
        basis.append(expr)
    return LadderBasisAssembly(targets, tuple(basis))


def ladder_basis_z_pole_residues(
    basis_coefficients,
    z=None,
) -> tuple[sp.Expr, ...]:
    """Return residues of possible simple 1/z poles in basis coefficients."""
    z = sp.Symbol("z") if z is None else sp.sympify(z)
    out = []
    for coeff in basis_coefficients:
        expr = sp.sympify(coeff)
        terms = expr.args if isinstance(expr, sp.Add) else (expr,)
        residue = sp.Add(*(sp.limit(z * term, z, 0) for term in terms))
        out.append(sp.factor(sp.cancel(residue)))
    return tuple(out)



def ladder_basis_z_double_pole_coefficients(
    basis_coefficients,
    z=None,
) -> tuple[sp.Expr, ...]:
    """Return coefficients of possible 1/z^2 terms, evaluated termwise."""
    z = sp.Symbol("z") if z is None else sp.sympify(z)
    out = []
    for coeff in basis_coefficients:
        expr = sp.sympify(coeff)
        terms = expr.args if isinstance(expr, sp.Add) else (expr,)
        value = sp.Add(*(sp.limit(z**2 * term, z, 0) for term in terms))
        out.append(sp.factor(sp.cancel(value)))
    return tuple(out)

def ladder_projector_leading_z_pole_cancellation(
    basis_coefficients,
    D=None,
    mass_squared=None,
    z=None,
):
    """Check cancellation of the leading magnetic-projector 1/z pole.

    Individual reduced-basis coefficients may contain 1/z.  The physical sum
    must be formed before the z->0 limit.  At leading order the pole coefficient
    is sum_i r_i(D) I_i(0), where r_i is the basis-coefficient residue.  This
    helper inserts the exact v0.43 z=0 values and returns the simplified sum.
    The v0.41 symbolic reduction matrix is normalized with m^2=1, so this
    helper defaults to mass_squared=1.
    """
    D = sp.Symbol("D") if D is None else sp.sympify(D)
    m2 = sp.Integer(1) if mass_squared is None else sp.sympify(mass_squared)
    residues = ladder_basis_z_pole_residues(basis_coefficients, z=z)
    values = ordinary_ladder_basis_z0_evaluations(D=D, mass_squared=m2)
    if len(values) != len(residues):
        raise ValueError("Basis coefficient count does not match the z=0 basis registry.")
    total = sp.Add(*(r * item.value for r, item in zip(residues, values)))
    return sp.simplify(total)


def ladder_projector_derivative_weights(
    basis_coefficients,
    z=None,
) -> tuple[sp.Expr, ...]:
    """Weights multiplying I_i'(0) in the finite z->0 projector limit.

    If C_i(z)=r_i/z+c_i+..., then C_i(z) I_i(z) contributes r_i I_i'(0)
    to the finite term after the leading pole cancels.  These weights identify
    exactly which basis derivatives are required by the next evaluation stage.
    """
    return ladder_basis_z_pole_residues(basis_coefficients, z=z)



def ladder_basis_z_regular_parts(basis_coefficients, z=None) -> tuple[sp.Expr, ...]:
    """Return the finite z^0 part of every reduced-basis coefficient.

    The extraction is performed term by term so large Add expressions do not
    have to be combined before the removable 1/z pieces are subtracted.
    """
    z = sp.Symbol("z") if z is None else sp.sympify(z)
    out = []
    for coeff in basis_coefficients:
        expr = sp.sympify(coeff)
        terms = expr.args if isinstance(expr, sp.Add) else (expr,)
        finite_terms = []
        for term in terms:
            residue = sp.limit(z * term, z, 0)
            finite_terms.append(sp.limit(term - residue / z, z, 0))
        out.append(sp.factor(sp.cancel(sp.Add(*finite_terms))))
    return tuple(out)


def ladder_projector_finite_z_expression(
    basis_coefficients,
    D=None,
    mass_squared=None,
    z=None,
):
    r"""Assemble the convention-free Euclidean finite z->0 ladder projector.

    If C_i(z)=r_i/z+c_i+O(z) and I_i(z)=I_i(0)+z I_i'(0)+O(z^2),
    the finite term after the exact leading-pole cancellation is

        sum_i [ c_i I_i(0) + r_i I_i'(0) ].

    v0.44 evaluates every derivative carrying a nonzero r_i analytically.
    The result still excludes loop-measure/coupling convention factors.
    """
    D = sp.Symbol("D") if D is None else sp.sympify(D)
    m2 = sp.Integer(1) if mass_squared is None else sp.sympify(mass_squared)
    residues = ladder_basis_z_pole_residues(basis_coefficients, z=z)
    regular = ladder_basis_z_regular_parts(basis_coefficients, z=z)
    values = ordinary_ladder_basis_z0_evaluations(D=D, mass_squared=m2)
    derivatives = ordinary_ladder_basis_z_derivative_evaluations(D=D, mass_squared=m2)
    if not (len(residues) == len(regular) == len(values) == len(derivatives)):
        raise ValueError("Basis registries do not have the same size.")
    missing = [item.basis_index for item, r in zip(derivatives, residues)
               if r != 0 and item.value is None]
    if missing:
        raise ValueError(f"Missing required z derivatives for basis indices {missing}.")
    pieces = []
    for c, r, v, dv in zip(regular, residues, values, derivatives):
        pieces.append(c * v.value)
        if r != 0:
            pieces.append(r * dv.value)
    return sp.Add(*pieces, evaluate=False)


def ladder_checkpoint_measure_factor(D=None):
    r"""Two-loop normalization used by the archived ordinary-ladder checkpoint.

    The master-integral layer returns raw Euclidean d^Dk d^Dl integrals, with
    a factor pi^D generated by the Gaussian integrations.  The historical
    ladder checkpoint uses the common normalized two-loop measure with one
    e^(gamma_E epsilon)/(i*pi^(D/2)) factor per loop.  With
    D=4-2 epsilon and after converting e^4 to (alpha/pi)^2 this gives

        exp[-gamma_E (D-4)] / (16*pi^D).

    This factor is deliberately kept outside the convention-free master layer.
    """
    D = sp.Symbol("D") if D is None else sp.sympify(D)
    return sp.exp(-sp.EulerGamma * (D - 4)) / (16 * sp.pi**D)


def ladder_projector_checkpoint_normalized_expression(
    basis_coefficients,
    D=None,
    mass_squared=None,
    z=None,
):
    """Finite-z projector expression in the historical checkpoint measure."""
    D = sp.Symbol("D") if D is None else sp.sympify(D)
    return ladder_checkpoint_measure_factor(D) * ladder_projector_finite_z_expression(
        basis_coefficients, D=D, mass_squared=mass_squared, z=z,
    )
