from pathlib import Path
import sympy as sp

from qedcalc import parse_latex, parse_loop_integral_latex, render_latex, Symbol, Vector, ScalarMul, __version__
from qedcalc.core.expression import CompletedSquare, VectorLinearCombination
from qedcalc.history.markdown_session import MarkdownSession
from qedcalc.config.conventions import load_conventions
from qedcalc.operations.algebra import expand_expression, normalize_noncommutative_products
from qedcalc.operations.dirac import contract_gamma
from qedcalc.operations.loop import shift_loop_momentum_in_numerator, drop_odd_loop_terms
from qedcalc.operations.simplify import expand_commutative, simplify_expression
from qedcalc.operations.bare_diagram import (
    find_self_energy_subdiagrams, contract_self_energy_subdiagram, contract_self_energy_to_outer_loop,
)
from qedcalc.operations.self_energy import (
    self_energy_delta, self_energy_delta0, uv_cancellation_numerator,
    log_ratio_parameter_kernel, log_ratio_prefactor,
    finite_four_parameter_integrand, finite_b_integrated_kernel,
    finite_one_variable_kernel, finite_part_numeric, finite_part_expected,
    finite_part_recognize, ir_part_asymptotic, total_self_energy_coefficient,
)

ROOT=Path(__file__).resolve().parents[1]
raw_right_path=ROOT/'input/self_energy_insertion_right_2loop_bare.tex'
raw_left_path=ROOT/'input/self_energy_insertion_left_2loop_bare.tex'
raw_right=parse_loop_integral_latex(raw_right_path.read_text(encoding='utf-8'))
raw_left=parse_loop_integral_latex(raw_left_path.read_text(encoding='utf-8'))
right_match=find_self_energy_subdiagrams(raw_right)[0]
left_match=find_self_energy_subdiagrams(raw_left)[0]
right_red=contract_self_energy_subdiagram(raw_right)
left_red=contract_self_energy_subdiagram(raw_left)
source_path=ROOT/'input/self_energy_subloop_numerator.tex'
out_path=ROOT/'output/self_energy_insertion_2loop_trial.md'
source=source_path.read_text(encoding='utf-8').strip()
expr=parse_latex(source)
expanded=normalize_noncommutative_products(expand_expression(expr))
reduced=simplify_expression(contract_gamma(expanded))

a_sym=Symbol('a')
completed=CompletedSquare(
    loop=Vector('l'),
    shift=VectorLinearCombination(((a_sym, Vector('r')),)),
    remainder=Symbol('0'),
)
shifted=expand_commutative(shift_loop_momentum_in_numerator(reduced, completed, new_loop='t'))
even=simplify_expression(drop_odd_loop_terms(shifted, loop='t'))

a,z,b,q,r2,m,lam,rslash,rho=sp.symbols('a z b q r2 m lambda rslash rho', positive=True)
delta=self_energy_delta(a,r2,m,lam)
delta0=self_energy_delta0(a,m,lam)
uv=sp.simplify(uv_cancellation_numerator(a,m,rslash))
conventions=load_conventions(ROOT/'conventions.txt')
outer_prefactor=conventions.compact_outer_one_loop_prefactor_latex()
right_compact_bare=contract_self_energy_to_outer_loop(raw_right, conventions=conventions, renormalized=False)
left_compact_bare=contract_self_energy_to_outer_loop(raw_left, conventions=conventions, renormalized=False)
right_compact_ren=contract_self_energy_to_outer_loop(raw_right, conventions=conventions, renormalized=(uv==0))
left_compact_ren=contract_self_energy_to_outer_loop(raw_left, conventions=conventions, renormalized=(uv==0))
logden=log_ratio_parameter_kernel(a,z,r2,m,lam)
logpref=log_ratio_prefactor(a,r2,m)
GA=finite_four_parameter_integrand(a,z,b,q)
B=finite_b_integrated_kernel(a,z,q)
F=finite_one_variable_kernel(a)
num=finite_part_numeric(55)
recognized=finite_part_recognize(num,50)
expected=finite_part_expected()
ir=ir_part_asymptotic(rho)
total=total_self_energy_coefficient(rho)

s=MarkdownSession(out_path,title='QEDCalc two-loop trial: self-energy insertion')
s.text('Version',f'QEDCalc v{__version__}')
s.text('Loaded conventions', conventions.to_markdown())
s.equation('Outer prefactor generated from conventions.txt', outer_prefactor)
s.text('Scope','v0.22 parses each bare two-loop self-energy-insertion RHS as one LoopIntegralExpression, discovers the open one-loop self-energy block from the repeated electron propagator pattern, identifies whether the insertion is left or right of the external photon vertex, and contracts it to S Sigma S. After the existing on-shell UV cancellation check passes, the same topology is rendered with Sigma_R. The internal-photon reduction currently selects the Feynman-gauge metric part; automatic finite on-shell counterterm reconstruction directly from the raw general-gauge expression remains a later step.')
s.equation('Raw right-insertion two-loop RHS',raw_right)
s.text('Right subdiagram detection',f'PASS: side={right_match.side}, subloop={right_match.loop_momentum.name}, external momentum={render_latex(right_match.external_momentum)}')
s.equation('Right self-energy numerator extracted from raw RHS',right_red.reduced_numerator)
s.equation('Right compact bare outer diagram',right_compact_bare)
s.equation('Raw left-insertion two-loop RHS',raw_left)
s.text('Left subdiagram detection',f'PASS: side={left_match.side}, subloop={left_match.loop_momentum.name}, external momentum={render_latex(left_match.external_momentum)}')
s.equation('Left self-energy numerator extracted from raw RHS',left_red.reduced_numerator)
s.equation('Left compact bare outer diagram',left_compact_bare)
s.equation('Self-energy subloop numerator input',expr)
s.equation('After expansion and gamma contraction',reduced)
s.equation('After l = t + a r',shifted)
s.equation('After removing odd t terms',even)
s.equation('Self-energy denominator',sp.latex(delta))
s.equation('On-shell denominator',sp.latex(delta0))
s.equation('UV numerator after on-shell counterterms',sp.latex(uv))
s.text('UV cancellation check','PASS' if uv==0 else 'FAIL')
s.equation('Right compact renormalized outer diagram',right_compact_ren)
s.equation('Left compact renormalized outer diagram',left_compact_ren)
s.equation('Rationalized logarithm prefactor',sp.latex(logpref))
s.equation('Rationalized logarithm denominator',sp.latex(logden))
s.equation('Finite four-parameter integrand G_A',sp.latex(GA))
s.equation('Analytic b-integrated kernel',sp.latex(B))
s.equation('Final one-variable finite kernel',sp.latex(F))
s.text('Finite coefficient numerical value',f'A_A = {num}')
s.equation('Finite coefficient analytic recognition',sp.latex(recognized))
s.equation('Finite coefficient reference',sp.latex(expected))
s.text('Finite-part recognition check','PASS' if sp.simplify(recognized-expected)==0 else 'FAIL')
s.equation('IR part through O(rho^0)',sp.latex(ir))
s.equation('Total self-energy-insertion coefficient',sp.latex(total))
s.equation('Equivalent conventional form',r'A_{\mathrm S}=-\frac12\ln\rho^{-2}+\frac{11}{24}-\frac{\pi^2}{18}')
s.save()

print(f'QEDCalc v{__version__} two-loop self-energy-insertion trial')
print(f'Output: {out_path}')
print(f'UV cancellation: {uv}')
print(f'A_A numeric = {num}')
print(f'A_A recognized = {recognized}')
print(f'A_S = {total}')
