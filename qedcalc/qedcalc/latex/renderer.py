from qedcalc.core.expression import (
    QEDExpr, Symbol, Vector, Index, Gamma, Metric, Slash, ScalarProduct,
    Add, Product, NCProduct, ScalarMul, Power, Fraction, FermionPropagator, PhotonPropagator, VectorComponent, VectorLinearCombination, CompletedSquare, FeynmanParamIntegral, SpinorSandwich, PauliTerm, FormFactorDecomposition, LoopMomentumSet,
    MultiLoopCompletedSquare, PoleTerm, LaurentResult, Counterterm, GeneralFeynmanParamIntegral, CountertermInsertion, DiracTrace, LoopIntegralExpression, SelfEnergySubdiagram
)
from qedcalc.config.symbols import LATEX_COMMAND_NAMES
import re

def _name(name):
    """Convert an internal identifier to an unambiguous LaTeX symbol.

    Internal identifiers stay ASCII-friendly (for example ``deltaZ1``),
    while rendered mathematics uses conventional QED notation
    (``\\delta Z_1``).  Exact Greek names are always emitted as LaTeX
    commands, so ``zeta`` becomes ``\\zeta`` and ``omega`` becomes
    ``\\omega``.
    """
    if name.startswith("\\"):
        return name

    # Standard renormalization constants used by QEDCalc.
    m = re.fullmatch(r"deltaZ(\d+)", name)
    if m:
        return rf"\delta Z_{{{m.group(1)}}}"
    m = re.fullmatch(r"delta_Z(\d+)", name)
    if m:
        return rf"\delta Z_{{{m.group(1)}}}"
    if name == "delta_m":
        return r"\delta m"

    # Frequently used regulator identifiers.
    if name == "epsilon_UV":
        return r"\epsilon_{\mathrm{UV}}"
    if name == "epsilon_IR":
        return r"\epsilon_{\mathrm{IR}}"

    # Generic configured Greek symbols.
    if name in LATEX_COMMAND_NAMES:
        return "\\" + name

    # Generic Greek symbol with an explicit underscore suffix, e.g. zeta_n.
    if "_" in name:
        head, tail = name.split("_", 1)
        if head in LATEX_COMMAND_NAMES and tail:
            return rf"\{head}_{{{tail}}}"

    return name

def _coeff_latex(coeff):
    if isinstance(coeff, QEDExpr):
        return render_latex(coeff)
    try:
        import sympy as sp
        if isinstance(coeff, sp.Basic):
            return sp.latex(coeff)
    except Exception:
        pass
    text = str(coeff)
    if "/" in text:
        num, den = text.split("/", 1)
        if num.startswith("-"):
            return r"-\frac{" + num[1:] + "}{" + den + "}"
        return r"\frac{" + num + "}{" + den + "}"
    return text


def _coeff_is_negative(coeff):
    """Return True only when a scalar coefficient is provably negative."""
    if isinstance(coeff, (int, float)):
        return coeff < 0
    try:
        import sympy as sp
        if isinstance(coeff, sp.Basic):
            return bool(coeff.is_negative)
    except Exception:
        pass
    return False

def render_latex(expr: QEDExpr) -> str:
    if isinstance(expr, Symbol): return _name(expr.name)
    if isinstance(expr, Vector): return _name(expr.name)
    if isinstance(expr, Index): return _name(expr.name)
    if isinstance(expr, Gamma):
        op = "^" if expr.index.position == "up" else "_"
        return rf"\gamma{op}{{{_name(expr.index.name)}}}"
    if isinstance(expr, Metric):
        return rf"g_{{{_name(expr.left.name)}{_name(expr.right.name)}}}"
    if isinstance(expr, Slash):
        inner = render_latex(expr.arg)
        if isinstance(expr.arg, Add):
            return rf"\rlap{{/}}\left({inner}\right)"
        return rf"\rlap{{/}}{inner}"
    if isinstance(expr, ScalarProduct): return rf"{render_latex(expr.left)}\cdot {render_latex(expr.right)}"
    if isinstance(expr, VectorComponent):
        op = "^" if expr.index.position == "up" else "_"
        return rf"{render_latex(expr.vector)}{op}{{{_name(expr.index.name)}}}"
    if isinstance(expr, DiracTrace):
        return rf"\operatorname{{tr}}\left[{render_latex(expr.argument)}\right]"
    if isinstance(expr, SelfEnergySubdiagram):
        label = r"\Sigma_R" if expr.renormalized else r"\Sigma"
        return label + rf"^{{({expr.order})}}\left({render_latex(expr.external_momentum)}\right)"
    if isinstance(expr, LoopIntegralExpression):
        measures = r"\,".join(
            rf"d^{{{expr.dimension}}}{render_latex(v)}" for v in expr.loops
        )
        pref = expr.prefactor_latex.strip()
        if pref == "1":
            pref = ""
        else:
            pref += r"\,"
        return pref + r"\int " + measures + r"\," + render_latex(expr.integrand)
    if isinstance(expr, VectorLinearCombination):
        chunks = []
        for i, (coeff, vec) in enumerate(expr.terms):
            term = rf"{render_latex(coeff)}\,{render_latex(vec)}"
            if i == 0:
                chunks.append(term)
            elif term.startswith("-"):
                chunks.append(" - " + term[1:])
            else:
                chunks.append(" + " + term)
        return "".join(chunks) if chunks else "0"
    if isinstance(expr, CompletedSquare):
        shift = render_latex(expr.shift)
        loop = render_latex(expr.loop)
        sq = rf"\left({loop}-\left({shift}\right)\right)^2"
        if expr.quadratic_sign == -1:
            sq = "-" + sq
        return sq + " + " + render_latex(expr.remainder)
    if isinstance(expr, LoopMomentumSet):
        return r"\left\{" + ", ".join(render_latex(v) for v in expr.momenta) + r"\right\}"
    if isinstance(expr, MultiLoopCompletedSquare):
        kvec = r"\begin{pmatrix}" + r" \\ ".join(render_latex(v) for v in expr.loops) + r"\end{pmatrix}"
        svec = r"\begin{pmatrix}" + r" \\ ".join(render_latex(v) for v in expr.shifts) + r"\end{pmatrix}"
        rows = []
        for row in expr.matrix:
            rows.append(" & ".join(render_latex(x) for x in row))
        matrix = r"\begin{pmatrix}" + r" \\ ".join(rows) + r"\end{pmatrix}"
        return (r"\left(" + kvec + " + " + svec + r"\right)^T " + matrix
                + r"\left(" + kvec + " + " + svec + r"\right) + "
                + render_latex(expr.remainder))
    if isinstance(expr, PoleTerm):
        if expr.regulator.startswith("epsilon"):
            reg = r"\epsilon"
        elif expr.regulator.startswith("\\"):
            reg = expr.regulator
        else:
            reg = "\\" + expr.regulator
        reg = reg + r"_{\mathrm{" + expr.kind + r"}}"
        den = reg if expr.order == 1 else reg + "^{" + str(expr.order) + "}"
        return r"\frac{" + render_latex(expr.coefficient) + "}{" + den + "}"
    if isinstance(expr, LaurentResult):
        parts = [render_latex(p) for p in expr.poles]
        parts.append(render_latex(expr.finite))
        return " + ".join(parts)
    if isinstance(expr, Counterterm):
        structure = render_latex(expr.structure)
        if isinstance(expr.structure, Add):
            structure = r"\left(" + structure + r"\right)"
        if isinstance(expr.structure, Symbol) and expr.structure.name == "1":
            body = render_latex(expr.coefficient)
        else:
            body = render_latex(expr.coefficient) + r"\," + structure
        return r"\underbrace{" + body + r"}_{" + _name(expr.name) + r"}"
    if isinstance(expr, SpinorSandwich):
        return rf"\bar u({render_latex(expr.outgoing)})\,\left[{render_latex(expr.operator)}\right]\,u({render_latex(expr.incoming)})"
    if isinstance(expr, PauliTerm):
        mu = _name(expr.index.name)
        q = render_latex(expr.momentum)
        return rf"i\sigma_{{{mu}\nu}}{q}^{{\nu}}"
    if isinstance(expr, FormFactorDecomposition):
        mu = _name(expr.index.name)
        q = render_latex(expr.momentum_transfer)
        m = render_latex(expr.mass)
        return rf"\left({render_latex(expr.f1)}\right)\,\gamma_{{{mu}}} + \left({render_latex(expr.f2)}\right)\,\frac{{i\sigma_{{{mu}\nu}}{q}^{{\nu}}}}{{2{m}}}"
    if isinstance(expr, Fraction): return rf"\frac{{{render_latex(expr.numerator)}}}{{{render_latex(expr.denominator)}}}"
    if isinstance(expr, FermionPropagator): return rf"\frac{{1}}{{{render_latex(expr.denominator)}}}"
    if isinstance(expr, PhotonPropagator): return rf"\frac{{{render_latex(expr.numerator)}}}{{{render_latex(expr.denominator)}}}"
    if isinstance(expr, Power):
        if isinstance(expr.base, (Symbol, Vector)):
            return rf"{render_latex(expr.base)}^{{{expr.exponent}}}"
        return rf"\left({render_latex(expr.base)}\right)^{{{expr.exponent}}}"
    if isinstance(expr, ScalarMul):
        inner = render_latex(expr.expr)
        coeff = _coeff_latex(expr.coeff)
        if isinstance(expr.expr, Symbol) and expr.expr.name == "1":
            return coeff
        if expr.coeff == -1:
            return rf"-\left({inner}\right)"
        return coeff + rf"\left({inner}\right)"
    if isinstance(expr, Add):
        chunks = []
        for i, t in enumerate(expr.terms):
            txt = render_latex(t)
            if i == 0: chunks.append(txt)
            elif txt.startswith("-"): chunks.append(r" - " + txt[1:])
            else: chunks.append(r" + " + txt)
        return "".join(chunks)
    if isinstance(expr, Product):
        parts = []
        for f in expr.factors:
            txt = render_latex(f)
            if isinstance(f, Add):
                txt = rf"\left({txt}\right)"
            elif isinstance(f, ScalarMul) and _coeff_is_negative(f.coeff):
                txt = rf"\left({txt}\right)"
            parts.append(txt)
        return r"\,".join(parts)
    if isinstance(expr, GeneralFeynmanParamIntegral):
        pars = [render_latex(x) for x in expr.parameters]
        dim = len(pars)
        measure = rf"\int_{{\Delta_{{{dim}}}}} " + r"\,".join(rf"d{x}" for x in pars)
        weight = render_latex(expr.parameter_weight)
        num = render_latex(expr.numerator)
        den = render_latex(expr.combined_denominator)
        body = rf"\frac{{{weight}\,{num}}}{{\left[{den}\right]^{{{expr.total_power}}}}}"
        pref = render_latex(expr.prefactor)
        if pref == "1":
            pref = ""
        else:
            pref += r"\,"
        return pref + measure + r"\," + body
    if isinstance(expr, CountertermInsertion):
        return (r"\underbrace{" + render_latex(expr.result) + r"}_{\mathrm{CT\ "
                + expr.mode.replace("_", r"\_") + r"\ at\ factor\ " + str(expr.factor_index) + r"}}")
    if isinstance(expr, FeynmanParamIntegral):
        pars = [render_latex(x) for x in expr.parameters]
        if len(pars) == 2:
            measure = rf"\int_0^1 d{pars[0]}\int_0^{{1-{pars[0]}}} d{pars[1]}"
        else:
            dim = len(pars)
            measure = rf"\int_{{\Delta_{{{dim}}}}} " + r"\,".join(rf"d{x}" for x in pars)
        body = rf"\frac{{{render_latex(expr.numerator)}}}{{\left[{render_latex(expr.combined_denominator)}\right]^{{{expr.power}}}}}"
        pref = "" if expr.prefactor == 1 else str(expr.prefactor) + r"\,"
        return pref + measure + r"\," + body
    if isinstance(expr, NCProduct):
        parts = []
        for f in expr.factors:
            txt = render_latex(f)
            # A negative factor inside a product must be visually grouped.
            # Without grouping, "A\,-B" is rendered like subtraction even
            # though the internal expression means A * (-B).
            if isinstance(f, ScalarMul) and f.coeff == -1:
                # Render A * (-B) as A\,\left(-B\right), not A\,-B.
                txt = rf"\left(-{render_latex(f.expr)}\right)"
            elif isinstance(f, ScalarMul) and _coeff_is_negative(f.coeff):
                txt = rf"\left({txt}\right)"
            elif isinstance(f, Add):
                txt = rf"\left({txt}\right)"
            parts.append(txt)
        return r"\,".join(parts)
    raise TypeError(f"Unsupported expression type: {type(expr).__name__}")
