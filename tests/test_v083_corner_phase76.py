import sympy as sp


def test_phase76_soft_finite_ownership_is_exact():
    from qedcalc.operations.corner import corner_phase76_soft_finite_ownership_audit
    a=corner_phase76_soft_finite_ownership_audit()
    assert a['ownership_residual'] == 0
    assert a['independent_checkpoint_residual'] == 0
    assert a['checkpoint_used_as_input'] is False
    assert sp.N(a['soft_finite_constant'], 15) < 0


def test_phase76_full_qmc_smoke():
    from qedcalc.operations.corner import corner_phase76_full_finite_qmc
    a=corner_phase76_full_finite_qmc(0.05,power=5,seed=13,replicates=2)
    assert a['checkpoint_used_as_input'] is False
    assert a['full_finite_stderr'] >= 0
