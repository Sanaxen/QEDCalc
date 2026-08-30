from pathlib import Path
import sys

from qedcalc import parse_latex, render_latex
from qedcalc.config import load_symbol_table
from qedcalc.core.expression import Fraction, FeynmanParamIntegral
from qedcalc.operations.propagator import (
    recognize_propagators,
    scalarize_fermion_propagators,
    separate_numerator_denominator,
)
from qedcalc.operations.lorentz import contract_metric
from qedcalc.operations.algebra import expand_expression
from qedcalc.operations.dirac import contract_gamma
from qedcalc.operations.denominator import expand_denominator, feynman_parameterize
from qedcalc.operations.onshell import apply_scalar_onshell
from qedcalc.operations.simplify import simplify_expression, expand_commutative
from qedcalc.operations.feynman import complete_square, shift_loop_momentum
from qedcalc.operations.loop import (
    shift_loop_momentum_in_numerator,
    drop_odd_loop_terms,
    symmetric_rank2,
)
from qedcalc.validation.validator import validate_indices
from qedcalc.history import MarkdownSession


def main():
    root = Path(__file__).resolve().parents[1]
    input_path = root / "input" / "vertex_1loop_integrand.tex"
    symbols_path = root / "symbols.txt"

    try:
        symbols = load_symbol_table(symbols_path)
        source = input_path.read_text(encoding="utf-8")
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
        shifted_den = shift_loop_momentum(completed, "l")

        shifted_num = shift_loop_momentum_in_numerator(dirac_num, completed, "l")
        even_num = simplify_expression(drop_odd_loop_terms(expand_expression(shifted_num), "l"))
        symmetric_num = simplify_expression(symmetric_rank2(even_num, "l"))
        messages = validate_indices(expr)
    except (ValueError, FileNotFoundError, TypeError) as exc:
        print("\n[QEDCalc ERROR]")
        print(exc)
        print("\nCheck the input expression and symbols.txt.")
        return 1

    print("=== QEDCalc one-loop stage 3 ===")
    print("=== Input file ===")
    print(input_path)
    print("\n=== Parser interpretation ===")
    print(render_latex(expr))
    print("\n=== Dirac numerator after metric/gamma processing ===")
    print(render_latex(dirac_num))
    print("\n=== Combined Feynman denominator ===")
    print(render_latex(combined_den))
    print("\n=== Completed square ===")
    print(render_latex(completed))
    print("\n=== Denominator after loop-momentum shift ===")
    print(render_latex(shifted_den))
    print("\n=== Numerator after odd-term removal and rank-2 symmetric reduction ===")
    print(render_latex(symmetric_num))

    out = root / "output" / "vertex_1loop_session.md"
    s = MarkdownSession(out, "QED 1-loop vertex correction - calculation session")
    s.text("Symbol definitions", f"`{symbols_path.relative_to(root)}`\n\n{symbols.to_markdown()}")
    s.text("Input file", f"`{input_path.relative_to(root)}`")
    s.equation("Original input", source.strip())
    s.equation("Parser interpretation", expr)
    s.step(1, "Propagator recognition", expr, recognized,
           "Recognize supported fraction structures as propagator candidates.")
    s.step(2, "Fermion propagator scalarization", recognized, scalarized,
           "Convert each fermion propagator into a Dirac numerator and a scalar denominator.")
    s.step(3, "Numerator / denominator separation", scalarized, separated,
           "Separate the Dirac numerator from the commutative scalar denominator product.")
    s.step(4, "Metric contraction", separated.numerator, metric_num,
           "Contract the photon metric tensor with matching Lorentz indices.")
    s.step(5, "Dirac numerator expansion", metric_num, expanded_num,
           "Distribute the non-commutative numerator product over additive factors.")
    s.step(6, "Four-dimensional gamma contraction", expanded_num, dirac_num,
           "Apply supported 4D outer-gamma contraction identities.")
    s.step(7, "Scalar denominator expansion", separated.denominator, expanded_den,
           "Expand squared linear combinations of four-momenta into scalar products.")
    s.step(8, "On-shell scalar conditions", expanded_den, onshell_den,
           "Apply p^2 = m^2 and p'^2 = m^2.")
    s.equation("Feynman-parameterized integrand", fpi)
    s.step(9, "Combined Feynman denominator", fpi.combined_denominator, combined_den,
           "Distribute scalar products and simplify the combined denominator.")
    s.step(10, "Square completion", combined_den, completed,
           "Complete the square in k and identify the shift A = x p' + y p.")
    s.step(11, "Loop-momentum shift in denominator", completed, shifted_den,
           "Define l = k - A.")
    s.step(12, "Loop-momentum shift in numerator", dirac_num, shifted_num,
           "Apply k = l + A to slash and Lorentz-component structures in the numerator.")
    s.step(13, "Odd loop-momentum removal", shifted_num, even_num,
           "Drop monomials that are odd under l -> -l in the symmetric loop integral.")
    s.step(14, "Rank-2 symmetric integration reduction", even_num, symmetric_num,
           "Apply supported four-dimensional rank-2 symmetric-integration rules.")
    s.text("Index validation", "\n".join(f"- [{m.level}] {m.message}" for m in messages))
    s.save()
    print(f"\nMarkdown session written to: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
