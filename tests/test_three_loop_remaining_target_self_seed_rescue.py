from qedcalc.operations.ibp import IntegralIndex
from three_loop.remaining_target_self_seed_rescue import combined_sector_seeds


def test_combined_sector_seeds_deduplicates_and_sorts():
    a = IntegralIndex((1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
    b = IntegralIndex((0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
    out = combined_sector_seeds((a, b), (a,))
    assert len(out) == 2
    assert set(out) == {a, b}


def test_combined_sector_seeds_accepts_target_only():
    target = IntegralIndex((1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
    assert combined_sector_seeds((), (target,)) == (target,)
