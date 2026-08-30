from __future__ import annotations
import re
from qedcalc.core.expression import (
    QEDExpr, Symbol, Vector, Index, Gamma, Metric, Slash, ScalarProduct,
    Add, NCProduct, ScalarMul, Fraction, Power, VectorComponent, DiracTrace, LoopIntegralExpression
)
from qedcalc.config.symbols import SymbolTable, load_symbol_table, normalize_latex_symbol

NAME = r"(?:\\[A-Za-z]+|[A-Za-z](?:')?)"
TOKEN_RE = re.compile(
    rf"""
    __TRACE\d+__ |
    __FRAC\d+__ |
    \\gamma(?:\^|\_)\{{?{NAME}\}}? |
    g_\{{?{NAME}{NAME}\}}? |
    {NAME}(?:\^|\_)\{{?{NAME}\}}? |
    \\rlap\{{/\}}{NAME} |
    \\rlap\{{/{NAME}\}} |
    {NAME}\^\{{?-?\d+\}}? |
    {NAME}\\cdot{NAME} |
    {NAME} |
    -?\d+ |
    [()+\-]
    """, re.VERBOSE
)


def _strip_math_wrappers(s: str) -> str:
    s = s.strip()
    if s.startswith("$$") and s.endswith("$$"):
        s = s[2:-2]
    # Normalize visual grouping before removing \left/\right.  Curly braces
    # used by LaTeX commands are left untouched; only escaped display braces
    # and square brackets become parser parentheses.
    s = s.replace(r"\left\{", "(").replace(r"\right\}", ")")
    s = s.replace(r"\left[", "(").replace(r"\right]", ")")
    s = s.replace(r"\left(", "(").replace(r"\right)", ")")
    s = s.replace(r"\left", "").replace(r"\right", "")
    s = s.replace("[", "(").replace("]", ")")
    s = s.replace(r"\,", " ").replace(r"\;", " ").replace(r"\times", " ")
    return re.sub(r"\s+", " ", s).strip()


def _extract_group(s: str, start: int):
    if start >= len(s) or s[start] != "{":
        raise ValueError("Expected '{'.")
    depth = 0
    for i in range(start, len(s)):
        if s[i] == "{":
            depth += 1
        elif s[i] == "}":
            depth -= 1
            if depth == 0:
                return s[start + 1:i], i + 1
    raise ValueError("Missing closing '}'.")


def _extract_parenthesized(s: str, start: int):
    if start >= len(s) or s[start] != "(":
        raise ValueError("Expected '('.")
    depth = 0
    for i in range(start, len(s)):
        if s[i] == "(":
            depth += 1
        elif s[i] == ")":
            depth -= 1
            if depth == 0:
                return s[start + 1:i], i + 1
    raise ValueError("Missing closing ')'.")


def _replace_traces(s: str):
    traces = {}
    out = ""
    i = 0
    n = 0
    tag = r"\operatorname{tr}"
    while i < len(s):
        if s.startswith(tag, i):
            j = i + len(tag)
            while j < len(s) and s[j].isspace():
                j += 1
            if j >= len(s) or s[j] != "(":
                raise ValueError("Dirac trace must be followed by a grouped expression.")
            body, j = _extract_parenthesized(s, j)
            key = f"__TRACE{n}__"
            traces[key] = body
            out += key
            n += 1
            i = j
        else:
            out += s[i]
            i += 1
    return out, traces


def _replace_fractions(s: str):
    fractions = {}
    out = ""
    i = 0
    n = 0
    while i < len(s):
        if s.startswith(r"\frac", i):
            j = i + len(r"\frac")
            num, j = _extract_group(s, j)
            den, j = _extract_group(s, j)
            key = f"__FRAC{n}__"
            fractions[key] = (num, den)
            out += key
            n += 1
            i = j
        else:
            out += s[i]
            i += 1
    return out, fractions


def _idx(raw: str, symbols: SymbolTable, pos="down"):
    raw = raw.strip("{}")
    name = symbols.require(raw, "Index", context="Lorentz index")
    return Index(name, pos)


def _make_bare(tok: str, symbols: SymbolTable) -> QEDExpr:
    if re.fullmatch(r"-?\d+", tok):
        return Symbol(tok)
    kind = symbols.classify_bare(tok)
    name = normalize_latex_symbol(tok)
    if kind == "Vector":
        return Vector(name)
    return Symbol(name)


def _parse_atom(tok: str, fractions, traces, symbols: SymbolTable) -> QEDExpr:
    if tok.startswith("__TRACE"):
        return DiracTrace(parse_latex(traces[tok], symbol_table=symbols))

    if tok.startswith("__FRAC"):
        num, den = fractions[tok]
        return Fraction(
            parse_latex(num, symbol_table=symbols),
            parse_latex(den, symbol_table=symbols),
        )

    if tok.startswith(r"\gamma"):
        m = re.match(rf"\\gamma(\^|\_)\{{?({NAME})\}}?", tok)
        if not m:
            raise ValueError(f"Could not parse gamma-matrix syntax: {tok}")
        pos = "up" if m.group(1) == "^" else "down"
        return Gamma(_idx(m.group(2), symbols, pos))

    if tok.startswith("g_"):
        body = tok[2:].strip("{}")
        inds = re.findall(NAME, body)
        if len(inds) != 2:
            raise ValueError(f"Could not parse metric-tensor indices: {tok}")
        return Metric(_idx(inds[0], symbols, "down"), _idx(inds[1], symbols, "down"))

    m = re.match(rf"({NAME})(\^|\_)\{{?({NAME})\}}?$", tok)
    if m:
        raw_vec, op, raw_idx = m.groups()
        vec_name = symbols.require(raw_vec, "Vector", context="vector component")
        pos = "up" if op == "^" else "down"
        return VectorComponent(Vector(vec_name), _idx(raw_idx, symbols, pos))

    if tok.startswith(r"\rlap{/}"):
        raw = tok[len(r"\rlap{/}"):]
        name = symbols.require(raw, "Vector", context="momentum in Feynman slash")
        return Slash(Vector(name))

    if tok.startswith(r"\rlap{/"):
        m = re.match(rf"\\rlap\{{/({NAME})\}}", tok)
        if not m:
            raise ValueError(f"Could not parse Feynman slash: {tok}")
        raw = m.group(1)
        name = symbols.require(raw, "Vector", context="momentum in Feynman slash")
        return Slash(Vector(name))

    if r"\cdot" in tok:
        a, b = tok.split(r"\cdot", 1)
        an = symbols.require(a, "Vector", context="scalar product")
        bn = symbols.require(b, "Vector", context="scalar product")
        return ScalarProduct(Vector(an), Vector(bn))

    m = re.match(rf"({NAME})\^\{{?(-?\d+)\}}?$", tok)
    if m:
        raw, exp_text = m.groups()
        exp = int(exp_text)
        name = normalize_latex_symbol(raw)
        if symbols.has(raw, "Vector"):
            if exp == 2:
                v = Vector(name)
                return ScalarProduct(v, v)
            return Power(Vector(name), exp)
        kind = symbols.classify_bare(raw)
        if kind == "Vector":
            return Power(Vector(name), exp)
        return Power(Symbol(name), exp)

    return _make_bare(tok, symbols)


def parse_latex(
    source: str,
    *,
    symbol_table: SymbolTable | None = None,
    symbols_path: str | None = None,
) -> QEDExpr:
    """Parse the supported QED-LaTeX subset.

    By default, symbols are validated against project-root ``symbols.txt``.
    Unknown symbols are errors; QEDCalc does not silently guess their role.
    """
    if symbol_table is not None and symbols_path is not None:
        raise ValueError("symbol_table and symbols_path cannot be specified at the same time.")
    symbols = symbol_table or load_symbol_table(symbols_path)

    s = _strip_math_wrappers(source)
    s, traces = _replace_traces(s)
    s, fractions = _replace_fractions(s)
    tokens = TOKEN_RE.findall(s)
    if not tokens:
        raise ValueError("The expression could not be parsed.")

    residue = s
    for t in tokens:
        residue = residue.replace(t, "", 1)
    residue = residue.replace("{", "").replace("}", "")
    residue = re.sub(r"\s+", "", residue)
    if residue:
        raise ValueError(f"Unsupported LaTeX syntax remains: {residue}")

    pos = 0

    def parse_sum():
        nonlocal pos
        first_sign = 1
        if pos < len(tokens) and tokens[pos] in ("+", "-"):
            first_sign = 1 if tokens[pos] == "+" else -1
            pos += 1
        terms, signs = [parse_product()], [first_sign]
        while pos < len(tokens) and tokens[pos] in ("+", "-"):
            signs.append(1 if tokens[pos] == "+" else -1)
            pos += 1
            terms.append(parse_product())
        cooked = [t if sgn == 1 else ScalarMul(-1, t) for sgn, t in zip(signs, terms)]
        return cooked[0] if len(cooked) == 1 else Add(*cooked)

    def parse_product():
        nonlocal pos
        factors = []
        while pos < len(tokens) and tokens[pos] not in ("+", "-", ")"):
            if tokens[pos] == "(":
                pos += 1
                factors.append(parse_sum())
                if pos >= len(tokens) or tokens[pos] != ")":
                    raise ValueError("Missing closing parenthesis ')'.")
                pos += 1
            else:
                factors.append(_parse_atom(tokens[pos], fractions, traces, symbols))
                pos += 1
        if not factors:
            raise ValueError("A product has no factors.")
        return factors[0] if len(factors) == 1 else NCProduct(*factors)

    expr = parse_sum()
    if pos != len(tokens):
        raise ValueError(f"Could not parse the end of the expression: {tokens[pos:]}")
    return expr



def parse_loop_integral_latex(
    source: str,
    *,
    symbol_table: SymbolTable | None = None,
    symbols_path: str | None = None,
) -> LoopIntegralExpression:
    r"""Parse a bare loop-integral RHS while preserving its overall normalization.

    Supported form (v0.21):
        <scalar prefactor> \int d^Dk\,d^Dl <QED integrand>

    The scalar prefactor is intentionally preserved as LaTeX text. The loop
    measures and integrand are structurally parsed and validated.
    """
    if symbol_table is not None and symbols_path is not None:
        raise ValueError("symbol_table and symbols_path cannot be specified at the same time.")
    symbols = symbol_table or load_symbol_table(symbols_path)
    raw = source.strip()
    if raw.startswith("$$") and raw.endswith("$$"):
        raw = raw[2:-2].strip()

    m = re.search(r"\\int\s*", raw)
    if not m:
        raise ValueError(r"Loop-integral LaTeX must contain \int.")
    prefactor = raw[:m.start()].strip() or "1"
    rest = raw[m.end():]

    loops = []
    dimension = None
    pos = 0
    measure_re = re.compile(rf"\s*d\^\{{?(\d+|D)\}}?\s*({NAME})\s*(?:\\,)?")
    while True:
        mm = measure_re.match(rest, pos)
        if not mm:
            break
        dim_text = mm.group(1)
        dim = int(dim_text) if dim_text.isdigit() else dim_text
        raw_name = mm.group(2)
        if dimension is None:
            dimension = dim
        elif dimension != dim:
            raise ValueError("Mixed loop-integration dimensions are not supported.")
        name = symbols.require(raw_name, "Vector", context="loop-integration momentum")
        loops.append(Vector(name))
        pos = mm.end()
    if not loops:
        raise ValueError(r"No loop measure such as d^4k was found after \int.")

    integrand_text = rest[pos:].strip()
    if not integrand_text:
        raise ValueError("The loop integral has no integrand.")
    integrand = parse_latex(integrand_text, symbol_table=symbols)
    return LoopIntegralExpression(prefactor, tuple(loops), integrand, dimension or 4)
