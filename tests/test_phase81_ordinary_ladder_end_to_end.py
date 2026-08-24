from pathlib import Path
import sympy as sp

from qedcalc.operations.ladder import ladder_subtraction_series, ladder_renormalized_checkpoint
from qedcalc.operations.ladder_assembly import (
    compose_ladder_projector_with_reduction,
    ladder_projector_leading_z_pole_cancellation,
)


def test_phase81_ordinary_ladder_release_invariants():
    root = Path(__file__).parents[1]
    assembly = compose_ladder_projector_with_reduction(
        root / "data" / "ladder_corrected_spin_sum_72_coefficients.csv",
        root / "data" / "ladder_corrected_40target_12basis_symbolic_reduction.csv",
    )
    assert len(assembly.canonical_target_coefficients) == 40
    assert len(assembly.basis_coefficients) == 12

    D, z, delta = sp.symbols("D z delta")
    assert sp.simplify(
        ladder_projector_leading_z_pole_cancellation(
            assembly.basis_coefficients, D=D, mass_squared=1, z=z
        )
    ) == 0

    subtraction = ladder_subtraction_series(delta, 1).removeO()
    assert sp.limit(delta * subtraction, delta, 0) == -sp.Rational(3, 4)
    assert sp.limit(subtraction + sp.Rational(3, 4) / delta, delta, 0) == 2
    assert sp.simplify(
        ladder_renormalized_checkpoint(delta)
        - (sp.Rational(11, 48) + sp.pi**2 / 18)
    ) == 0
