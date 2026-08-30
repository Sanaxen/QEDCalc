from __future__ import annotations

from dataclasses import dataclass
import sympy as sp

from qedcalc.core.expression import (
    QEDExpr, Symbol, Vector, ScalarProduct, Add, Product, ScalarMul, Power,
    Fraction, VectorLinearCombination, LoopMomentumSet, MultiLoopCompletedSquare
)
from qedcalc.operations.scalar_sympy import to_sympy_scalar, from_sympy_scalar
from qedcalc.operations.simplify import simplify_expression


def declare_loop_momenta(symbol_table, names):
    """Declare loop momenta after validating them against [Vector]."""
    if isinstance(names, str):
        names = (names,)
    names = tuple(names)
    if not names:
        raise ValueError("At least one loop momentum must be declared.")
    if len(set(names)) != len(names):
        raise ValueError("Loop momentum names must be unique.")
    for name in names:
        symbol_table.require(name, "Vector", context="loop momentum declaration")
    return LoopMomentumSet(tuple(Vector(name) for name in names))


def _sp_key(a, b):
    a, b = sorted((a, b))
    return f"SP__{a}__{b}"


def _sympy_to_qed(expr, reverse):
    return simplify_expression(from_sympy_scalar(sp.factor(sp.cancel(expr)), reverse))


def _collect_external_vectors(atom_map, loops):
    loopset = set(loops)
    external = set()
    for key in atom_map:
        if not key.startswith("SP__"):
            continue
        _, a, b = key.split("__", 2)
        if a in loopset and b not in loopset:
            external.add(b)
        if b in loopset and a not in loopset:
            external.add(a)
    return sorted(external)


def _atom(atom_map, key):
    return atom_map.get(key, sp.Symbol(key))


def complete_multiloop_square(expr: QEDExpr, loops=("k", "l")) -> MultiLoopCompletedSquare:
    """Complete a general Lorentz-scalar quadratic form in several loop momenta.

    The input is interpreted as
        K^T M K + 2 K.B + C.

    Mixed products may be written as k.l or l.k.  M is symmetrized.  All
    matrix inversion is exact SymPy algebra on scalar coefficients only.
    """
    loops = tuple(loops)
    if not loops:
        raise ValueError("At least one loop momentum is required.")

    atom_map = {}
    sexpr, reverse = to_sympy_scalar(expr, atom_map)
    sexpr = sp.expand(sexpr)
    n = len(loops)

    # Build the symmetric quadratic matrix M.
    M = sp.zeros(n, n)
    loop_atoms = set()
    for i, a in enumerate(loops):
        aa = _atom(atom_map, _sp_key(a, a))
        M[i, i] = sp.expand(sexpr).coeff(aa)
        loop_atoms.add(aa)
        for j in range(i + 1, n):
            b = loops[j]
            ab = _atom(atom_map, _sp_key(a, b))
            ba = _atom(atom_map, _sp_key(b, a))
            if ab == ba:
                coeff = sp.expand(sexpr).coeff(ab)
            else:
                coeff = sp.expand(sexpr).coeff(ab) + sp.expand(sexpr).coeff(ba)
            M[i, j] = M[j, i] = sp.simplify(coeff / 2)
            loop_atoms.update((ab, ba))

    if M.det() == 0:
        raise ValueError("The loop-momentum quadratic matrix is singular and cannot be square-completed.")

    external = _collect_external_vectors(atom_map, loops)

    # B_i is a Lorentz vector linear combination.  Store coefficients by
    # external vector name; the expression contains 2 K.B.
    B = []
    linear_atoms = set()
    for a in loops:
        row = {}
        for v in external:
            av = _atom(atom_map, _sp_key(a, v))
            va = _atom(atom_map, _sp_key(v, a))
            if av == va:
                coeff = sp.expand(sexpr).coeff(av)
            else:
                coeff = sp.expand(sexpr).coeff(av) + sp.expand(sexpr).coeff(va)
            if coeff != 0:
                row[v] = sp.simplify(coeff / 2)
            linear_atoms.update((av, va))
        B.append(row)

    # Constant C: remove every scalar-product atom containing a loop momentum.
    subs_zero = {}
    for key, atom in atom_map.items():
        if not key.startswith("SP__"):
            continue
        _, a, b = key.split("__", 2)
        if a in loops or b in loops:
            subs_zero[atom] = 0
    C = sp.simplify(sexpr.subs(subs_zero))

    Minv = sp.simplify(M.inv())

    # S = M^{-1} B, with each B_i itself a vector linear combination.
    shift_rows = []
    for i in range(n):
        terms = []
        for v in external:
            coeff = sp.Integer(0)
            for j in range(n):
                coeff += Minv[i, j] * B[j].get(v, 0)
            coeff = sp.factor(sp.simplify(coeff))
            if coeff != 0:
                terms.append((_sympy_to_qed(coeff, reverse), Vector(v)))
        shift_rows.append(VectorLinearCombination(tuple(terms)))

    # B^T M^{-1} B is a scalar assembled from external scalar products.
    btminvb = sp.Integer(0)
    for i in range(n):
        for j in range(n):
            if Minv[i, j] == 0:
                continue
            for va, ca in B[i].items():
                for vb, cb in B[j].items():
                    key = _sp_key(va, vb)
                    sp_atom = _atom(atom_map, key)
                    if key not in atom_map:
                        atom_map[key] = sp_atom
                        reverse[sp_atom] = ScalarProduct(Vector(va), Vector(vb))
                    btminvb += ca * Minv[i, j] * cb * sp_atom
    remainder_sym = sp.factor(sp.simplify(C - btminvb))

    matrix_qed = tuple(
        tuple(_sympy_to_qed(M[i, j], reverse) for j in range(n))
        for i in range(n)
    )
    remainder = _sympy_to_qed(remainder_sym, reverse)
    return MultiLoopCompletedSquare(
        tuple(Vector(x) for x in loops),
        matrix_qed,
        tuple(shift_rows),
        remainder,
    )


def shifted_multiloop_denominator(completed: MultiLoopCompletedSquare, new_loops=None):
    """Return the quadratic form after K -> L - S.

    Only the pure shifted quadratic term plus the remainder is returned.
    """
    if not isinstance(completed, MultiLoopCompletedSquare):
        raise TypeError("shifted_multiloop_denominator expects MultiLoopCompletedSquare.")
    n = len(completed.loops)
    if new_loops is None:
        new_loops = tuple(f"ell{i+1}" for i in range(n))
    if len(new_loops) != n:
        raise ValueError("new_loops must have the same length as the declared loop set.")
    L = [Vector(x) for x in new_loops]
    terms = []
    for i in range(n):
        for j in range(n):
            coeff = completed.matrix[i][j]
            if isinstance(coeff, Symbol) and coeff.name == "0":
                continue
            # Sum all matrix entries.  This naturally represents K^T M K.
            terms.append(Product(coeff, ScalarProduct(L[i], L[j])))
    terms.append(completed.remainder)
    from qedcalc.operations.scalar_sympy import simplify_scalar_with_sympy
    return simplify_scalar_with_sympy(simplify_expression(Add(*terms)), "simplify")


def shift_multiloop_momenta_in_numerator(expr: QEDExpr, completed: MultiLoopCompletedSquare, new_loops=None):
    """Apply all multi-loop square-completion shifts to a numerator.

    For the convention
        (K + S)^T M (K + S) + R,
    define L = K + S, so each old loop momentum is replaced by
        K_i = L_i - S_i.

    Supported structures include Slash(K_i), vector components, and scalar
    products.  The substitution is simultaneous, so k/l cross terms are not
    corrupted by sequential replacement.
    """
    from qedcalc.core.expression import Slash, VectorComponent, Fraction, NCProduct
    from qedcalc.operations.simplify import expand_commutative, simplify_expression

    if not isinstance(completed, MultiLoopCompletedSquare):
        raise TypeError("shift_multiloop_momenta_in_numerator expects MultiLoopCompletedSquare.")
    n = len(completed.loops)
    if new_loops is None:
        new_loops = tuple(f"ell{i+1}" for i in range(n))
    if len(new_loops) != n:
        raise ValueError("new_loops must have the same length as the completed loop set.")

    expansions = {}
    for old, new, shift in zip(completed.loops, new_loops, completed.shifts):
        # old = new - shift
        terms = [(Symbol("1"), Vector(new))]
        for coeff, vec in shift.terms:
            terms.append((ScalarMul(-1, coeff), vec))
        expansions[old.name] = tuple(terms)

    def vec_terms(v):
        if isinstance(v, Vector) and v.name in expansions:
            return expansions[v.name]
        return ((Symbol("1"), v),)

    def coeff_product(*cs):
        return simplify_expression(Product(*cs))

    def rec(e):
        if isinstance(e, Slash) and isinstance(e.arg, Vector) and e.arg.name in expansions:
            pieces = []
            for c, v in expansions[e.arg.name]:
                pieces.append(Product(c, Slash(v)))
            return simplify_expression(Add(*pieces))
        if isinstance(e, VectorComponent) and isinstance(e.vector, Vector) and e.vector.name in expansions:
            pieces = []
            for c, v in expansions[e.vector.name]:
                pieces.append(Product(c, VectorComponent(v, e.index)))
            return simplify_expression(Add(*pieces))
        if isinstance(e, ScalarProduct):
            left_terms = vec_terms(e.left)
            right_terms = vec_terms(e.right)
            if left_terms != ((Symbol("1"), e.left),) or right_terms != ((Symbol("1"), e.right),):
                pieces = []
                for ca, va in left_terms:
                    for cb, vb in right_terms:
                        pieces.append(Product(coeff_product(ca, cb), ScalarProduct(va, vb)))
                return expand_commutative(Add(*pieces))
            return e
        if isinstance(e, Add):
            return Add(*(rec(t) for t in e.terms))
        if isinstance(e, Product):
            return Product(*(rec(f) for f in e.factors))
        if isinstance(e, NCProduct):
            return NCProduct(*(rec(f) for f in e.factors))
        if isinstance(e, ScalarMul):
            return ScalarMul(e.coeff, rec(e.expr))
        if isinstance(e, Fraction):
            return Fraction(rec(e.numerator), rec(e.denominator))
        if isinstance(e, Power):
            return Power(rec(e.base), e.exponent)
        return e

    return simplify_expression(rec(expr))


def symmetric_multiloop_tensor(components, completed: MultiLoopCompletedSquare,
                               dimension=4, quadratic_symbol="Q"):
    r"""Reduce an even mixed tensor for a multi-loop quadratic form.

    Let the shifted denominator depend only on

        Q = L^T M L

    for ``n`` loop vectors in ``D`` Lorentz dimensions.  For an even product
    of components ``L_i^mu`` the isotropic average in the full ``n*D``
    dimensional integration space is

        Q^r / [N(N+2)...(N+2r-2)]
        * sum_pairings prod[(M^{-1})_ij g^{mu nu}],

    where ``N = n*D`` and ``r = rank/2``.

    ``components`` is a sequence of ``(loop_name, Index)`` pairs.  The routine
    is intended after simultaneous square completion, when the remaining
    integrand depends on loop momenta only through Q.  Odd ranks are rejected.
    """
    from qedcalc.core.expression import Index, Metric, Add, Product, Power, ScalarMul
    from qedcalc.operations.loop import _pairings

    if not isinstance(completed, MultiLoopCompletedSquare):
        raise TypeError("symmetric_multiloop_tensor expects MultiLoopCompletedSquare.")
    comps = tuple(components)
    if not comps or len(comps) % 2:
        raise ValueError("components must contain a non-empty even number of tensor components.")

    loop_names = tuple(v.name for v in completed.loops)
    loop_index = {name: i for i, name in enumerate(loop_names)}
    normalized = []
    for loop_name, index in comps:
        if loop_name not in loop_index:
            raise ValueError(f"Unknown loop momentum '{loop_name}'.")
        if not isinstance(index, Index):
            raise TypeError("Each tensor component index must be a qedcalc Index.")
        normalized.append((loop_name, index))

    # Convert M to exact SymPy scalars, then invert.
    atom_map = {}
    matrix_rows = []
    reverse = {}
    for row in completed.matrix:
        srow = []
        for item in row:
            sval, rev = to_sympy_scalar(item, atom_map)
            reverse.update(rev)
            srow.append(sval)
        matrix_rows.append(srow)
    M = sp.Matrix(matrix_rows)
    Minv = sp.simplify(M.inv())

    D = sp.sympify(dimension)
    nloops = len(loop_names)
    N = sp.simplify(nloops * D)
    rank_half = len(normalized) // 2
    denom = sp.Integer(1)
    for j in range(rank_half):
        denom *= N + 2*j
    overall = sp.simplify(1 / denom)

    pairing_terms = []
    positions = tuple(range(len(normalized)))
    for pairing in _pairings(positions):
        factors = []
        coeff = sp.Integer(1)
        for a_pos, b_pos in pairing:
            la, ia = normalized[a_pos]
            lb, ib = normalized[b_pos]
            coeff *= Minv[loop_index[la], loop_index[lb]]
            factors.append(Metric(ia, ib))
        coeff_qed = _sympy_to_qed(sp.simplify(overall * coeff), reverse)
        metric_product = factors[0] if len(factors) == 1 else Product(*factors)
        if isinstance(coeff_qed, Symbol) and coeff_qed.name == "1":
            term = metric_product
        elif isinstance(coeff_qed, Symbol) and coeff_qed.name == "-1":
            term = ScalarMul(-1, metric_product)
        else:
            term = Product(coeff_qed, metric_product)
        pairing_terms.append(term)

    metric_sum = pairing_terms[0] if len(pairing_terms) == 1 else Add(*pairing_terms)
    qsym = Symbol(str(quadratic_symbol))
    moment = qsym if rank_half == 1 else Power(qsym, rank_half)
    return simplify_expression(Product(moment, metric_sum))
