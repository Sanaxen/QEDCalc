from pathlib import Path
from qedcalc import parse_latex, render_latex
from qedcalc.config import load_symbol_table
from qedcalc.core.expression import Fraction
from qedcalc.operations.propagator import recognize_propagators, scalarize_fermion_propagators, separate_numerator_denominator
from qedcalc.operations.lorentz import contract_metric
from qedcalc.operations.algebra import expand_expression
from qedcalc.operations.dirac import contract_gamma
from qedcalc.operations.denominator import expand_denominator, feynman_parameterize
from qedcalc.operations.onshell import apply_scalar_onshell
from qedcalc.operations.simplify import expand_commutative, simplify_expression
from qedcalc.operations.feynman import complete_square, shift_loop_momentum
from qedcalc.operations.loop import shift_loop_momentum_in_numerator, drop_odd_loop_terms, symmetric_rank2

ROOT = Path(__file__).resolve().parents[1]

def _fraction():
    symbols=load_symbol_table(ROOT/'symbols.txt')
    source=(ROOT/'input'/'vertex_1loop_integrand.tex').read_text(encoding='utf-8')
    expr=parse_latex(source,symbol_table=symbols)
    return separate_numerator_denominator(scalarize_fermion_propagators(recognize_propagators(expr)))

def test_metric_contraction_on_vertex_numerator():
    fr=_fraction()
    out=render_latex(contract_metric(fr.numerator))
    assert r'\gamma_{\rho}' in out
    assert r'g_{\rho\sigma}' not in out

def test_denominator_feynman_combination():
    fr=_fraction()
    den=apply_scalar_onshell(expand_denominator(fr.denominator))
    fpi=feynman_parameterize(Fraction(fr.numerator,den))
    combined=render_latex(expand_commutative(fpi.combined_denominator))
    assert r'p\cdot k' in combined
    assert r"p'\cdot k" in combined
    assert r'k\cdot k' in combined

def test_complete_square_and_shift():
    fr=_fraction()
    den=apply_scalar_onshell(expand_denominator(fr.denominator))
    fpi=feynman_parameterize(Fraction(fr.numerator,den))
    combined=expand_commutative(fpi.combined_denominator)
    completed=complete_square(combined)
    text=render_latex(completed)
    assert r'k-\left(' in text
    assert r"x\,p'" in text
    shifted=render_latex(shift_loop_momentum(completed))
    assert r'l\cdot l' in shifted

def test_dirac_outer_contraction_after_expansion():
    fr=_fraction()
    num=contract_metric(fr.numerator)
    num=expand_expression(num)
    num=simplify_expression(contract_gamma(num))
    text=render_latex(num)
    assert r'p_{\mu}' in text
    assert r"p'_{\mu}" in text

def test_loop_shift_and_odd_drop():
    fr=_fraction()
    num=simplify_expression(contract_gamma(expand_expression(contract_metric(fr.numerator))))
    den=apply_scalar_onshell(expand_denominator(fr.denominator))
    fpi=feynman_parameterize(Fraction(num,den))
    completed=complete_square(expand_commutative(fpi.combined_denominator))
    shifted=shift_loop_momentum_in_numerator(num, completed)
    even=drop_odd_loop_terms(shifted)
    assert 'l_{\\mu}' not in render_latex(even) or render_latex(even)
