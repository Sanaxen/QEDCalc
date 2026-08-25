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


def _visible_width(latex: str) -> int:
    """Approximate rendered width; commands count as one glyph."""
    import re
    text = re.sub(r"\\[A-Za-z]+", "X", latex)
    text = text.replace("{", "").replace("}", "")
    return len(text)


def _top_level_binary_ops(source: str):
    """Return binary + / - positions outside braces and parentheses."""
    positions = []
    brace = 0
    paren = 0
    bracket = 0
    i = 0
    prev_sig = None
    while i < len(source):
        ch = source[i]
        if ch == "\\":
            # Skip TeX command name, but leave delimiters such as \\{ to brace logic.
            j = i + 1
            while j < len(source) and source[j].isalpha():
                j += 1
            if j > i + 1:
                i = j
                continue
        if ch == "{":
            brace += 1
        elif ch == "}":
            brace = max(0, brace - 1)
        elif brace == 0:
            if ch == "(":
                paren += 1
            elif ch == ")":
                paren = max(0, paren - 1)
            elif ch == "[":
                bracket += 1
            elif ch == "]":
                bracket = max(0, bracket - 1)
            elif ch in "+-" and paren == 0 and bracket == 0:
                # Unary signs are not split points.
                left = source[:i].rstrip()
                if left and left[-1] not in "=+-*/,( [":
                    positions.append((i, ch))
        if not ch.isspace():
            prev_sig = ch
        i += 1
    return positions


def _split_terms_keep_operator_previous(source: str):
    """Split a sum while keeping + or - at the END of the previous row."""
    ops = _top_level_binary_ops(source)
    if not ops:
        return [source.strip()]
    rows = []
    last = 0
    for pos, op in ops:
        piece = source[last:pos].strip()
        if piece:
            rows.append(piece + " {}" + op)
        last = pos + 1
    tail = source[last:].strip()
    if tail:
        rows.append(tail)
    return rows


def _find_long_parenthesized_body(source: str):
    """Find a parenthesized group whose body can be split as a sum."""
    stack = []
    pairs = []
    brace = 0
    for i, ch in enumerate(source):
        if ch == "{":
            brace += 1
        elif ch == "}":
            brace = max(0, brace - 1)
        elif brace == 0 and ch == "(":
            stack.append(i)
        elif brace == 0 and ch == ")" and stack:
            a = stack.pop()
            body = source[a + 1:i]
            if len(_split_terms_keep_operator_previous(body)) > 1:
                pairs.append((a, i, body))
    if not pairs:
        return None
    # Prefer the widest useful group.
    return max(pairs, key=lambda x: _visible_width(x[2]))


def _true_wrap_latex(latex: str, max_width: int = 92) -> str:
    """Wrap a long formula with real aligned rows; never create E_{...} proxies."""
    latex = latex.strip()
    if _visible_width(latex) <= max_width:
        return latex

    # First try an equation split at a top-level '='.
    brace = paren = bracket = 0
    eq_pos = None
    for i, ch in enumerate(latex):
        if ch == "{":
            brace += 1
        elif ch == "}":
            brace = max(0, brace - 1)
        elif brace == 0:
            if ch == "(": paren += 1
            elif ch == ")": paren = max(0, paren - 1)
            elif ch == "[": bracket += 1
            elif ch == "]": bracket = max(0, bracket - 1)
            elif ch == "=" and paren == 0 and bracket == 0:
                eq_pos = i
                break

    if eq_pos is not None:
        lhs = latex[:eq_pos].strip()
        rhs = latex[eq_pos + 1:].strip()
        rows = _split_terms_keep_operator_previous(rhs)
        if len(rows) > 1:
            out = [r"\begin{aligned}"]
            out.append(f"{lhs} &= {rows[0]} \\\\")
            for row in rows[1:-1]:
                out.append(f"{row} \\\\")
            if len(rows) > 1:
                out.append(rows[-1])
            out.append(r"\end{aligned}")
            return "\n".join(out)

        # RHS may be one outer parenthesized sum: split INSIDE it instead of proxying.
        grp = _find_long_parenthesized_body(rhs)
        if grp is not None:
            a, b, body = grp
            rows = _split_terms_keep_operator_previous(body)
            prefix = rhs[:a + 1]
            suffix = rhs[b:]
            inner = [r"\begin{aligned}"]
            for row in rows[:-1]:
                inner.append(f"{row} \\\\")
            inner.append(rows[-1])
            inner.append(r"\end{aligned}")
            rhs2 = prefix + "\n" + "\n".join(inner) + "\n" + suffix
            return "\n".join([
                r"\begin{aligned}",
                f"{lhs} &= {rhs2}",
                r"\end{aligned}",
            ])

    # No equation sign: split a top-level sum.
    rows = _split_terms_keep_operator_previous(latex)
    if len(rows) > 1:
        out = [r"\begin{aligned}"]
        for row in rows[:-1]:
            out.append(f"{row} \\\\")
        out.append(rows[-1])
        out.append(r"\end{aligned}")
        return "\n".join(out)

    # Last resort: split inside the widest parenthesized sum.
    grp = _find_long_parenthesized_body(latex)
    if grp is not None:
        a, b, body = grp
        rows = _split_terms_keep_operator_previous(body)
        inner = [r"\begin{aligned}"]
        for row in rows[:-1]:
            inner.append(f"{row} \\\\")
        inner.append(rows[-1])
        inner.append(r"\end{aligned}")
        return latex[:a + 1] + "\n" + "\n".join(inner) + "\n" + latex[b:]

    # Do not invent proxy variables. Return unchanged if no mathematically safe split point exists.
    return latex


def md_equation(title, expr):
    """Render one display equation with genuine line breaks, not proxy definitions."""
    latex = expr if isinstance(expr, str) else render_latex(expr)
    wrapped = _true_wrap_latex(latex, max_width=92)
    return f"### {title}\n\n$$\n{wrapped}\n$$"


def md_step(number, title, before, after, note):
    """Render a calculation step using genuine aligned equation wrapping."""
    before_latex = before if isinstance(before, str) else render_latex(before)
    after_latex = after if isinstance(after, str) else render_latex(after)
    before_block = f"$$\n{_true_wrap_latex(before_latex, max_width=92)}\n$$"
    after_block = f"$$\n{_true_wrap_latex(after_latex, max_width=92)}\n$$"
    return (
        f"### Step {number}: {title}\n\n"
        f"{note}\n\n"
        f"#### Before\n\n{before_block}\n\n"
        f"#### After\n\n{after_block}"
    )


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
    s.text('Original input', md_equation('Original input', source.strip()))
    s.text('Numerator after symmetric loop reduction', md_equation('Numerator after symmetric loop reduction', symmetric_num))
    s.text('Step 15', md_step(15, 'Non-commutative normalization', symmetric_num, normalized_num,
           'Move commutative scalar coefficients outside slash/gamma chains so the Dirac ordering is explicit.'))
    s.text('Step 16', md_step(16, 'Exact external Dirac reduction', normalized_num, dirac_reduced,
           "Recursively commute /p' left and /p right. Each recursion lowers the distance to an external spinor, then the on-shell Dirac equation is applied."))
    s.text('Step 17', md_step(17, 'Momentum-transfer introduction', dirac_reduced, q_current,
           "Introduce q = p' - p, apply p^2 = p'^2 = m^2, and use p.q = -q^2/2."))
    s.text('Step 18', md_step(18, 'First-order q truncation', q_current, q_linear,
           'Discard terms of explicit order q^2 and higher. The magnetic form factor requires the current through first order in q.'))
    s.text('Gamma_mu coefficient', md_equation('Gamma_mu coefficient', gamma_coeff))
    s.text('p_mu coefficient', md_equation('p_mu coefficient', p_coeff))
    s.text('q_mu coefficient', md_equation('q_mu coefficient', q_coeff))
    s.text('Residual current structures', md_equation('Residual current structures', residual))
    s.text("Gordon-pair coefficient B multiplying (p' + p)_mu", md_equation("Gordon-pair coefficient B multiplying (p' + p)_mu", pair_coeff))
    s.text('Longitudinal q_mu coefficient', md_equation('Longitudinal q_mu coefficient', longitudinal_coeff))
    s.text('Projected F2 numerator', md_equation('Projected F2 numerator', f2_numerator))
    s.text('Shifted denominator at q = 0', md_equation('Shifted denominator at q = 0', q0_den))
    s.text('Delta', md_equation('Delta', delta))
    s.text('Scalar loop integral convention',
           'For the cubic denominator, QEDCalc uses the convention '
           '`int d^4l / (-l^2 + Delta - i epsilon)^3 = i*pi^2/(2*Delta)`. '
           'Together with the original vertex prefactor and the Feynman-parameter factor 2, '
           'this leaves alpha/(4*pi) times the triangle parameter integral.')
    s.text('Parameter integrand after loop integration', md_equation('Parameter integrand after loop integration', sp_latex(parameter_integrand)))
    s.text('Triangle parameter integral', f'`{triangle_value}`')
    s.text('Final one-loop anomalous magnetic moment correction', md_equation('Final one-loop anomalous magnetic moment correction', final_f2))
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
