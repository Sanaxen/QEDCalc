from pathlib import Path
import sys

from qedcalc import parse_latex, render_latex
from qedcalc.config import load_symbol_table
from qedcalc.core.expression import Fraction, Symbol, Vector, Index, Gamma, VectorComponent, Add, Product
from qedcalc.operations.propagator import recognize_propagators, scalarize_fermion_propagators, separate_numerator_denominator
from qedcalc.operations.lorentz import contract_metric
from qedcalc.operations.algebra import expand_expression
from qedcalc.operations.dirac import contract_gamma
from qedcalc.operations.denominator import expand_denominator, feynman_parameterize
from qedcalc.operations.onshell import apply_scalar_onshell
from qedcalc.operations.simplify import expand_commutative, simplify_expression
from qedcalc.operations.feynman import complete_square, shift_loop_momentum
from qedcalc.operations.loop import shift_loop_momentum_in_numerator, drop_odd_loop_terms, symmetric_rank2
from qedcalc.operations.spinor import sandwich, reduce_external_dirac
from qedcalc.operations.momentum import introduce_q, take_q_zero
from qedcalc.operations.projector import gordon_rhs, project_f2_gordon_basis, form_factors_from_gordon_basis
from qedcalc.validation.validator import validate_indices
from qedcalc.history.markdown_session import MarkdownSession


def main():
    root=Path(__file__).resolve().parents[1]
    input_path=root/'input'/'vertex_1loop_integrand.tex'
    symbols_path=root/'symbols.txt'
    try:
        symbols=load_symbol_table(symbols_path)
        source=input_path.read_text(encoding='utf-8')
        expr=parse_latex(source,symbol_table=symbols)
        recognized=recognize_propagators(expr)
        scalarized=scalarize_fermion_propagators(recognized)
        separated=separate_numerator_denominator(scalarized)

        metric_num=contract_metric(separated.numerator)
        expanded_num=expand_expression(metric_num)
        dirac_num=simplify_expression(contract_gamma(expanded_num))

        expanded_den=expand_denominator(separated.denominator)
        onshell_den=apply_scalar_onshell(expanded_den)
        fpi=feynman_parameterize(Fraction(dirac_num,onshell_den))
        combined_den=expand_commutative(fpi.combined_denominator)
        completed=complete_square(combined_den)
        shifted_den=shift_loop_momentum(completed,'l')
        shifted_num=shift_loop_momentum_in_numerator(dirac_num,completed,'l')
        even_num=simplify_expression(drop_odd_loop_terms(expand_expression(shifted_num),'l'))
        symmetric_num=simplify_expression(symmetric_rank2(even_num,'l'))

        spinor_expr=sandwich(symmetric_num)
        dirac_reduced=reduce_external_dirac(spinor_expr)
        q_expr=introduce_q(dirac_reduced)

        q_den=introduce_q(shifted_den)
        q0_den=apply_scalar_onshell(take_q_zero(q_den))

        # A deliberately clean basis example verifies the Gordon/F2 machinery.
        A=Symbol('A'); B=Symbol('B'); idx=Index('mu','down')
        clean_current=Add(
            Product(A,Gamma(idx)),
            Product(B,VectorComponent(Vector("p'"),idx)),
            Product(B,VectorComponent(Vector('p'),idx)),
        )
        clean_ff=form_factors_from_gordon_basis(A,B)
        clean_f2=project_f2_gordon_basis(clean_current)
        messages=validate_indices(expr)
    except (ValueError,FileNotFoundError,TypeError,RuntimeError) as exc:
        print('\n[QEDCalc ERROR]')
        print(exc)
        print('\nCheck the input expression and symbols.txt.')
        return 1

    print('=== QEDCalc v0.8.0 ===')
    print('=== Numerator after symmetric loop reduction ===')
    print(render_latex(symmetric_num))
    print('\n=== External-spinor Dirac reduction ===')
    print(render_latex(dirac_reduced))
    print('\n=== q = p\' - p introduced in the operator ===')
    print(render_latex(q_expr))
    print('\n=== Denominator at q = 0 ===')
    print(render_latex(q0_den))
    print('\n=== Gordon-basis verification current ===')
    print(render_latex(clean_current))
    print('\n=== Corresponding form-factor decomposition ===')
    print(render_latex(clean_ff))
    print('\n=== F2 extracted from B(p\' + p)_mu ===')
    print(render_latex(clean_f2))

    out=root/'output'/'vertex_1loop_session.md'
    s=MarkdownSession(out,'QED 1-loop vertex correction - calculation session')
    s.text('Version','QEDCalc v0.8.0')
    s.text('Symbol definitions',f'`{symbols_path.relative_to(root)}`\n\n{symbols.to_markdown()}')
    s.text('Input file',f'`{input_path.relative_to(root)}`')
    s.equation('Original input',source.strip())
    s.equation('Numerator after symmetric loop reduction',symmetric_num)
    s.step(15,'External spinor sandwich',symmetric_num,spinor_expr,
           "Wrap the operator as bar u(p') [ ... ] u(p) so external Dirac equations have a well-defined domain.")
    s.step(16,'External Dirac reduction',spinor_expr,dirac_reduced,
           "Use gamma anticommutation to move external /p' left and /p right, then apply the on-shell Dirac equations only at the spinor edges.")
    s.step(17,'Momentum-transfer introduction',dirac_reduced,q_expr,
           "Introduce q = p' - p by substituting p' = p + q inside the operator.")
    s.step(18,'q = 0 denominator limit',shifted_den,q0_den,
           "Introduce q in the shifted denominator, set q = 0, and re-apply scalar on-shell conditions.")
    s.equation('Gordon identity used by the projector',gordon_rhs())
    s.equation('Clean Gordon-basis verification current',clean_current)
    s.equation('Form-factor decomposition of the verification current',clean_ff)
    s.equation('F2 extracted from the verification current',clean_f2)
    s.text('Current limitation',
           "The Gordon/F2 projector is intentionally strict. It currently accepts a current only after it has been reduced to A gamma_mu + B(p'_mu + p_mu). Automatic extraction of A and B from the full one-loop numerator is the next implementation step.")
    s.text('Index validation','\n'.join(f'- [{m.level}] {m.message}' for m in messages))
    s.save()
    print(f'\nMarkdown session written to: {out}')
    return 0

if __name__=='__main__':
    sys.exit(main())
