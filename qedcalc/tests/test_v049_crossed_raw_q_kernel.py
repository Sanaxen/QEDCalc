from qedcalc.operations.crossed_ladder import (
    crossed_raw_one_variable_kernel_checks,
    crossed_raw_to_canonical_difference,
)


def test_crossed_t_cutoff_cancels():
    checks = crossed_raw_one_variable_kernel_checks()
    assert checks["cutoff_log_coefficient"] == 0
    assert checks["contains_Dq"]
    assert checks["unexpected_polylogs"] == ()


def test_crossed_raw_kernel_matches_canonical_plus_total_derivative():
    assert crossed_raw_to_canonical_difference() == 0
