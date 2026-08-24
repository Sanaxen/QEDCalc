from pathlib import Path
import sys

from qedcalc import parse_latex, render_latex, Fraction, __version__
from qedcalc.config import load_symbol_table
from qedcalc.operations.propagator import (
    recognize_propagators, scalarize_fermion_propagators,
    separate_numerator_denominator,
)
from qedcalc.operations.lorentz import contract_metric
from qedcalc.operations.algebra import (
    expand_expression, normalize_noncommutative_products,
)
from qedcalc.operations.dirac import contract_gamma
from qedcalc.operations.denominator import expand_denominator, feynman_parameterize
from qedcalc.operations.onshell import apply_scalar_onshell
from qedcalc.operations.simplify import expand_commutative, simplify_expression
from qedcalc.operations.feynman import complete_square, shift_loop_momentum
from qedcalc.operations.loop import (
    shift_loop_momentum_in_numerator, drop_odd_loop_terms, symmetric_rank2,
)
from qedcalc.operations.spinor import sandwich, reduce_external_dirac_exact
from qedcalc.operations.momentum import introduce_q, take_q_zero
from qedcalc.operations.qexpansion import truncate_q_order, apply_elastic_onshell_q
from qedcalc.operations.current import (
    decompose_q_basis, split_q_basis_into_gordon, project_f2_from_q_basis,
)
from qedcalc.operations.scalar_sympy import simplify_scalar_with_sympy
from qedcalc.operations.integral import (
    extract_delta_from_shifted_denominator,
    triangle_integral_ratio,
    qed_vertex_prefactor_after_n3_loop,
)
from qedcalc.validation.validator import validate_indices
from qedcalc.history.markdown_session import MarkdownSession


def main():
    root = Path(__file__).resolve().parents[1]
    input_path = root / 'input' / 'vertex_1loop_integrand.tex'
    symbols_path = root / 'symbols.txt'

    try:
        symbols = load_symbol_table(symbols_path)
        source = input_path.read_text(encoding='utf-8')
        expr = parse_latex(source, symbol_table=symbols)
        recognized = recognize_propagators(expr)
        scalarized = scalarize_fermion_propagators(recognized)
        separated = separate_numerator_denominator(scalarized)

        metric_num = contract_metric(separated.numerator)
        expanded_num = expand_expression(metric_num)
        dirac_num = simplify_expression(contract_gamma(expanded_num))

        expanded_den = expand_denominator(separated.denominator)
        onshell_den = apply_scalar_onshell(expanded_den)
        fpi = feynman_parameterize(Fraction(dirac_num, onshell_den))
        combined_den = expand_commutative(fpi.combined_denominator)
        completed = complete_square(combined_den)
        shifted_den = shift_loop_momentum(completed, 'l')

        shifted_num = shift_loop_momentum_in_numerator(dirac_num, completed, 'l')
        even_num = simplify_expression(drop_odd_loop_terms(expand_expression(shifted_num), 'l'))
        symmetric_num = simplify_expression(symmetric_rank2(even_num, 'l'))
        normalized_num = normalize_noncommutative_products(symmetric_num)

        # Deterministic on-shell Dirac reduction before introducing q.
        spinor_expr = sandwich(normalized_num)
        dirac_reduced = reduce_external_dirac_exact(spinor_expr)

        # Introduce q = p' - p, apply elastic on-shell scalar identities,
        # and keep terms through first order in q.
        q_current = introduce_q(dirac_reduced)
        q_current = apply_elastic_onshell_q(q_current)
        q_linear = truncate_q_order(q_current, 1)
        q_operator = normalize_noncommutative_products(
            expand_commutative(expand_expression(q_linear.operator))
        )

        basis = decompose_q_basis(q_operator)
        gamma_coeff = simplify_scalar_with_sympy(basis.gamma, 'factor')
        p_coeff = simplify_scalar_with_sympy(basis.p, 'factor')
        q_coeff = simplify_scalar_with_sympy(basis.q, 'factor')
        residual = basis.residual

        gordon_split = split_q_basis_into_gordon(basis)
        pair_coeff = simplify_scalar_with_sympy(gordon_split.pair, 'factor')
        longitudinal_coeff = simplify_scalar_with_sympy(gordon_split.longitudinal_q, 'factor')
        f2_numerator = simplify_scalar_with_sympy(project_f2_from_q_basis(basis), 'factor')

        # q -> 0 denominator and Delta extraction.
        q_den = introduce_q(shifted_den)
        q_den = apply_elastic_onshell_q(q_den)
        q0_den = take_q_zero(q_den)
        delta = extract_delta_from_shifted_denominator(q0_den, 'l')

        parameter_integrand, triangle_value = triangle_integral_ratio(f2_numerator, delta)
        final_f2 = qed_vertex_prefactor_after_n3_loop(triangle_value)

        messages = validate_indices(expr)

    except (ValueError, FileNotFoundError, TypeError, RuntimeError) as exc:
        print('\n[QEDCalc ERROR]')
        print(exc)
        print('\nCheck the input expression and symbols.txt.')
        return 1

    print(f'=== QEDCalc v{__version__} ===')
    print('=== Reduced q-basis coefficients ===')
    print('gamma_mu coefficient :', render_latex(gamma_coeff))
    print('p_mu coefficient     :', render_latex(p_coeff))
    print('q_mu coefficient     :', render_latex(q_coeff))
    print('residual             :', render_latex(residual))
    print('\n=== Gordon split ===')
    print("B for (p' + p)_mu   :", render_latex(pair_coeff))
    print('longitudinal q_mu    :', render_latex(longitudinal_coeff))
    print('\n=== Projected F2 numerator ===')
    print(render_latex(f2_numerator))
    print('\n=== Delta at q = 0 ===')
    print(render_latex(delta))
    print('\n=== Parameter integrand after loop integration ===')
    print(parameter_integrand)
    print('\n=== Triangle parameter integral ===')
    print(triangle_value)
    print('\n=== Final one-loop correction ===')
    print(render_latex(final_f2))

    out = root / 'output' / 'vertex_1loop_session.md'
    s = MarkdownSession(out, 'QED 1-loop vertex correction - calculation session')
    s.text('Version', f'QEDCalc v{__version__}')
    s.text('Symbol definitions', f'`{symbols_path.relative_to(root)}`\n\n{symbols.to_markdown()}')
    s.text('Input file', f'`{input_path.relative_to(root)}`')
    s.equation('Original input', source.strip())
    s.equation('Numerator after symmetric loop reduction', symmetric_num)
    s.step(15, 'Non-commutative normalization', symmetric_num, normalized_num,
           'Move commutative scalar coefficients outside slash/gamma chains so the Dirac ordering is explicit.')
    s.step(16, 'Exact external Dirac reduction', normalized_num, dirac_reduced,
           "Recursively commute /p' left and /p right. Each recursion lowers the distance to an external spinor, then the on-shell Dirac equation is applied.")
    s.step(17, 'Momentum-transfer introduction', dirac_reduced, q_current,
           "Introduce q = p' - p, apply p^2 = p'^2 = m^2, and use p.q = -q^2/2.")
    s.step(18, 'First-order q truncation', q_current, q_linear,
           'Discard terms of explicit order q^2 and higher. The magnetic form factor requires the current through first order in q.')
    s.equation('Gamma_mu coefficient', gamma_coeff)
    s.equation('p_mu coefficient', p_coeff)
    s.equation('q_mu coefficient', q_coeff)
    s.equation('Residual current structures', residual)
    s.equation("Gordon-pair coefficient B multiplying (p' + p)_mu", pair_coeff)
    s.equation('Longitudinal q_mu coefficient', longitudinal_coeff)
    s.equation('Projected F2 numerator', f2_numerator)
    s.equation('Shifted denominator at q = 0', q0_den)
    s.equation('Delta', delta)
    s.text('Scalar loop integral convention',
           'For the cubic denominator, QEDCalc uses the convention '
           '`int d^4l / (-l^2 + Delta - i epsilon)^3 = i*pi^2/(2*Delta)`. '
           'Together with the original vertex prefactor and the Feynman-parameter factor 2, '
           'this leaves alpha/(4*pi) times the triangle parameter integral.')
    s.equation('Parameter integrand after loop integration', sp_latex(parameter_integrand))
    s.text('Triangle parameter integral', f'`{triangle_value}`')
    s.equation('Final one-loop anomalous magnetic moment correction', final_f2)
    s.text('Index validation', '\n'.join(f'- [{m.level}] {m.message}' for m in messages))
    s.save()

    print(f'\nMarkdown session written to: {out}')
    return 0


def sp_latex(expr):
    import sympy as sp
    replacements = {
        sym: sp.Symbol(str(sym)[3:])
        for sym in expr.free_symbols
        if str(sym).startswith('S__')
    }
    return sp.latex(expr.xreplace(replacements))


if __name__ == '__main__':
    sys.exit(main())
