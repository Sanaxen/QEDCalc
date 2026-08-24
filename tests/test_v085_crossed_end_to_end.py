import sympy as sp
from qedcalc.operations.crossed_ladder import crossed_phase78_end_to_end_checkpoint


def test_phase78_crossed_end_to_end_exact_closure():
    c = crossed_phase78_end_to_end_checkpoint()
    assert c["projector_residual_F1"] == 0
    assert c["projector_residual_F2"] == 0
    assert c["endpoint_divergent_residual"] == 0
    assert c["final_closed_form_residual"] == 0
    assert c["historical_karplus_kroll_gap"] == sp.Rational(1, 32)
    assert c["historical_gap_origin_resolved"] is False
