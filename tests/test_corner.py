import sympy as sp

from qedcalc.operations.corner import (
    corner_soft_kernel,
    corner_soft_spatial_kernel,
    corner_soft_integrate_S,
    corner_soft_integrate_R,
    corner_soft_ir_coefficient,
    corner_shifted_p_minus_k,
    corner_hard_primary_result,
    corner_shift_correction_result,
    corner_hard_total_result,
    corner_z_sector_result,
    corner_finite_result,
    corner_expected_finite_result,
    corner_result_difference,
    corner_self_energy_ir_cancellation,
)


def test_corner_soft_kernel_factorization():
    U,R,S,v = sp.symbols('U R S v', positive=True)
    lhs = corner_soft_kernel(U,R,S,v)
    rhs = sp.simplify(U/(1+U**2) * corner_soft_spatial_kernel(R,S,v))
    assert sp.simplify(lhs-rhs) == 0


def test_corner_soft_spatial_integrals():
    R,S,v = sp.symbols('R S v', positive=True)
    direct_S = sp.integrate(corner_soft_spatial_kernel(R,S,v), (S,0,sp.oo))
    assert sp.simplify(direct_S - corner_soft_integrate_S(R,v)) == 0
    direct_R = sp.integrate(corner_soft_integrate_S(R,v), (R,0,sp.oo))
    assert sp.simplify(direct_R - corner_soft_integrate_R(v)) == 0
    assert corner_soft_ir_coefficient() == 1


def test_corner_shift_coefficients():
    u,v = sp.symbols('u v')
    c = corner_shifted_p_minus_k(u,v)
    assert sp.simplify(c['p_prime']-(1-u*v)) == 0
    assert sp.simplify(c['p_double_prime']+u*(1-v)) == 0
    assert c['k'] == -1


def test_corner_hard_sector_sum():
    expected = (-sp.Rational(11,3) - sp.Rational(9,8)*sp.zeta(3)
                + sp.pi**2/18 + sp.Rational(7,12)*sp.pi**2*sp.log(2))
    assert sp.simplify(corner_hard_primary_result()+corner_shift_correction_result()-expected) == 0
    assert sp.simplify(corner_hard_total_result()-expected) == 0


def test_corner_z_sector():
    expected = sp.Rational(7,8)+sp.Rational(5,8)*sp.zeta(3)-sp.pi**2*sp.log(2)/4
    assert sp.simplify(corner_z_sector_result()-expected) == 0


def test_corner_final_finite_part():
    assert corner_result_difference() == 0
    assert sp.simplify(corner_finite_result()-corner_expected_finite_result()) == 0


def test_corner_self_energy_ir_cancellation():
    c = corner_self_energy_ir_cancellation()
    assert c.corner_log_coefficient == 1
    assert c.self_energy_log_coefficient == -1
    assert c.total_log_coefficient == 0
    expected = -sp.Rational(7,3)-sp.zeta(3)/2+sp.pi**2*sp.log(2)/3
    assert sp.simplify(c.combined_finite-expected) == 0


def test_corner_soft_hard_diagnostic_split():
    from qedcalc.operations.corner import (
        corner_soft_finite_constant,
        corner_hard_remainder_from_soft_split,
        corner_soft_hard_split_difference,
    )
    expected_soft = sp.pi**2/6 + sp.log(2)**2 - 3*sp.log(2) - sp.Rational(7,4)
    assert sp.simplify(corner_soft_finite_constant()-expected_soft) == 0
    expected_hard = (-sp.Rational(25,24)-sp.pi**2/9-sp.log(2)**2+3*sp.log(2)
                     -sp.zeta(3)/2+sp.pi**2*sp.log(2)/3)
    assert sp.simplify(corner_hard_remainder_from_soft_split()-expected_hard) == 0
    assert corner_soft_hard_split_difference() == 0


def test_v055_raw_corner_pair_recognizes_two_feynman_diagrams():
    from qedcalc.operations.corner import corner_raw_pair_audit
    r=corner_raw_pair_audit()
    assert r.diagram5.electron_labels == ("p'-k","p-k","p-k-l","p-l")
    assert r.diagram4.electron_labels == ("p'-k","p'-k-l","p'-l","p-l")
    assert r.diagram5.inner_vertex_side == "right"
    assert r.diagram4.inner_vertex_side == "left"


def test_v055_corner_q0_multiplicities_match_two_parameter_families():
    from qedcalc.operations.corner import corner_raw_pair_audit
    r=corner_raw_pair_audit()
    assert r.diagram5.q0_denominator_powers == (2,1,1,1,1)
    assert r.diagram4.q0_denominator_powers == (1,1,2,1,1)


def test_v055_corner_inner_vertex_is_common_l_loop():
    from qedcalc.operations.corner import corner_raw_pair_audit
    r=corner_raw_pair_audit()
    assert r.common_inner_loop == 'l'
    assert r.diagram5.inner_external_electrons == ('p-k','p')
    assert r.diagram4.inner_external_electrons == ("p'-k","p'")


def test_v055_corner_common_q0_parametric_family_matches_detailed_derivation():
    from qedcalc.operations.corner import corner_q0_parametric_family
    x,y,z,u,v,rho,t=sp.symbols('x y z u v rho t')
    f=corner_q0_parametric_family(x,y,z,u,v,rho,t)
    a=x+y+u; b=y+z+v; c=y; r=x+y; s=y+z
    assert sp.expand(f.Delta-(a*b-c**2)) == 0
    assert sp.expand(f.W-(b*r**2-2*c*r*s+a*s**2)) == 0
    assert sp.expand(f.Omega-(f.W+rho**2*(u+v)*f.Delta)) == 0
    assert f.multiplicity5 == 120*x
    assert f.multiplicity4 == 120*z


def test_v055_corner_split_parameter_q_derivatives_match_two_diagrams():
    from qedcalc.operations.corner import corner_q0_parametric_family
    x,y,z,u,v,rho,t=sp.symbols('x y z u v rho t')
    f=corner_q0_parametric_family(x,y,z,u,v,rho,t)
    assert f.qderivative5_k == x*t and f.qderivative5_l == 0
    assert f.qderivative4_k == x+y and f.qderivative4_l == y+z*t


def test_v055_corner_raw_projector_generates_both_diagrams_and_three_vs_one_q_insertions():
    from qedcalc.operations.corner import corner_raw_projector_polynomials
    r=corner_raw_projector_polynomials()
    assert r.diagram4_base != 0 and r.diagram5_base != 0
    assert r.diagram4_transverse_zero != 0 and r.diagram5_transverse_zero != 0
    assert len(r.term_counts)==2


def test_v056_corner_streaming_gaussian_bridge_generates_real_bare_templates():
    from qedcalc.operations.corner import corner_gaussian_bare_templates
    r=corner_gaussian_bare_templates()
    assert r.G4 != 0 and r.G5 != 0
    assert not r.G4.has(sp.I)
    assert not r.G5.has(sp.I)


def test_v056_corner_generated_bare_uv_residue_factorizes_for_diagram5():
    from qedcalc.operations.corner import corner_uv_residue_sample
    X=sp.Rational(2,5); Y=sp.Rational(1,4); Z=sp.Rational(1,3); rho=sp.Rational(1,7)
    got=corner_uv_residue_sample(5,X,Y,Z,rho)
    expected=sp.Rational(1,2)*X**2*(1-X)/(X**2+rho**2*(1-X))
    assert sp.simplify(got-expected) == 0


def test_v056_corner_generated_bare_uv_residue_factorizes_for_diagram4():
    from qedcalc.operations.corner import corner_uv_residue_sample
    X=sp.Rational(2,5); Y=sp.Rational(1,4); Z=sp.Rational(1,3); rho=sp.Rational(1,7)
    got=corner_uv_residue_sample(4,X,Y,Z,rho)
    expected=sp.Rational(1,2)*X**2*(1-X)/(X**2+rho**2*(1-X))
    assert sp.simplify(got-expected) == 0


def test_v056_corner_local_Bgamma_subtractions_match_both_uv_residues():
    from qedcalc.operations.corner import corner_local_uv_residue_sample
    X=sp.Rational(3,7); Y=sp.Rational(1,5); Z=sp.Rational(1,4); rho=sp.Rational(2,11)
    expected=sp.Rational(1,2)*X**2*(1-X)/(X**2+rho**2*(1-X))
    assert sp.simplify(corner_local_uv_residue_sample(5,X,Y,Z,rho)-expected) == 0
    assert sp.simplify(corner_local_uv_residue_sample(4,X,Y,Z,rho)-expected) == 0


def test_v056_corner_local_subtraction_removes_logarithmic_uv_residue():
    from qedcalc.operations.corner import corner_uv_subtracted_residue_sample
    X=sp.Rational(4,9); Y=sp.Rational(1,6); Z=sp.Rational(1,5); rho=sp.Rational(1,8)
    assert corner_uv_subtracted_residue_sample(5,X,Y,Z,rho) == 0
    assert corner_uv_subtracted_residue_sample(4,X,Y,Z,rho) == 0


def test_v057_corner_inner_vertex_z_sector_closes_to_log_exactly():
    from qedcalc.operations.corner import corner_inner_vertex_z_integral_residual
    L0,Lp=sp.symbols('L0 Lp', positive=True)
    assert corner_inner_vertex_z_integral_residual(L0,Lp) == 0


def test_v057_corner_inner_vertex_kappa_sector_is_simple_denominator_difference():
    from qedcalc.operations.corner import corner_inner_vertex_kappa_difference_residual
    L0,Lp=sp.symbols('L0 Lp', positive=True)
    assert corner_inner_vertex_kappa_difference_residual(L0,Lp) == 0


def test_v057_corner_inner_vertex_gamma_sectors_vanish_at_onshell_subtraction_point():
    from qedcalc.operations.corner import corner_inner_vertex_sector_scalar_coefficients
    u,k2,L0=sp.symbols('u k2 L0', positive=True)
    c=corner_inner_vertex_sector_scalar_coefficients(u,k2,L0,L0)
    assert sp.simplify(c['z_log']) == 0
    assert sp.simplify(c['kappa_difference']) == 0
    assert sp.simplify(c['gamma_total']) == 0


def test_v057_corner_inner_vertex_keeps_corrected_kappa_squared_not_outer_k_squared():
    from qedcalc.operations.corner import corner_inner_vertex_sector_scalar_coefficients
    u,kappa2,L0,Lp=sp.symbols('u kappa2 L0 Lp', positive=True)
    c=corner_inner_vertex_sector_scalar_coefficients(u,kappa2,L0,Lp)
    outer_k2=sp.Symbol('k2_outer')
    assert kappa2 in c['kappa_difference'].free_symbols
    assert outer_k2 not in c['kappa_difference'].free_symbols


def test_v057_corner_inner_vertex_three_sector_object_is_nontrivial():
    from qedcalc.operations.corner import corner_renormalized_inner_vertex_sectors
    r=corner_renormalized_inner_vertex_sectors()
    assert r.K_sector != 0
    assert r.z_sector_closed != 0
    assert r.kappa_sector != 0
    assert r.gamma_sector_closed != 0

# v0.58 outer Lambda-prime / square-completion bridge

def test_v058_lambda_prime_bulk_coefficients_are_generated_from_eq32_structure():
    import sympy as sp
    from qedcalc.operations.corner import corner_lambda_prime_bulk_coefficients
    u,v=sp.symbols('u v')
    c=corner_lambda_prime_bulk_coefficients(u,v)
    assert sp.simplify(c['k2']-u*v*(1-u*v)) == 0
    assert sp.simplify(c['pk']-u*v*(1-u)) == 0
    assert c['constant'] == u**2


def test_v058_outer_bulk_H_and_Q_are_generated_exactly():
    import sympy as sp
    from qedcalc.operations.corner import corner_outer_quadratic_checkpoint_residuals
    u,v,ad,al,z=sp.symbols('u v a_d a_l z')
    r=corner_outer_quadratic_checkpoint_residuals(u,v,ad,al,z)
    assert r['H'] == 0
    assert r['Q'] == 0
    assert r['Q_completed_square'] == 0


def test_v058_outer_z_H_and_Q_are_generated_exactly():
    import sympy as sp
    from qedcalc.operations.corner import corner_outer_quadratic_checkpoint_residuals
    u,v,ad,al,z=sp.symbols('u v a_d a_l z')
    r=corner_outer_quadratic_checkpoint_residuals(u,v,ad,al,z)
    assert r['H_z'] == 0
    assert r['Q_z'] == 0
    assert r['Q_z_completed_square'] == 0


def test_v058_z_one_reduces_to_bulk_quadratic_form():
    import sympy as sp
    from qedcalc.operations.corner import corner_outer_quadratic_bridge
    u,v,ad,al=sp.symbols('u v a_d a_l')
    b=corner_outer_quadratic_bridge(u,v,ad,al,sp.Integer(1))
    assert sp.simplify(b.H_z-b.H) == 0
    assert sp.simplify(b.shift_B_z-b.shift_B) == 0
    assert sp.simplify(b.Q_z-b.Q) == 0


def test_v058_z_zero_removes_offshell_inner_momentum_dependence():
    import sympy as sp
    from qedcalc.operations.corner import corner_outer_quadratic_bridge
    u,v,ad,al=sp.symbols('u v a_d a_l')
    b=corner_outer_quadratic_bridge(u,v,ad,al,sp.Integer(0))
    assert sp.simplify(b.H_z-(1-al)) == 0
    assert sp.simplify(b.shift_B_z-ad) == 0


def test_v058_combined_denominator_coefficients_reproduce_H_and_B():
    import sympy as sp
    from qedcalc.operations.corner import corner_outer_combined_bulk_denominator, corner_outer_quadratic_bridge
    u,v,ad,al,k2,pk=sp.symbols('u v a_d a_l k2 pk')
    raw=corner_outer_combined_bulk_denominator(u,v,ad,al,k2,pk)
    b=corner_outer_quadratic_bridge(u,v,ad,al,sp.Symbol('z'))
    assert sp.simplify(sp.diff(raw,k2)-b.H) == 0
    assert sp.simplify(sp.diff(raw,pk)+2*b.shift_B) == 0
    assert sp.simplify(raw.subs({k2:0,pk:0})-al*u**2) == 0

# v0.59 raw one-loop inner-vertex finite-remainder bridge

def test_v059_raw_inner_vertex_radial_uv_coefficient_is_pure_gamma():
    from qedcalc.operations.corner import corner_raw_inner_vertex_radial_residuals
    for M in corner_raw_inner_vertex_radial_residuals():
        assert all(sp.simplify(x)==0 for x in M)


def test_v059_raw_inner_vertex_complete_on_shell_difference_vanishes_at_k0():
    from qedcalc.operations.corner import corner_raw_inner_vertex_on_shell_residuals
    for M in corner_raw_inner_vertex_on_shell_residuals():
        assert all(sp.simplify(x)==0 for x in M)


def test_v059_raw_inner_vertex_universal_log_coefficient_is_gamma_nu():
    from qedcalc.operations.corner import corner_raw_inner_vertex_log_coeff_residuals
    for M in corner_raw_inner_vertex_log_coeff_residuals():
        assert all(sp.simplify(x)==0 for x in M)


def test_v059_raw_inner_vertex_lambda_prime_matches_v058_bulk_expression():
    from qedcalc.operations.corner import corner_raw_inner_vertex_finite_bridge, corner_lambda_prime_bulk_expression
    b=corner_raw_inner_vertex_finite_bridge()
    k0,k1,k2,k3=b.k
    mink_k2=k0**2-k1**2-k2**2-k3**2
    ref=corner_lambda_prime_bulk_expression(b.u,b.v,mink_k2,k0)+b.rho**2*(1-b.u)
    assert sp.simplify(b.lambda_prime_sq-ref)==0


def test_v059_raw_inner_shift_coefficients_are_generated_from_x_uv_y_u1v():
    from qedcalc.operations.corner import corner_raw_inner_shift_coefficients
    u,v=sp.symbols('u v')
    c=corner_raw_inner_shift_coefficients()
    assert sp.simplify(c['left_p']-(1-u))==0
    assert sp.simplify(c['left_k']+(1-u*v))==0
    assert sp.simplify(c['right_p']-(1-u))==0
    assert sp.simplify(c['right_k']-u*v)==0

# v0.60 finite inner remainder -> outer projector streams

def test_v060_outer_projector_stream_term_counts_are_small_and_stable():
    from qedcalc.operations.corner import corner_outer_projector_streams
    s=corner_outer_projector_streams()
    assert s.term_counts == (('log',4,2),('lambda_prime',21,15),('lambda0',6,2))


def test_v060_outer_projector_streams_are_scalar_polynomials():
    from qedcalc.operations.corner import corner_outer_projector_streams
    s=corner_outer_projector_streams()
    for p in (s.log_base,s.log_transverse,s.lp_base,s.lp_transverse,s.l0_base,s.l0_transverse):
        sp.Poly(p,*s.k)


def test_v060_outer_stream_denominators_regenerate_v058_bulk_forms():
    from qedcalc.operations.corner import corner_outer_stream_denominator_residuals
    u,v,ad,al,z=sp.symbols('u v a_d a_l z')
    r=corner_outer_stream_denominator_residuals(u,v,ad,al,z)
    assert all(sp.simplify(x)==0 for x in r.values())


def test_v060_lambda0_stream_has_only_outer_photon_electron_quadratic():
    from qedcalc.operations.corner import corner_outer_stream_denominators
    u,v,rho,ad,al,z=sp.symbols('u v rho a_d a_l z')
    d=corner_outer_stream_denominators(u,v,rho,ad,al,z)
    assert sp.simplify(d.Q_0-(ad**2+(1-ad)*rho**2))==0
    assert not d.Q_0.has(al)
    assert not d.Q_0.has(v)


def test_v060_log_stream_delta_is_exact_lambda_prime_minus_lambda0():
    from qedcalc.operations.corner import corner_outer_stream_denominators, corner_raw_inner_vertex_finite_bridge
    d=corner_outer_stream_denominators()
    b=corner_raw_inner_vertex_finite_bridge()
    k0,k1,k2,k3=b.k
    kk=k0**2-k1**2-k2**2-k3**2
    actual=sp.expand(b.lambda_prime_sq-b.lambda0_sq)
    A=sp.expand(b.u*b.v*(1-b.u*b.v))
    C=sp.expand(b.u*b.v*(1-b.u))
    assert sp.simplify(actual-(A*kk-2*C*k0))==0

# v0.61 physical on-shell B*gamma subtraction and common-quotient Gaussian bridge

def test_v061_physical_inner_temporal_on_shell_subtraction_vanishes():
    from qedcalc.operations.corner import corner_physical_inner_vertex_bridge
    assert sp.simplify(corner_physical_inner_vertex_bridge().temporal_on_shell_residual)==0


def test_v061_physical_outer_common_quotients_have_only_transverse_odd_remainders():
    from qedcalc.operations.corner import corner_physical_common_quotients
    q=corner_physical_common_quotients()
    assert q.counts == (('log',4,2),('lp',21,5),('B',4,2))
    assert q.odd_flags == (True,True,True)


def test_v061_log_delta_decomposition_uses_correct_K_and_D_coefficients():
    from qedcalc.operations.corner import corner_log_delta_decomposition
    u,v,K,D=sp.symbols('u v K D')
    d=corner_log_delta_decomposition(u,v,K,D)
    assert sp.expand(d['K_coefficient']-u**2*v*(1-v))==0
    assert sp.expand(d['D_coefficient']-u*v*(1-u))==0
    assert sp.expand(d['expression']-(u**2*v*(1-v)*K+u*v*(1-u)*D))==0


def test_v061_compact_physical_gaussian_templates_are_pole_free():
    from qedcalc.operations.corner import corner_physical_gaussian_templates
    g=corner_physical_gaussian_templates()
    assert g.lp_poles == ()
    assert g.b_poles == ()
    assert g.log_poles == ()
    assert sp.count_ops(g.lp_template) < 200
    assert sp.count_ops(g.b_template) < 50
    assert sp.count_ops(g.log_n3_template) < 20


def test_v061_physical_parameter_kernels_build_without_archived_I_sector_inputs():
    from qedcalc.operations.corner import corner_physical_parameter_kernels
    p=corner_physical_parameter_kernels()
    for expr in (p.lp,p.B_gamma,p.log_photon_cancel,p.log_electron_cancel):
        assert expr != 0
        assert not any(s.name.startswith('CORNER_GAMMA') for s in expr.free_symbols)

# v0.62 D-dimensional inner-radial evanescent audit

def test_v062_dimensional_radial_gamma_coefficient_has_expected_epsilon_term():
    from qedcalc.operations.corner import corner_dimensional_radial_audit
    r=corner_dimensional_radial_audit()
    eps=r.epsilon
    assert sp.limit(r.gamma_coefficient_D,eps,0,dir='+') == 1
    assert sp.expand(sp.series(r.gamma_coefficient_D,eps,0,2).removeO()).coeff(eps) == -sp.Rational(3,2)


def test_v062_dimensional_radial_evanescent_finite_shift_is_generated_not_hardcoded():
    from qedcalc.operations.corner import corner_dimensional_radial_audit
    r=corner_dimensional_radial_audit()
    assert sp.simplify(r.evanescent_finite_shift + sp.Rational(3,2)) == 0

# v0.63 evanescent local-term OS-cancellation bridge

def test_v063_evanescent_local_shift_is_same_in_bare_and_B_channel():
    from qedcalc.operations.corner import corner_evanescent_renormalization_bridge
    r=corner_evanescent_renormalization_bridge()
    assert r.local_shift == -sp.Rational(3,2)
    assert sp.simplify(r.bare_local_coeff-r.B_local_coeff) == 0
    assert r.renormalized_local_coeff == 0


def test_v063_evanescent_local_shift_cancels_before_outer_integration():
    from qedcalc.operations.corner import corner_evanescent_renormalization_bridge
    r=corner_evanescent_renormalization_bridge()
    assert sp.simplify(r.renormalized_base) == 0
    assert sp.simplify(r.renormalized_transverse) == 0


def test_phase45_eq32_operator_identity():
    from qedcalc.operations.corner import corner_eq32_operator_residual_flags
    assert corner_eq32_operator_residual_flags() == (True, True, True, True)


def test_phase45_schwinger_raw_calibration():
    from qedcalc.operations.corner import corner_schwinger_calibration
    c=corner_schwinger_calibration()
    assert sp.simplify(c.raw_ratio + 4) == 0


def test_phase45_schwinger_after_quarter_sign():
    from qedcalc.operations.corner import corner_schwinger_calibration
    c=corner_schwinger_calibration()
    assert sp.simplify(c.after_eq42_quarter_ratio + 1) == 0

# v0.65 inner/outer photon sign ownership

def test_v065_photon_sign_ownership_pair_cancels():
    from qedcalc.operations.corner import corner_photon_sign_ownership_audit
    a=corner_photon_sign_ownership_audit()
    assert a.inner_photon_numerator_sign == -1
    assert a.outer_photon_numerator_sign == -1
    assert a.full_corner_photon_sign == 1


def test_v065_outer_only_schwinger_calibration_closes_without_flipping_full_corner():
    from qedcalc.operations.corner import corner_photon_sign_ownership_audit
    a=corner_photon_sign_ownership_audit()
    assert sp.simplify(a.outer_only_schwinger_raw_ratio-4) == 0
    assert sp.simplify(a.outer_only_schwinger_after_quarter_ratio-1) == 0
    assert a.one_sign_only_full_kernel_ratio == -1

# v0.66 exact log-family denominator cancellation

def test_v066_log_denominator_cancellation_identity_is_exact():
    from qedcalc.operations.corner import corner_log_denominator_cancellation_audit
    a=corner_log_denominator_cancellation_audit()
    assert a.residual == 0


def test_v066_log_mass_residual_family_is_present_and_pole_free():
    from qedcalc.operations.corner import corner_physical_parameter_kernels, corner_physical_gaussian_templates
    p=corner_physical_parameter_kernels(); g=corner_physical_gaussian_templates()
    assert p.log_photon_mass_residual != 0
    rho=next(s for s in p.symbols_log_photon_mass if s.name=='rho')
    num,den=sp.fraction(sp.cancel(p.log_photon_mass_residual))
    assert sp.Poly(num,rho).as_dict() and min(k[0] for k in sp.Poly(num,rho).as_dict()) >= 2
    assert g.log_n4_poles == ()


def test_v066_log_cancelled_families_have_minkowski_minus_signs():
    from qedcalc.operations.corner import corner_phase47_log_family_audit
    a=corner_phase47_log_family_audit()
    assert a['photon_cancel_sign'] == -1
    assert a['electron_cancel_sign'] == -1
    assert a['scalar_identity_residual'] == 0

# v0.66 Phase 48 sequential-family normalization / LP-definition audit

def test_v066_phase48_mirror_factor_is_already_in_eq42_normalization():
    from qedcalc.operations.corner import corner_sequential_family_audit
    a=corner_sequential_family_audit()
    assert a.one_side_alpha2_prefactor == sp.Rational(1,8)
    assert a.mirror_pair_alpha2_prefactor == sp.Rational(1,4)
    assert a.eq42_quarter_normalization == sp.Rational(1,4)


def test_v066_phase48_B_gamma_factorizes_to_schwinger_kernel():
    from qedcalc.operations.corner import corner_sequential_family_audit
    a=corner_sequential_family_audit()
    assert sp.simplify(a.b_gamma_schwinger_ratio_raw-4) == 0
    assert sp.simplify(a.b_gamma_schwinger_ratio_physical-1) == 0


def test_v066_phase48_lp_sign_change_is_exposed_and_n3_reinterpretation_is_forbidden():
    from qedcalc.operations.corner import corner_sequential_family_audit
    a=corner_sequential_family_audit()
    assert a.raw_radial_C_sign == -1
    assert a.physical_bridge_C_sign == 1
    assert a.lp_n3_poles
    assert any(sp.simplify(coeff) != 0 for _,coeff in a.lp_n3_pole_coefficients)


def test_historical_K_projector_regenerates_DQ_plus_k1k2_odd_remainder():
    from qedcalc.operations.corner import corner_historical_K_projector_audit
    a=corner_historical_K_projector_audit()
    assert sp.expand(a.common_numerator-a.D*a.Q_K-a.odd_remainder) == 0
    assert a.odd_flag
    assert a.has_k1k2_factor
    assert sp.simplify(a.odd_remainder.subs(a.k[1],0)) == 0
    assert sp.simplify(a.odd_remainder.subs(a.k[2],0)) == 0


def test_historical_K_projector_is_independent_of_current_C_based_lp_object():
    from qedcalc.operations.corner import corner_historical_K_projector_audit, corner_physical_common_quotients
    h=corner_historical_K_projector_audit(); c=corner_physical_common_quotients()
    # Independent namespaces are intentional: historical Q_K is regenerated
    # from the stored K_nu operator, not aliased to the C_nu-derived LP quotient.
    assert h.Q_K is not c.lp_quotient
    assert tuple(x.name for x in h.k) != tuple(x.name for x in c.k)


def test_phase50_resolved_K_convention_matches_current_raw_C_projector():
    from qedcalc.operations.corner import corner_K_convention_resolved_audit
    a=corner_K_convention_resolved_audit()
    assert a.basis_coefficients == (-1,1,0,-1,sp.I,1,-sp.Rational(1,2))
    assert a.null_base == 0
    assert a.null_transverse == 0
    assert a.base_residual == 0
    assert a.transverse_residual == 0
    assert a.common_residual == 0


def test_phase50_resolved_K_remainder_is_exact_transverse_odd():
    from qedcalc.operations.corner import corner_K_convention_resolved_audit
    a=corner_K_convention_resolved_audit()
    assert a.mapped_odd_flag
    assert a.mapped_has_k1k2_factor


def test_phase51_rational_regrouping_is_exact_before_and_after_gaussian_map():
    from qedcalc.operations.corner import corner_rational_regrouping_audit
    a=corner_rational_regrouping_audit()
    assert a.quotient_residual == 0
    assert a.remainder_residual == 0
    assert a.lp_template_residual == 0
    assert a.b_l0_template_residual == 0
    assert all(x == 0 for x in a.identity_residuals)


def test_phase52_direct_unsplit_log_kernel_is_pole_free_and_scalar_split_exact():
    from qedcalc.operations.corner import corner_log_unsplit_audit
    a=corner_log_unsplit_audit()
    assert a.direct_poles == ()
    assert a.scalar_split_residual == 0
    assert a.direct_parameter_kernel != 0


def test_phase52_direct_unsplit_log_delta_coefficients_are_generated_correctly():
    from qedcalc.operations.corner import corner_log_unsplit_audit
    a=corner_log_unsplit_audit(); u,v,_,_,_,_=a.symbols
    AK,AD=a.delta_coefficients
    assert sp.expand(AK-u**2*v*(1-v)) == 0
    assert sp.expand(AD-u*v*(1-u)) == 0


def test_phase53_soft_importance_maps_cover_endpoints_and_simplex_exactly():
    from qedcalc.operations.corner import corner_soft_importance_audit, corner_phase53_soft_importance_audit
    a=corner_soft_importance_audit(); d=corner_phase53_soft_importance_audit()
    assert a.simplex_sum_residual == 0
    assert a.line_sum_residual == 0
    assert d["u_at_t0"] == 0
    assert d["u_at_t1"] == 1


def test_phase53_soft_importance_jacobians_are_nonzero_symbolic_maps():
    from qedcalc.operations.corner import corner_soft_importance_audit
    a=corner_soft_importance_audit()
    assert a.du_dt != 0
    assert a.simplex_jacobian != 0
    assert a.line_jacobian != 0


def test_phase54_B_finite_normalization_is_independently_11_over_4():
    from qedcalc.operations.corner import corner_B_finite_normalization_audit
    a=corner_B_finite_normalization_audit()
    assert a.division_residual == 0
    assert a.hard_log_limit == sp.Rational(1,2)
    assert a.rational_constant == -sp.Rational(5,4)
    assert a.B_finite_constant == sp.Rational(11,4)


def test_phase54_counterterm_local_finite_constant_is_minus_11_over_8():
    from qedcalc.operations.corner import corner_B_finite_normalization_audit
    a=corner_B_finite_normalization_audit()
    assert a.schwinger_limit == sp.Rational(1,2)
    assert a.counterterm_finite_constant == -sp.Rational(11,8)


def test_phase55_local_B_finite_pieces_cancel_before_outer_loop():
    from qedcalc.operations.corner import corner_local_finite_ownership_audit
    a=corner_local_finite_ownership_audit()
    assert a.log_residual == 0
    assert a.radial_constant_residual == 0
    assert a.rational_residual == 0
    assert a.renormalized_local_finite_coeff == 0
    assert a.current_temporal_on_shell_residual == 0


def test_phase55_minus_11_over_8_is_owned_and_not_an_extra_remainder_term():
    from qedcalc.operations.corner import corner_local_finite_ownership_audit
    a=corner_local_finite_ownership_audit()
    assert a.counterterm_finite_constant == -sp.Rational(11,8)
    assert a.bare_matching_finite_constant == sp.Rational(11,8)
    assert a.net_local_finite_constant == 0
    assert a.outer_base_residual == 0
    assert a.outer_transverse_residual == 0


def test_phase56_sequential_prefactor_rederives_eq42_quarter_exactly():
    from qedcalc.operations.corner import corner_sequential_normalization_ownership_audit
    a=corner_sequential_normalization_ownership_audit()
    assert a.one_side_prefactor == a.alpha**2/(8*sp.pi**4)
    assert a.mirror_pair_prefactor == a.alpha**2/(4*sp.pi**4)
    assert a.prefactor_residual == 0
    assert a.physical_quarter == sp.Rational(1,4)
    assert a.physical_quarter_residual == 0


def test_phase56_photon_signs_and_u_measure_ownership_are_explicit():
    from qedcalc.operations.corner import corner_sequential_normalization_ownership_audit
    a=corner_sequential_normalization_ownership_audit()
    assert a.inner_photon_sign == -1
    assert a.outer_photon_sign == -1
    assert a.full_photon_sign == 1
    assert all(measure.startswith('u du') for _,measure in a.measures)


def test_phase57_large_r_overlap_coefficient_and_subtraction_are_exact():
    from qedcalc.operations.corner import corner_large_r_overlap_audit
    a=corner_large_r_overlap_audit()
    assert a.large_r_residual == 0
    assert a.subtracted_one_over_r_residual == 0
    assert sp.simplify(a.overlap_coefficient-8*a.v/(1-a.a_l)**2) == 0


def test_phase58_simplex_cutoff_owns_the_overlap_log_exactly():
    from qedcalc.operations.corner import corner_large_r_cutoff_audit
    a=corner_large_r_cutoff_audit()
    assert a.r_max == (1-a.a_l)/a.u
    assert a.log_coefficient_residual == 0
    assert sp.simplify(a.log_coefficient-8*a.v/(1-a.a_l)**2) == 0


def test_phase59_overlap_add_subtract_is_exact_on_same_simplex_cutoff():
    from qedcalc.operations.corner import corner_overlap_add_subtract_audit
    a=corner_overlap_add_subtract_audit()
    assert a.pointwise_recombination_residual == 0
    assert a.cutoff_addback_residual == 0
    assert a.subtracted_one_over_r_residual == 0
    assert a.da_d_dr == a.u
    assert sp.expand(a.a_p-(1-a.a_l-a.u*a.r)) == 0


def test_phase60_joint_soft_density_is_normalized_exactly():
    from qedcalc.operations.corner import corner_joint_soft_density_audit
    a=corner_joint_soft_density_audit()
    assert a.S_integral_residual == 0
    assert a.R_integral == 1
    assert a.normalization_residual == 0


def test_phase61_joint_soft_triangle_exact_ownership():
    from qedcalc.operations.corner import corner_joint_soft_triangle_audit
    a = corner_joint_soft_triangle_audit()
    assert a.endpoint_derivative_residual == 0
    assert a.zero_cutoff_residual == 0
    assert a.infinite_cutoff_residual == 0
    assert sp.simplify(a.tail_log_coefficient - 2*a.v) == 0
    assert sp.simplify(a.tail_constant - a.v*(1-2*sp.log(a.v))) == 0
    assert sp.simplify(a.physical_tail_scaled_limit - 2*a.U*a.v) == 0


def test_phase62_eq28_shift_ownership_is_exact():
    from qedcalc.operations.corner import corner_eq28_shift_ownership_audit
    a = corner_eq28_shift_ownership_audit()
    assert a.difference_residual == 0
    assert sp.simplify(a.coefficient_difference - (a.v-a.u)) == 0
    assert a.hard_ownership_residual == 0


def test_phase63_pure_matching_constant_is_exactly_zero():
    from qedcalc.operations.corner import corner_pure_matching_audit, corner_finite_result
    a=corner_pure_matching_audit()
    assert a.analytic_matching_constant == 0
    assert sp.simplify(a.analytic_finite-corner_finite_result()) == 0


def test_phase63_archived_finite_rho_checkpoint_is_regression_only_and_converges():
    from qedcalc.operations.corner import corner_pure_matching_audit
    a=corner_pure_matching_audit()
    assert a.last_within_uncertainty
    assert abs(float(a.last_checkpoint_residual)) <= float(a.last_checkpoint_uncertainty)
    # It approaches the analytic zero-matching condition much more closely at
    # rho=.002 than at the first checkpoint rho=.1.
    assert abs(float(a.checkpoint_residuals[-1])) < abs(float(a.checkpoint_residuals[0]))


def test_phase64_finite_rho_numerical_measure_ownership_is_exact():
    from qedcalc.operations.corner import corner_finite_rho_numerical_measure_audit
    a=corner_finite_rho_numerical_measure_audit()
    assert a.normalization == sp.Rational(1,4)
    assert sp.factor(a.simplex_a_d+a.simplex_a_p+a.simplex_a_l-1) == 0
    assert sp.factor(a.line_a_d+a.line_a_l-1) == 0
    assert sp.simplify(a.physical_u_measure-a.u*a.du_dt) == 0
    assert sp.simplify(a.simplex_physical_measure-a.u*a.du_dt*a.simplex_jacobian) == 0
    assert sp.simplify(a.line_physical_measure-a.u*a.du_dt*a.line_jacobian) == 0
    assert dict(a.family_dimensions) == {
        'lp':4,'B_gamma':2,'log_photon_cancel':4,
        'log_electron_cancel':5,'log_photon_mass_residual':5,
    }


def test_phase68_historical_K_sector_decomposition():
    from qedcalc.operations.corner import corner_phase68_historical_K_sector_decomposition_audit
    a=corner_phase68_historical_K_sector_decomposition_audit()
    assert a['full_base_residual'] == 0
    assert a['full_transverse_residual'] == 0
    assert a['full_common_residual'] == 0
    assert a['D_base_divisible_by_D'] and a['D_transverse_divisible_by_D']
    assert a['k2_base_divisible_by_k2'] and a['k2_transverse_divisible_by_k2']


def test_phase69_cancellation_first_families():
    from qedcalc.operations.corner import corner_phase69_K_cancellation_first_family_audit
    a=corner_phase69_K_cancellation_first_family_audit()
    assert a['odd_flags'] == (True, True, True)
    assert a['family_powers_K_D_Lp_and_total_n'] == (
        ('preserving',(1,2,1),4),
        ('D_cancel',(1,1,1),3),
        ('k2_cancel',(0,2,1),3),
    )


def test_phase70_cancellation_first_rational_kernels_are_pole_free():
    from qedcalc.operations.corner import corner_phase70_cancellation_first_rational_kernel_audit
    a=corner_phase70_cancellation_first_rational_kernel_audit()
    assert a['all_kernels_pole_free'] is True
    assert a['D_cancel_ops'] > 0
    assert a['k2_cancel_ops'] > 0


def test_phase71_cancellation_first_overlap_measure_is_exact():
    from qedcalc.operations.corner import corner_phase71_cancellation_first_overlap_measure_audit
    a=corner_phase71_cancellation_first_overlap_measure_audit()
    assert a['triangle_ad_jacobian_residual'] == 0
    assert a['triangle_upper_boundary_residual'] == 0
    assert a['line_ad_jacobian_residual'] == 0
    assert a['line_upper_boundary_residual'] == 0


def test_phase71_overlap_qmc_smoke():
    import pytest
    pytest.importorskip('numpy')
    pytest.importorskip('scipy')
    from qedcalc.operations.corner import corner_cancellation_first_overlap_qmc
    a=corner_cancellation_first_overlap_qmc(0.05,power=5,seed=3,replicates=2)
    assert a['assembled']['replicates'] == 2
    assert a['assembled']['samples_per_sector_per_replicate'] == 32
    for name in ('preserving','D_cancel','k2_cancel','kappa_Lp','kappa_L0'):
        assert a[name]['finite_fraction_min'] > 0.99


def test_phase72_direct_log_unsplit_is_exact_and_checkpoint_not_input():
    from qedcalc.operations.corner import corner_phase72_full_stabilized_audit
    a=corner_phase72_full_stabilized_audit()
    assert a['direct_log_scalar_split_residual'] == 0
    assert not a['direct_log_poles']
    assert a['physical_quarter'] == sp.Rational(1,4)
    assert a['checkpoint_is_input'] is False


def test_phase72_full_stabilized_qmc_smoke():
    import pytest, math
    pytest.importorskip('numpy'); pytest.importorskip('scipy')
    from qedcalc.operations.corner import corner_phase72_full_stabilized_qmc
    a=corner_phase72_full_stabilized_qmc(0.05,power=5,seed=3,replicates=2)
    assert a['status'].startswith('finite and numerically stabilized')
    assert math.isfinite(a['full_finite_estimate'])
    assert math.isfinite(a['checkpoint_residual'])


def test_phase74_k2_mass_residual_is_nonuniform_in_soft_region():
    from qedcalc.operations.corner import corner_phase74_k2_mass_residual_nonuniform_audit
    a=corner_phase74_k2_mass_residual_nonuniform_audit()
    assert a['fixed_k_rho0_limit'] == 0
    assert a['soft_scaled_rho0_limit'] != 0
    assert a['limit_noncommutation'] != 0
    assert a['can_discard_before_integration'] is False



def test_phase75_retained_photon_reconstruction_and_corrected_cancel_signs():
    from qedcalc.operations.corner import (
        corner_phase73_finite_rho_cancellation_wick_audit,
        corner_phase75_retained_photon_residual_audit,
    )
    a=corner_phase73_finite_rho_cancellation_wick_audit()
    b=corner_phase75_retained_photon_residual_audit()
    assert a['electron_scalar_cancellation_residual'] == 0
    assert a['photon_scalar_cancellation_residual'] == 0
    assert a['D_cancel_euclidean_coefficient'] == -1
    assert a['k2_cancel_euclidean_coefficient'] == sp.Rational(1,2)
    assert a['k2_mass_residual_euclidean_coefficient'] == -sp.Rational(1,2)
    assert b['scalar_residual_identity'] == 0
    assert b['uses_phase69_k2_quotient'] is True
    assert b['checkpoint_used'] is False


def test_phase75_route_closure_qmc_smoke():
    import pytest, math
    pytest.importorskip('numpy'); pytest.importorskip('scipy')
    from qedcalc.operations.corner import corner_phase75_route_closure_qmc
    a=corner_phase75_route_closure_qmc(0.05,power=6,seed=31,replicates=2)
    assert math.isfinite(a['phase64_generated_physical_rational'])
    assert math.isfinite(a['phase71_plus_residual'])
    assert math.isfinite(a['gap_after_residual'])
    assert a['checkpoint_used'] is False
