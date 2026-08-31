from qedcalc.operations.ibp import IntegralIndex
from three_loop.q01_exact_symmetry import (
    canonicalize_scalar_under_exact_symmetry,
    discover_q01_exact_signed_loop_symmetries,
)


def test_q01_exact_symmetry_includes_identity():
    symmetries = discover_q01_exact_signed_loop_symmetries()
    assert symmetries
    assert any(
        sym.loop_images == ("k", "l", "r")
        and sym.loop_signs == (1, 1, 1)
        and sym.physical_permutation == tuple(range(9))
        for sym in symmetries
    )


def test_q01_exact_symmetry_canonicalization_preserves_scalar_auxiliary_zeroes():
    symmetries = discover_q01_exact_signed_loop_symmetries()
    index = IntegralIndex((1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 0, 0))
    canonical = canonicalize_scalar_under_exact_symmetry(index, symmetries)
    assert canonical.powers[9:] == (0, 0, 0)
    assert sum(1 for x in canonical.powers[:9] if x > 0) == sum(1 for x in index.powers[:9] if x > 0)
