import sympy as sp


def test_phase77_end_to_end_corner_closure_is_exact():
    from qedcalc.operations.corner import corner_phase77_end_to_end_checkpoint

    a = corner_phase77_end_to_end_checkpoint()
    assert a['soft_log_coefficient'] == 1
    assert a['sector_route_residual'] == 0
    assert a['matching_route_residual'] == 0
    assert a['route_to_route_residual'] == 0
    assert a['closed_form_residual'] == 0
    assert a['combined_ir_log_coefficient'] == 0
    assert a['combined_finite_checkpoint_residual'] == 0
    assert a['checkpoint_used_as_input'] is False
    assert sp.N(a['finite_result'], 16) < 0


def test_phase77_numerical_checkpoint_smoke():
    from qedcalc.operations.corner import corner_phase77_numerical_checkpoint

    a = corner_phase77_numerical_checkpoint(0.05, power=5, seed=17, replicates=2)
    assert a['checkpoint_used_as_input'] is False
    assert a['full_finite_stderr'] >= 0
