from qedcalc.operations.crossed_ladder import crossed_automatic_hermite_checks


def test_crossed_automatic_hermite_reproduces_audited_reduction():
    checks = crossed_automatic_hermite_checks()
    assert checks["G_difference"] == 0
    assert checks["canonical_difference"] == 0
    assert checks["raw_reconstruction_difference"] == 0
