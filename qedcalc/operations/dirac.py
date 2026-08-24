from functools import lru_cache
from qedcalc.core.expression import (
    QEDExpr, Gamma, Slash, Vector, VectorComponent, Index,
    NCProduct, Product, ScalarMul, Add, Symbol
)


def _extract_gamma_like(obj):
    if isinstance(obj, (Gamma, Slash)):
        return 1, obj
    if isinstance(obj, ScalarMul) and isinstance(obj.expr, (Gamma, Slash)):
        return obj.coeff, obj.expr
    return None

def _gamma_like(obj):
    return _extract_gamma_like(obj) is not None


def _outer_same_index(factors):
    if len(factors) < 3:
        return None
    a, c = factors[0], factors[-1]
    if not isinstance(a, Gamma) or not isinstance(c, Gamma):
        return None
    if a.index.name != c.index.name or a.index.position == c.index.position:
        return None
    return a.index.name


def contract_outer_gamma_4d(expr: QEDExpr):
    """Contract an outer gamma pair in four dimensions.

    Implemented identities:
      gamma^a X gamma_a = -2 X                       (one gamma-like X)
      gamma^a X Y gamma_a = 4 contraction(X,Y)      (two gamma-like factors)
      gamma^a X Y Z gamma_a = -2 Z Y X              (three gamma-like factors)

    Slash(v) is treated as v_mu gamma^mu.  The two-factor identity therefore
    produces scalar products or vector components where appropriate.
    """
    if isinstance(expr, Add):
        return Add(*(contract_outer_gamma_4d(t) for t in expr.terms))
    if isinstance(expr, ScalarMul):
        return ScalarMul(expr.coeff, contract_outer_gamma_4d(expr.expr))
    if not isinstance(expr, NCProduct):
        return expr

    factors = list(expr.factors)
    idx = _outer_same_index(factors)
    if idx is None:
        return NCProduct(*(contract_outer_gamma_4d(f) for f in factors))

    inner = factors[1:-1]
    scalars = [f for f in inner if isinstance(f, Symbol)]
    gamma_parts = [_extract_gamma_like(f) for f in inner if _gamma_like(f)]
    gammas = [g for _, g in gamma_parts]
    gamma_coeff = 1
    for c, _ in gamma_parts:
        gamma_coeff *= c
    other = [f for f in inner if not isinstance(f, Symbol) and not _gamma_like(f)]
    if other or len(gammas) not in (0, 1, 2, 3):
        return expr

    scalar_product = Product(*scalars) if len(scalars) > 1 else (scalars[0] if scalars else None)

    if len(gammas) == 0:
        core = Symbol("4")
    elif len(gammas) == 1:
        core = ScalarMul(-2, gammas[0])
    elif len(gammas) == 2:
        a, b = gammas
        if isinstance(a, Slash) and isinstance(b, Slash):
            from qedcalc.core.expression import ScalarProduct
            core = ScalarMul(4, ScalarProduct(a.arg, b.arg))
        elif isinstance(a, Slash) and isinstance(b, Gamma):
            core = ScalarMul(4, VectorComponent(a.arg, Index(b.index.name, b.index.position)))
        elif isinstance(a, Gamma) and isinstance(b, Slash):
            core = ScalarMul(4, VectorComponent(b.arg, Index(a.index.name, a.index.position)))
        else:
            # Two explicit gamma matrices contract to a metric.  Keep the
            # result formal rather than inventing index positions.
            from qedcalc.core.expression import Metric
            core = ScalarMul(4, Metric(a.index, b.index))
    else:
        core = ScalarMul(-2, NCProduct(gammas[2], gammas[1], gammas[0]))

    if gamma_coeff != 1:
        core = ScalarMul(gamma_coeff, core)
    if scalar_product is None:
        return core
    return Product(scalar_product, core)


def contract_gamma(expr):
    """Apply elementary and outer-pair four-dimensional gamma contractions."""
    if isinstance(expr, Add):
        return Add(*(contract_gamma(t) for t in expr.terms))
    if isinstance(expr, ScalarMul):
        return ScalarMul(expr.coeff, contract_gamma(expr.expr))
    if isinstance(expr, Product):
        return Product(*(contract_gamma(f) for f in expr.factors))
    if not isinstance(expr, NCProduct):
        return expr

    # First use the general outer-pair rule when applicable.
    out = contract_outer_gamma_4d(expr)
    if out != expr:
        return out

    f = list(expr.factors)
    # Direct four-dimensional contraction gamma^a gamma_a = 4.
    if (len(f) == 2 and isinstance(f[0], Gamma) and isinstance(f[1], Gamma)
            and f[0].index.name == f[1].index.name
            and f[0].index.position != f[1].index.position):
        return Symbol("4")
    i = 0
    result = []
    while i < len(f):
        if i + 2 < len(f):
            a, b, c = f[i:i+3]
            if (
                isinstance(a, Gamma) and _gamma_like(b) and isinstance(c, Gamma)
                and a.index.name == c.index.name
                and a.index.position != c.index.position
            ):
                result.append(ScalarMul(-2, b))
                i += 3
                continue
        result.append(f[i])
        i += 1
    if len(result) == 1:
        return result[0]
    return NCProduct(*result)


def _trace_pair_4d(a, b):
    """Return the Lorentz scalar/tensor produced by Tr[a b]/4.

    ``a`` and ``b`` are Gamma or Slash objects.
    """
    from qedcalc.core.expression import Metric, VectorComponent, ScalarProduct
    if isinstance(a, Gamma) and isinstance(b, Gamma):
        return Metric(a.index, b.index)
    if isinstance(a, Slash) and isinstance(b, Gamma):
        return VectorComponent(a.arg, b.index)
    if isinstance(a, Gamma) and isinstance(b, Slash):
        return VectorComponent(b.arg, a.index)
    if isinstance(a, Slash) and isinstance(b, Slash):
        return ScalarProduct(a.arg, b.arg)
    raise TypeError("Dirac trace supports Gamma and Slash factors only.")


def dirac_trace_4d(expr: QEDExpr):
    """Evaluate a four-dimensional Dirac trace after algebraic expansion.

    Supported monomials contain 0, 2, or 4 Gamma/Slash factors together with
    commutative scalar factors. Odd traces vanish. This is sufficient for the
    one-loop vacuum-polarization numerator and deliberately rejects longer
    chains instead of guessing a reduction.
    """
    from qedcalc.operations.algebra import expand_expression, normalize_noncommutative_products
    from qedcalc.operations.simplify import simplify_expression
    from qedcalc.core.expression import Metric, VectorComponent, ScalarProduct

    expanded = normalize_noncommutative_products(expand_expression(expr))

    def one(term):
        coeff = []
        chain = []

        def collect_factor(f):
            if isinstance(f, (Gamma, Slash)):
                chain.append(f)
            elif isinstance(f, NCProduct):
                for q in f.factors:
                    collect_factor(q)
            else:
                coeff.append(f)

        if isinstance(term, Product):
            for f in term.factors:
                collect_factor(f)
        elif isinstance(term, NCProduct):
            for f in term.factors:
                collect_factor(f)
        elif isinstance(term, ScalarMul):
            inner = one(term.expr)
            return simplify_expression(ScalarMul(term.coeff, inner))
        else:
            collect_factor(term)

        scalar = Symbol("1") if not coeff else (coeff[0] if len(coeff) == 1 else Product(*coeff))
        n = len(chain)
        if n % 2 == 1:
            return Symbol("0")
        if n == 0:
            return simplify_expression(ScalarMul(4, scalar))
        if n == 2:
            core = _trace_pair_4d(chain[0], chain[1])
            return simplify_expression(ScalarMul(4, Product(scalar, core)))
        if n == 4:
            c12 = _trace_pair_4d(chain[0], chain[1])
            c34 = _trace_pair_4d(chain[2], chain[3])
            c13 = _trace_pair_4d(chain[0], chain[2])
            c24 = _trace_pair_4d(chain[1], chain[3])
            c14 = _trace_pair_4d(chain[0], chain[3])
            c23 = _trace_pair_4d(chain[1], chain[2])
            core = Add(Product(c12, c34), ScalarMul(-1, Product(c13, c24)), Product(c14, c23))
            return simplify_expression(ScalarMul(4, Product(scalar, core)))
        raise ValueError("dirac_trace_4d currently supports traces with at most four Gamma/Slash factors.")

    if isinstance(expanded, Add):
        return simplify_expression(Add(*(one(t) for t in expanded.terms)))
    return simplify_expression(one(expanded))

# --- v0.25: arbitrary-length D-dimensional Clifford trace ---

def _trace_pair_ddim(a, b):
    """Return the Lorentz contraction produced by pairing two Clifford factors.

    The Clifford trace recursion itself is dimension independent; D enters
    later when closed metric-index networks are contracted.
    """
    from qedcalc.core.expression import Gamma, Slash, Metric, VectorComponent, ScalarProduct
    if isinstance(a, Gamma) and isinstance(b, Gamma):
        return Metric(a.index, b.index)
    if isinstance(a, Gamma) and isinstance(b, Slash):
        return VectorComponent(b.arg, a.index)
    if isinstance(a, Slash) and isinstance(b, Gamma):
        return VectorComponent(a.arg, b.index)
    if isinstance(a, Slash) and isinstance(b, Slash):
        return ScalarProduct(a.arg, b.arg)
    raise TypeError("D-dimensional Dirac trace supports Gamma and Slash factors only.")


from functools import lru_cache

@lru_cache(maxsize=None)
def _trace_word_ddim(chain):
    """Recursive trace of an even Gamma/Slash word with Tr(1)=4."""
    from qedcalc.core.expression import Symbol, Add, Product, ScalarMul
    from qedcalc.operations.simplify import simplify_expression
    n = len(chain)
    if n == 0:
        return Symbol("4")
    if n % 2:
        return Symbol("0")
    first = chain[0]
    terms = []
    for j in range(1, n):
        pair = _trace_pair_ddim(first, chain[j])
        rest = chain[1:j] + chain[j+1:]
        sub = _trace_word_ddim(rest)
        term = Product(pair, sub)
        # Tr(g1 ... g2n) = sum_j (-1)^(j+1) (g1.gj) Tr(rest)
        if j % 2 == 0:
            term = ScalarMul(-1, term)
        terms.append(term)
    return simplify_expression(terms[0] if len(terms) == 1 else Add(*terms))


def dirac_trace_ddim(expr: QEDExpr):
    """Evaluate an arbitrary-length D-dimensional Dirac trace.

    This function expands additive Dirac numerators, preserves scalar factors,
    recursively evaluates any even Gamma/Slash word, and leaves Lorentz metric
    contraction to ``contract_fully_scalar_lorentz``.

    No gamma5 is supported.  The trace normalization is Tr(1)=4.
    """
    from qedcalc.core.expression import Symbol, Add, Product, NCProduct, ScalarMul, Gamma, Slash
    from qedcalc.operations.algebra import expand_expression, normalize_noncommutative_products
    from qedcalc.operations.simplify import simplify_expression, expand_commutative

    expanded = expand_expression(expr)
    expanded = normalize_noncommutative_products(expanded)
    expanded = expand_expression(expanded)

    def one(term):
        term = normalize_noncommutative_products(term)
        scalar_factors = []
        chain = []

        def absorb(f):
            if isinstance(f, NCProduct):
                for x in f.factors:
                    absorb(x)
            elif isinstance(f, (Gamma, Slash)):
                chain.append(f)
            else:
                scalar_factors.append(f)

        if isinstance(term, Product):
            for f in term.factors:
                absorb(f)
        elif isinstance(term, NCProduct):
            absorb(term)
        elif isinstance(term, ScalarMul):
            scalar_factors.append(Symbol(str(term.coeff)))
            absorb(term.expr)
        elif isinstance(term, (Gamma, Slash)):
            chain.append(term)
        else:
            scalar_factors.append(term)

        tr = _trace_word_ddim(tuple(chain))
        if isinstance(tr, Symbol) and tr.name == "0":
            return tr
        factors = scalar_factors + [tr]
        out = factors[0] if len(factors) == 1 else Product(*factors)
        return expand_commutative(simplify_expression(out))

    if isinstance(expanded, Add):
        return expand_commutative(simplify_expression(Add(*(one(t) for t in expanded.terms))))
    return expand_commutative(simplify_expression(one(expanded)))

# --- v0.25: optimized fully-contracted trace directly to SymPy ---
def _dirac_poly_terms(expr):
    """Expand a Dirac polynomial into (SymPy scalar coefficient, Clifford word)."""
    import sympy as sp
    from qedcalc.core.expression import Symbol, Gamma, Slash, Add, Product, NCProduct, ScalarMul

    if isinstance(expr, Gamma):
        return [(sp.Integer(1), (expr,))]
    if isinstance(expr, Slash):
        return [(sp.Integer(1), (expr,))]
    if isinstance(expr, Symbol):
        try:
            return [(sp.sympify(expr.name), tuple())]
        except Exception:
            return [(sp.Symbol(expr.name), tuple())]
    if isinstance(expr, ScalarMul):
        return [(sp.sympify(expr.coeff) * c, w) for c, w in _dirac_poly_terms(expr.expr)]
    if isinstance(expr, Add):
        out=[]
        for t in expr.terms:
            out.extend(_dirac_poly_terms(t))
        return out
    if isinstance(expr, (Product, NCProduct)):
        acc=[(sp.Integer(1), tuple())]
        for f in expr.factors:
            ft=_dirac_poly_terms(f)
            new=[]
            for c1,w1 in acc:
                for c2,w2 in ft:
                    new.append((c1*c2, w1+w2))
            acc=new
        return acc
    raise TypeError(f"Unsupported structure in optimized Dirac polynomial expansion: {type(expr).__name__}")


@lru_cache(maxsize=None)
def _pairing_patterns(n):
    """Return (sign,pairs) for all perfect pairings with Clifford-trace signs."""
    from functools import lru_cache

    @lru_cache(maxsize=None)
    def rec(indices):
        indices=tuple(indices)
        if not indices:
            return ((1, tuple()),)
        first=indices[0]
        out=[]
        # j is the position within the current word; sign is +,-,+,...
        for j in range(1,len(indices)):
            second=indices[j]
            sign = 1 if j % 2 == 1 else -1
            rest=indices[1:j]+indices[j+1:]
            for s,pairs in rec(rest):
                out.append((sign*s, ((first,second),)+pairs))
        return tuple(out)
    return rec(tuple(range(n)))


def _sp_atom_name(a, b):
    names=sorted((a,b))
    return f"SP__{names[0]}__{names[1]}"


def _evaluate_clifford_pairing_key(word, pairs):
    """Evaluate one pairing to a canonical scalar-monomial key.

    The key is ``(D_power, tuple(sorted(SP_atom_names)))``.  Keeping the
    pairing result structural avoids constructing and repeatedly adding large
    SymPy expressions inside long D-dimensional traces.
    """
    from collections import Counter, defaultdict
    from qedcalc.core.expression import Gamma, Slash, Vector

    d_power = 0
    sp_atoms = []
    metrics = []
    stubs = []
    for i, j in pairs:
        a, b = word[i], word[j]
        if isinstance(a, Slash) and isinstance(b, Slash):
            if not isinstance(a.arg, Vector) or not isinstance(b.arg, Vector):
                raise TypeError("Optimized trace currently requires Slash(Vector).")
            sp_atoms.append(_sp_atom_name(a.arg.name, b.arg.name))
        elif isinstance(a, Gamma) and isinstance(b, Gamma):
            metrics.append((a.index.name, b.index.name))
        elif isinstance(a, Gamma) and isinstance(b, Slash):
            if not isinstance(b.arg, Vector):
                raise TypeError("Optimized trace currently requires Slash(Vector).")
            stubs.append((a.index.name, b.arg.name))
        elif isinstance(a, Slash) and isinstance(b, Gamma):
            if not isinstance(a.arg, Vector):
                raise TypeError("Optimized trace currently requires Slash(Vector).")
            stubs.append((b.index.name, a.arg.name))
        else:
            raise TypeError("Optimized trace supports Gamma and Slash only.")

    occurrences = Counter()
    adjacency = defaultdict(set)
    vectors_at = defaultdict(list)
    for a, b in metrics:
        occurrences[a] += 1
        occurrences[b] += 1
        adjacency[a].add(b)
        adjacency[b].add(a)
    for idx, v in stubs:
        occurrences[idx] += 1
        vectors_at[idx].append(v)
        adjacency[idx]

    bad = {k: v for k, v in occurrences.items() if v != 2}
    if bad:
        raise ValueError(f"Trace is not fully Lorentz contracted; index counts: {bad}")

    visited = set()
    for start in occurrences:
        if start in visited:
            continue
        stack = [start]
        nodes = set()
        while stack:
            u = stack.pop()
            if u in nodes:
                continue
            nodes.add(u)
            visited.add(u)
            stack.extend(adjacency[u] - nodes)
        vs = []
        for u in nodes:
            vs.extend(vectors_at[u])
        if len(vs) == 0:
            d_power += 1
        elif len(vs) == 2:
            sp_atoms.append(_sp_atom_name(vs[0], vs[1]))
        else:
            raise ValueError(f"Unsupported Lorentz component with {len(vs)} vector stubs.")

    return d_power, tuple(sorted(sp_atoms))


def _evaluate_clifford_pairing_scalar(word, pairs, Dsym):
    """Backward-compatible SymPy form of one Clifford pairing."""
    import sympy as sp
    d_power, atoms = _evaluate_clifford_pairing_key(word, pairs)
    out = Dsym**d_power
    for atom in atoms:
        out *= sp.Symbol(atom)
    return out


@lru_cache(maxsize=4096)
def _trace_word_fully_contracted_sympy(word, Dsym):
    """Evaluate one even Clifford word using monomial aggregation.

    Pairings that produce the same scalar-product monomial are combined with
    integer arithmetic before a SymPy expression is materialized.  This is
    substantially faster for finite-q projector traces, where many distinct
    scalar products occur.
    """
    import sympy as sp
    from collections import defaultdict

    n = len(word)
    if n % 2:
        return sp.Integer(0)
    if n == 0:
        return sp.Integer(4)

    coeffs = defaultdict(int)
    for sign, pairs in _pairing_patterns(n):
        key = _evaluate_clifford_pairing_key(word, pairs)
        coeffs[key] += sign

    terms = []
    for (d_power, atoms), coeff in coeffs.items():
        if coeff == 0:
            continue
        monomial = sp.Integer(4 * coeff) * Dsym**d_power
        for atom in atoms:
            monomial *= sp.Symbol(atom)
        terms.append(monomial)
    return sp.Add(*terms) if terms else sp.Integer(0)

def dirac_trace_fully_contracted_sympy(expr: QEDExpr, D_name="D"):
    """Fast arbitrary-length D-dimensional trace for fully contracted scalars.

    Unlike ``dirac_trace_ddim`` this routine does not materialize the huge
    intermediate metric expression.  It expands the Dirac polynomial into
    unique Clifford words, evaluates perfect pairings directly to scalar
    products, and returns a SymPy scalar expression.  This is intended for
    long projector traces such as the two-loop ordinary ladder.
    """
    import sympy as sp
    from collections import defaultdict

    Dsym=sp.Symbol(D_name)
    combined=defaultdict(lambda: sp.Integer(0))
    for coeff,word in _dirac_poly_terms(expr):
        combined[word] += coeff

    result=sp.Integer(0)
    cache={}
    for word,coeff in combined.items():
        coeff=sp.simplify(coeff)
        if coeff==0: continue
        n=len(word)
        if n%2: continue
        if word not in cache:
            cache[word] = _trace_word_fully_contracted_sympy(word, Dsym)
        result += coeff*cache[word]
    return sp.expand(result)
