from pathlib import Path
import sympy as sp

from qedcalc.operations.ladder_assembly import (
    compose_ladder_projector_with_reduction,
    ladder_basis_z_pole_residues,
    ladder_basis_z_double_pole_coefficients,
    ladder_projector_leading_z_pole_cancellation,
)

ROOT = Path(__file__).resolve().parents[1]


def _assembly():
    return compose_ladder_projector_with_reduction(
        ROOT / 'data' / 'ladder_corrected_spin_sum_72_coefficients.csv',
        ROOT / 'data' / 'ladder_corrected_40target_12basis_symbolic_reduction.csv',
    )


def test_corrected_72_projector_terms_canonicalize_to_40_targets():
    a = _assembly()
    assert len(a.canonical_target_coefficients) == 40
    assert len(a.basis_coefficients) == 12


def test_reduced_basis_has_only_simple_projector_z_poles():
    a = _assembly()
    z = sp.Symbol('z')
    residues = ladder_basis_z_pole_residues(a.basis_coefficients, z)
    # A simple-pole residue extraction must leave z-independent coefficients.
    assert all(z not in r.free_symbols for r in residues)
    assert [i for i,r in enumerate(residues) if r != 0] == [0,1,3,5,6,7,8]
    # No 1/z^2 pole remains after the 72->40->12 composition.
    assert all(x == 0 for x in ladder_basis_z_double_pole_coefficients(a.basis_coefficients, z))


def test_leading_projector_z_pole_cancels_after_exact_z0_basis_relations():
    a = _assembly()
    D,z = sp.symbols('D z')
    assert ladder_projector_leading_z_pole_cancellation(
        a.basis_coefficients, D=D, mass_squared=1, z=z
    ) == 0
