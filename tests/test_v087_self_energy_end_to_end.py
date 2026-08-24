import sympy as sp
from qedcalc.operations.self_energy import finite_part_expected, total_self_energy_coefficient
from qedcalc.operations.corner import corner_self_energy_ir_cancellation

def test_phase80_self_energy_release_invariants():
    rho=sp.Symbol('rho', positive=True)
    assert sp.simplify(finite_part_expected()-(-sp.Rational(1,24)-sp.pi**2/18)) == 0
    assert sp.simplify(total_self_energy_coefficient(rho)-(sp.log(rho)+sp.Rational(11,24)-sp.pi**2/18)) == 0
    irc=corner_self_energy_ir_cancellation()
    assert irc.total_log_coefficient == 0
