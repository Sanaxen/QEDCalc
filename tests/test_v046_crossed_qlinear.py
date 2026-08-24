from pathlib import Path
import sympy as sp
from qedcalc.parser.qed_latex import parse_loop_integral_latex
from qedcalc.operations.crossed_ladder import (
    analyze_raw_crossed_ladder,
    crossed_raw_numerator_q_expansion,
    crossed_q0_parametric_bridge_checks,
    crossed_denominator_q1_correction,
    crossed_breit_projector_check,
)
ROOT=Path(__file__).resolve().parents[1]

def _raw():
    return analyze_raw_crossed_ladder(parse_loop_integral_latex((ROOT/'input'/'crossed_ladder_2loop_bare.tex').read_text(encoding='utf-8')))

def test_crossed_q_expansion_matches_independent_chain_count():
    s=crossed_raw_numerator_q_expansion(_raw())
    assert (s.q0_terms,s.q1_terms,s.total_terms)==(144,84,228)

def test_crossed_q0_symanzik_matches_delta_w_and_measure():
    c=crossed_q0_parametric_bridge_checks()
    assert c['Delta_difference']==0
    assert c['W_difference']==0
    assert c['measure_difference']==0

def test_crossed_denominator_q1_correction():
    x,y=sp.symbols('x y')
    kq=sp.Symbol('SP__k__q'); lq=sp.Symbol('SP__l__q')
    assert sp.expand(crossed_denominator_q1_correction(x,y)-(2*x*kq+y*(kq+lq)))==0

def test_crossed_breit_projector_normalization():
    c=crossed_breit_projector_check()
    assert c.F1_coefficient==0
    assert c.F2_coefficient==1
