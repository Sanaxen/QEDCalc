from qedcalc.operations.corner import corner_phase65_raw_radial_sign_ownership_audit


def test_phase65_raw_radial_scalar_master_and_C_sign():
    a=corner_phase65_raw_radial_sign_ownership_audit()
    assert a['scalar_n3_residual'] == 0
    assert a['raw_log_sign'] == 1
    assert a['raw_C_sign'] == -1


def test_phase65_exposes_selective_physical_C_flip():
    a=corner_phase65_raw_radial_sign_ownership_audit()
    assert a['local_B_changes_nonlocal_C'] is False
    assert a['physical_bridge_C_sign'] == 1
    assert a['physical_bridge_minus_raw_C_sign'] == 2

from qedcalc.operations.corner import corner_phase66_physical_C_sign_charge_audit


def test_phase66_charge_condition_uniquely_selects_plus_C():
    a=corner_phase66_physical_C_sign_charge_audit()
    assert a['plus_candidate_residual'] == 0
    assert a['minus_candidate_residual'] != 0
    assert a['resolved_physical_C_sign'] == 1

from qedcalc.operations.corner import corner_phase67_secondary_overlap_measure_audit


def test_phase67_secondary_overlap_measure_is_exact():
    a=corner_phase67_secondary_overlap_measure_audit()
    assert a['B_line_embedding_residual'] == 0
    assert a['a_d_u_r_jacobian_residual'] == 0
