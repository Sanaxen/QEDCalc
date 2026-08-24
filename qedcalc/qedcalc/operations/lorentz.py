from qedcalc.core.expression import (
    QEDExpr, Add, Product, NCProduct, ScalarMul, Metric, Gamma,
    VectorComponent, ScalarProduct, Index
)


def _replace_index(expr: QEDExpr, old: str, new: Index):
    if isinstance(expr, Gamma) and expr.index.name == old:
        return Gamma(Index(new.name, new.position))
    if isinstance(expr, VectorComponent) and expr.index.name == old:
        return VectorComponent(expr.vector, Index(new.name, new.position))
    if isinstance(expr, Add):
        return Add(*(_replace_index(t, old, new) for t in expr.terms))
    if isinstance(expr, Product):
        return Product(*(_replace_index(f, old, new) for f in expr.factors))
    if isinstance(expr, NCProduct):
        return NCProduct(*(_replace_index(f, old, new) for f in expr.factors))
    if isinstance(expr, ScalarMul):
        return ScalarMul(expr.coeff, _replace_index(expr.expr, old, new))
    return expr


def contract_metric(expr: QEDExpr):
    """Contract metric tensors against gamma/vector indices in a product.

    The first implementation targets the structures needed by the one-loop
    QED vertex numerator, e.g. gamma^sigma g_{rho sigma} -> gamma_rho.
    """
    if isinstance(expr, Add):
        return Add(*(contract_metric(t) for t in expr.terms))
    if isinstance(expr, ScalarMul):
        return ScalarMul(expr.coeff, contract_metric(expr.expr))
    if not isinstance(expr, (Product, NCProduct)):
        return expr

    cls = type(expr)
    factors = list(expr.factors)
    changed = True
    while changed:
        changed = False
        for mi, m in enumerate(factors):
            if not isinstance(m, Metric):
                continue
            # Try contracting the right metric index first, then the left.
            for metric_name, replacement in (
                (m.right.name, Index(m.left.name, "down")),
                (m.left.name, Index(m.right.name, "down")),
            ):
                for fi, f in enumerate(factors):
                    if fi == mi:
                        continue
                    if isinstance(f, Gamma) and f.index.name == metric_name and f.index.position == "up":
                        factors[fi] = Gamma(replacement)
                        factors.pop(mi)
                        changed = True
                        break
                    if isinstance(f, VectorComponent) and f.index.name == metric_name and f.index.position == "up":
                        factors[fi] = VectorComponent(f.vector, replacement)
                        factors.pop(mi)
                        changed = True
                        break
                if changed:
                    break
            if changed:
                break

    if len(factors) == 1:
        return factors[0]
    return cls(*factors)

# --- v0.25: fully contracted Lorentz scalar network ---
def contract_fully_scalar_lorentz(expr: QEDExpr, D_name="D") -> QEDExpr:
    """Contract a fully scalar Lorentz tensor network to scalar products.

    Designed for closed Dirac/projector traces.  Each dummy Lorentz index must
    occur exactly twice in a monomial.  Metric tensors connect index labels;
    two vector stubs in a connected component become a scalar product, while a
    closed metric-only component contributes D.

    The routine intentionally rejects free or multiply-used indices instead of
    guessing tensor structure.
    """
    from collections import Counter, defaultdict
    import sympy as sp
    from qedcalc.core.expression import Symbol, Vector, Add, Product, ScalarMul, Metric, VectorComponent, ScalarProduct, Power
    from qedcalc.operations.simplify import simplify_expression, expand_commutative

    Dsym = sp.Symbol(D_name)

    def monomial(term):
        coeff = sp.Integer(1)
        scalar = []
        metrics = []
        comps = []

        def absorb(f):
            nonlocal coeff
            if isinstance(f, Product):
                for x in f.factors:
                    absorb(x)
            elif isinstance(f, ScalarMul):
                coeff *= sp.sympify(f.coeff)
                absorb(f.expr)
            elif isinstance(f, Symbol):
                try:
                    coeff *= sp.sympify(f.name)
                except Exception:
                    scalar.append(f)
            elif isinstance(f, Metric):
                metrics.append(f)
            elif isinstance(f, VectorComponent):
                comps.append(f)
            elif isinstance(f, (ScalarProduct, Power)):
                scalar.append(f)
            else:
                scalar.append(f)

        absorb(term)

        occurrences = Counter()
        adjacency = defaultdict(set)
        vectors_at = defaultdict(list)
        for m in metrics:
            a, b = m.left.name, m.right.name
            occurrences[a] += 1; occurrences[b] += 1
            adjacency[a].add(b); adjacency[b].add(a)
        for c in comps:
            a = c.index.name
            occurrences[a] += 1
            vectors_at[a].append(c.vector)
            adjacency[a]  # ensure key

        bad = {k:v for k,v in occurrences.items() if v != 2}
        if bad:
            raise ValueError(f"Lorentz network is not fully contracted; index occurrence counts: {bad}")

        visited = set()
        for start in occurrences:
            if start in visited:
                continue
            stack=[start]; nodes=set()
            while stack:
                u=stack.pop()
                if u in nodes: continue
                nodes.add(u); visited.add(u)
                stack.extend(adjacency[u] - nodes)
            vlist=[]
            for u in nodes:
                vlist.extend(vectors_at[u])
            if len(vlist) == 0:
                # One closed index network = one free Lorentz sum.
                coeff *= Dsym
            elif len(vlist) == 2:
                scalar.append(ScalarProduct(vlist[0], vlist[1]))
            else:
                raise ValueError(
                    f"Unsupported fully contracted Lorentz component with {len(vlist)} vector stubs."
                )

        base = Symbol("1") if not scalar else (scalar[0] if len(scalar)==1 else Product(*scalar))
        return simplify_expression(base if coeff == 1 else ScalarMul(sp.simplify(coeff), base))

    expr = expand_commutative(expr)
    if isinstance(expr, Add):
        return expand_commutative(simplify_expression(Add(*(monomial(t) for t in expr.terms))))
    return expand_commutative(simplify_expression(monomial(expr)))
