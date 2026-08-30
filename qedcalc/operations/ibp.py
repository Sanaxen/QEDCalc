from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Iterable, Mapping, Sequence
import json
from pathlib import Path
import sympy as sp
from sympy.polys.polyfuncs import rational_interpolate


def sp_name(a: str, b: str) -> str:
    """Canonical SymPy symbol name for a Lorentz scalar product."""
    x, y = sorted((str(a), str(b)))
    return f"SP__{x}__{y}"


def sp_atom(a: str, b: str) -> sp.Symbol:
    return sp.Symbol(sp_name(a, b))


@dataclass(frozen=True, order=True)
class IntegralIndex:
    """Generic integral-family exponent tuple."""
    powers: tuple[int, ...]

    def __init__(self, powers: Sequence[int]):
        object.__setattr__(self, "powers", tuple(int(x) for x in powers))

    def shifted(self, shifts: Mapping[int, int]) -> "IntegralIndex":
        out = list(self.powers)
        for i, delta in shifts.items():
            out[i] += int(delta)
        return IntegralIndex(out)

    def as_tuple(self):
        return self.powers


@dataclass(frozen=True)
class IBPEquation:
    """Sparse linear relation sum_i coeff_i J(index_i) = 0."""
    terms: Mapping[IntegralIndex, sp.Expr]
    label: str = ""

    def simplified(self) -> "IBPEquation":
        out = {}
        for idx, coeff in self.terms.items():
            c = sp.factor(sp.simplify(coeff))
            if c != 0:
                out[idx] = c
        return IBPEquation(out, self.label)

    def coefficient(self, index: IntegralIndex | Sequence[int]):
        idx = index if isinstance(index, IntegralIndex) else IntegralIndex(index)
        return self.terms.get(idx, sp.Integer(0))

    def as_expr(self, integral_function=None):
        if integral_function is None:
            integral_function = lambda idx: sp.Symbol("J(" + ",".join(map(str, idx.powers)) + ")")
        return sp.Add(*(c * integral_function(i) for i, c in self.terms.items()))


@dataclass(frozen=True)
class IntegralFamily:
    """Quadratic multi-loop integral family suitable for IBP generation.

    ``denominator_exprs`` are SymPy expressions written in SP__a__b atoms and
    invariant symbols. ``scalar_product_rules`` reduce all scalar products that
    can occur after differentiating a denominator back to the denominator
    symbols and external invariants.
    """
    name: str
    denominator_names: tuple[str, ...]
    denominator_exprs: tuple[sp.Expr, ...]
    loop_momenta: tuple[str, ...]
    external_momenta: tuple[str, ...]
    scalar_product_rules: Mapping[sp.Symbol, sp.Expr]
    dimension_symbol: sp.Expr = sp.Symbol("D")

    def __post_init__(self):
        if len(self.denominator_names) != len(self.denominator_exprs):
            raise ValueError("denominator_names and denominator_exprs must have the same length.")
        if len(set(self.denominator_names)) != len(self.denominator_names):
            raise ValueError("Denominator names must be unique.")

    @property
    def denominator_symbols(self):
        return tuple(sp.Symbol(x) for x in self.denominator_names)

    @property
    def size(self):
        return len(self.denominator_names)

    def validate_index(self, index: IntegralIndex | Sequence[int]) -> IntegralIndex:
        idx = index if isinstance(index, IntegralIndex) else IntegralIndex(index)
        if len(idx.powers) != self.size:
            raise ValueError(f"Integral index length {len(idx.powers)} does not match family size {self.size}.")
        return idx


def _differentiate_scalar_product_atom(atom: sp.Symbol, loop: str, vector: str) -> sp.Expr:
    """Return v·∂_loop (a·b) for a scalar-product atom."""
    name = str(atom)
    if not name.startswith("SP__"):
        return sp.Integer(0)
    _, a, b = name.split("__", 2)
    out = sp.Integer(0)
    if a == loop:
        out += sp_atom(b, vector)
    if b == loop:
        out += sp_atom(a, vector)
    return out


def directional_derivative(expr: sp.Expr, loop: str, vector: str) -> sp.Expr:
    """Compute v_mu ∂/∂loop_mu for an expression built from scalar products."""
    expr = sp.sympify(expr)
    out = sp.Integer(0)
    for atom in expr.free_symbols:
        if str(atom).startswith("SP__"):
            d_atom = _differentiate_scalar_product_atom(atom, loop, vector)
            if d_atom != 0:
                out += sp.diff(expr, atom) * d_atom
    return sp.expand(out)


def reduce_directional_derivative(family: IntegralFamily, denominator_index: int,
                                  loop: str, vector: str) -> sp.Expr:
    """Differentiate one denominator and reduce the result to family variables."""
    raw = directional_derivative(family.denominator_exprs[denominator_index], loop, vector)
    reduced = sp.expand(raw.subs(family.scalar_product_rules))
    leftovers = [s for s in reduced.free_symbols if str(s).startswith("SP__")]
    if leftovers:
        raise ValueError(
            f"Unreduced scalar products in IBP derivative of {family.denominator_names[denominator_index]}: {leftovers}"
        )
    return sp.factor(reduced)


def _linear_denominator_polynomial(expr: sp.Expr, denominator_symbols: Sequence[sp.Symbol]):
    """Return terms (coefficient, denominator power tuple) of a polynomial numerator."""
    expr = sp.expand(sp.sympify(expr))
    poly = sp.Poly(expr, *denominator_symbols)
    out = []
    for monom, coeff in poly.terms():
        # For a quadratic denominator family an IBP derivative should be at most
        # linear in the denominator variables after scalar-product reduction.
        out.append((sp.factor(coeff), tuple(int(x) for x in monom)))
    return out


def generate_ibp_equation(family: IntegralFamily, index: IntegralIndex | Sequence[int],
                          derivative_loop: str, vector: str) -> IBPEquation:
    r"""Generate one IBP identity.

    Implements

        0 = ∫ d^{LD}k ∂/∂k_i^mu [ v^mu / Π_a D_a^{n_a} ].

    The divergence term is D only when v is the same loop momentum as the
    differentiated loop; external vectors and other loop vectors have zero
    divergence with respect to k_i.
    """
    idx = family.validate_index(index)
    if derivative_loop not in family.loop_momenta:
        raise ValueError(f"Unknown derivative loop momentum '{derivative_loop}'.")
    allowed_vectors = set(family.loop_momenta) | set(family.external_momenta)
    if vector not in allowed_vectors:
        raise ValueError(f"Unknown IBP vector '{vector}'.")

    terms: dict[IntegralIndex, sp.Expr] = {}
    if vector == derivative_loop:
        terms[idx] = family.dimension_symbol

    dsymbols = family.denominator_symbols
    for a, n_a in enumerate(idx.powers):
        if n_a == 0:
            continue
        deriv = reduce_directional_derivative(family, a, derivative_loop, vector)
        for coeff, monom in _linear_denominator_polynomial(deriv, dsymbols):
            # From -n_a (v·∂D_a) D_a^(-n_a-1) Π_{b!=a}D_b^(-n_b).
            # A numerator Π_j D_j^{p_j} lowers the corresponding denominator powers.
            shifts = {a: 1}
            for j, power in enumerate(monom):
                if power:
                    shifts[j] = shifts.get(j, 0) - power
            target = idx.shifted(shifts)
            terms[target] = terms.get(target, 0) - sp.Integer(n_a) * coeff

    return IBPEquation(terms, f"d/d{derivative_loop} · {vector}").simplified()


def generate_ibp_system(family: IntegralFamily, seeds: Iterable[IntegralIndex | Sequence[int]],
                        vectors: Sequence[str] | None = None) -> tuple[IBPEquation, ...]:
    """Generate all requested loop-derivative/vector IBPs for a seed set."""
    if vectors is None:
        vectors = family.loop_momenta + family.external_momenta
    equations = []
    for seed in seeds:
        for loop in family.loop_momenta:
            for vector in vectors:
                equations.append(generate_ibp_equation(family, seed, loop, vector))
    return tuple(equations)


def default_laporta_rank(index: IntegralIndex):
    """A deterministic 'harder first' ordering suitable for small Laporta systems.

    Higher total positive denominator power is harder; irreducible numerator
    powers (negative indices) are also harder.  Lexicographic powers break ties.
    """
    positive = sum(max(n, 0) for n in index.powers)
    numerator = sum(max(-n, 0) for n in index.powers)
    active = sum(1 for n in index.powers if n != 0)
    return (positive + numerator, numerator, active, index.powers)


@dataclass(frozen=True)
class ReductionRule:
    lhs: IntegralIndex
    rhs: Mapping[IntegralIndex, sp.Expr]

    def as_expr(self):
        return sp.Add(*(c * sp.Symbol("J(" + ",".join(map(str, i.powers)) + ")") for i, c in self.rhs.items()))


def laporta_eliminate(equations: Sequence[IBPEquation], rank=default_laporta_rank,
                      protected: Iterable[IntegralIndex | Sequence[int]] = ()) -> tuple[ReductionRule, ...]:
    """Perform sparse symbolic elimination on a finite IBP equation set.

    This is intentionally the finite-system core, not yet an automatic seed
    expander.  The highest-ranked non-protected integral in each equation is
    solved for and substituted into the remaining equations/rules.
    """
    protected_set = {p if isinstance(p, IntegralIndex) else IntegralIndex(p) for p in protected}
    rows = [dict(eq.simplified().terms) for eq in equations if eq.simplified().terms]
    rules: list[ReductionRule] = []

    def substitute_rule(row, lhs, rhs):
        if lhs not in row:
            return row
        factor = row.pop(lhs)
        for idx, coeff in rhs.items():
            row[idx] = sp.factor(sp.simplify(row.get(idx, 0) + factor * coeff))
            if row[idx] == 0:
                row.pop(idx, None)
        return row

    while True:
        candidates = set()
        for row in rows:
            candidates.update(i for i in row if i not in protected_set)
        if not candidates:
            break
        pivot = max(candidates, key=rank)
        pivot_row_idx = next((r for r, row in enumerate(rows) if pivot in row), None)
        if pivot_row_idx is None:
            break
        row = rows.pop(pivot_row_idx)
        c = sp.factor(row.pop(pivot))
        if c == 0:
            continue
        rhs = {idx: sp.factor(-coeff / c) for idx, coeff in row.items() if coeff != 0}

        # Substitute previously generated rules into the new RHS.
        for old in rules:
            if old.lhs in rhs:
                fac = rhs.pop(old.lhs)
                for idx, coeff in old.rhs.items():
                    rhs[idx] = sp.factor(sp.simplify(rhs.get(idx, 0) + fac * coeff))
                    if rhs[idx] == 0:
                        rhs.pop(idx, None)

        # Eliminate the pivot from all remaining rows.
        rows = [substitute_rule(r, pivot, rhs) for r in rows]

        # Keep existing rules triangular as well.
        new_rules = []
        for old in rules:
            old_rhs = dict(old.rhs)
            if pivot in old_rhs:
                fac = old_rhs.pop(pivot)
                for idx, coeff in rhs.items():
                    old_rhs[idx] = sp.factor(sp.simplify(old_rhs.get(idx, 0) + fac * coeff))
                    if old_rhs[idx] == 0:
                        old_rhs.pop(idx, None)
            new_rules.append(ReductionRule(old.lhs, old_rhs))
        rules = new_rules
        rules.append(ReductionRule(pivot, rhs))

        rows = [{i: sp.factor(sp.simplify(c)) for i, c in r.items() if sp.simplify(c) != 0} for r in rows]
        rows = [r for r in rows if r]

    return tuple(sorted(rules, key=lambda r: rank(r.lhs), reverse=True))


def _fast_coeff(expr: sp.Expr) -> sp.Expr:
    """Cheaper rational-function normalization for large sparse IBP systems."""
    expr = sp.sympify(expr)
    if expr == 0:
        return sp.Integer(0)
    return sp.cancel(expr)


def laporta_forward_eliminate(equations: Sequence[IBPEquation], rank=None,
                              protected: Iterable[IntegralIndex | Sequence[int]] = (),
                              family: IntegralFamily | None = None,
                              prune_scaleless: bool = True) -> tuple[ReductionRule, ...]:
    """Sparse forward Laporta elimination intended for medium-size systems.

    Unlike :func:`laporta_eliminate`, this routine never substitutes a newly
    solved pivot back into every previously processed row.  Rows are reduced
    only against already-known harder pivots.  Because each pivot is chosen as
    the highest-ranked integral left in its row, the resulting rules are still
    acyclic and can be recursively reduced by :func:`reduce_integral`.
    """
    if rank is None:
        rank = sector_rank
    protected_set = {p if isinstance(p, IntegralIndex) else IntegralIndex(p) for p in protected}
    eqs = tuple(equations)
    if family is not None and prune_scaleless:
        eqs = prune_zero_sectors(family, eqs)

    rows = [dict(eq.terms) for eq in eqs if eq.terms]
    rows.sort(key=lambda row: max((rank(i) for i in row), default=(-1,)), reverse=True)
    rule_map: dict[IntegralIndex, dict[IntegralIndex, sp.Expr]] = {}

    for row in rows:
        # Eliminate pivots already solved.  Highest-ranked entries are tried first.
        while True:
            solved = [i for i in row if i in rule_map]
            if not solved:
                break
            lhs = max(solved, key=rank)
            fac = row.pop(lhs)
            if fac == 0:
                continue
            for idx, coeff in rule_map[lhs].items():
                val = row.get(idx, 0) + fac * coeff
                val = _fast_coeff(val)
                if val == 0:
                    row.pop(idx, None)
                else:
                    row[idx] = val

        candidates = [i for i in row if i not in protected_set]
        if not candidates:
            continue
        pivot = max(candidates, key=rank)
        c = row.pop(pivot)
        if c == 0:
            continue
        rhs = {}
        for idx, coeff in row.items():
            val = _fast_coeff(-coeff / c)
            if val != 0:
                rhs[idx] = val
        rule_map[pivot] = rhs

    rules = [ReductionRule(lhs, rhs) for lhs, rhs in rule_map.items()]
    return tuple(sorted(rules, key=lambda r: rank(r.lhs), reverse=True))


def master_candidates(equations: Sequence[IBPEquation], rules: Sequence[ReductionRule],
                      family: IntegralFamily | None = None,
                      prune_scaleless: bool = True) -> tuple[IntegralIndex, ...]:
    """Return unsolved integrals appearing in a finite IBP system."""
    eqs = tuple(equations)
    if family is not None and prune_scaleless:
        eqs = prune_zero_sectors(family, eqs)
    ints = set()
    for eq in eqs:
        ints.update(eq.terms)
    solved = {r.lhs for r in rules}
    return tuple(sorted(ints - solved, key=sector_rank))


def reduce_integral(index: IntegralIndex | Sequence[int], rules: Sequence[ReductionRule]) -> Mapping[IntegralIndex, sp.Expr]:
    """Recursively apply triangular reduction rules to one integral."""
    idx = index if isinstance(index, IntegralIndex) else IntegralIndex(index)
    rule_map = {r.lhs: r.rhs for r in rules}

    @lru_cache(maxsize=None)
    def rec(i: IntegralIndex):
        if i not in rule_map:
            return {i: sp.Integer(1)}
        out: dict[IntegralIndex, sp.Expr] = {}
        for j, c in rule_map[i].items():
            sub = rec(j)
            for k, v in sub.items():
                out[k] = sp.factor(sp.simplify(out.get(k, 0) + c * v))
                if out[k] == 0:
                    out.pop(k, None)
        return out

    return rec(idx)



@dataclass(frozen=True)
class IntegralSymmetry:
    """Permutation symmetry of an integral-family denominator basis.

    ``permutation[i]`` gives the source denominator whose exponent becomes
    slot ``i`` after the symmetry transformation.  Unit-Jacobian graph
    automorphisms therefore act only by permuting integral powers.
    """
    name: str
    permutation: tuple[int, ...]

    def __init__(self, name: str, permutation: Sequence[int]):
        perm = tuple(int(i) for i in permutation)
        if sorted(perm) != list(range(len(perm))):
            raise ValueError("IntegralSymmetry permutation must be a permutation of 0..N-1.")
        object.__setattr__(self, "name", str(name))
        object.__setattr__(self, "permutation", perm)

    def apply(self, index: IntegralIndex | Sequence[int]) -> IntegralIndex:
        idx = index if isinstance(index, IntegralIndex) else IntegralIndex(index)
        if len(idx.powers) != len(self.permutation):
            raise ValueError("Integral index length does not match symmetry size.")
        return IntegralIndex(tuple(idx.powers[j] for j in self.permutation))


def close_symmetry_group(symmetries: Sequence[IntegralSymmetry], size: int | None = None) -> tuple[IntegralSymmetry, ...]:
    """Return the finite permutation group generated by ``symmetries``."""
    if size is None:
        if not symmetries:
            raise ValueError("size is required when no symmetry generators are supplied.")
        size = len(symmetries[0].permutation)
    size = int(size)
    identity = tuple(range(size))
    generators = [s.permutation for s in symmetries]
    for g in generators:
        if len(g) != size:
            raise ValueError("All symmetry generators must have the same size.")
    group = {identity}
    frontier = [identity]
    while frontier:
        a = frontier.pop()
        for b in generators:
            # apply b first, then a: transformed[i] = original[a[b[i]]]
            c = tuple(a[b[i]] for i in range(size))
            if c not in group:
                group.add(c)
                frontier.append(c)
    return tuple(IntegralSymmetry(f"g{n}", g) for n, g in enumerate(sorted(group)))


def canonicalize_integral(index: IntegralIndex | Sequence[int], symmetries: Sequence[IntegralSymmetry]) -> IntegralIndex:
    """Map an integral to the lexicographically smallest member of its symmetry orbit."""
    idx = index if isinstance(index, IntegralIndex) else IntegralIndex(index)
    if not symmetries:
        return idx
    orbit = [s.apply(idx) for s in symmetries]
    return min(orbit, key=lambda x: x.powers)


def canonicalize_seed_set(seeds: Iterable[IntegralIndex | Sequence[int]],
                          symmetries: Sequence[IntegralSymmetry]) -> tuple[IntegralIndex, ...]:
    """Canonicalize and deduplicate a seed collection under family symmetries."""
    out = {canonicalize_integral(seed, symmetries) for seed in seeds}
    return tuple(sorted(out, key=lambda x: (sector_rank(x), x.powers)))


def canonicalize_ibp_equation(equation: IBPEquation, symmetries: Sequence[IntegralSymmetry]) -> IBPEquation:
    """Canonicalize every integral in an IBP row and combine orbit-equivalent terms."""
    if not symmetries:
        return equation
    terms: dict[IntegralIndex, sp.Expr] = {}
    for idx, coeff in equation.terms.items():
        cidx = canonicalize_integral(idx, symmetries)
        terms[cidx] = _fast_coeff(terms.get(cidx, 0) + coeff)
        if terms[cidx] == 0:
            terms.pop(cidx, None)
    return IBPEquation(terms, equation.label)


def canonicalize_ibp_system(equations: Sequence[IBPEquation],
                            symmetries: Sequence[IntegralSymmetry]) -> tuple[IBPEquation, ...]:
    """Canonicalize an IBP system under denominator-permutation symmetries."""
    return tuple(canonicalize_ibp_equation(eq, symmetries) for eq in equations)

def integral_latex(index: IntegralIndex | Sequence[int], symbol="J") -> str:
    idx = index if isinstance(index, IntegralIndex) else IntegralIndex(index)
    return symbol + r"\left(" + ",".join(str(n) for n in idx.powers) + r"\right)"


def ibp_equation_latex(equation: IBPEquation, symbol="J") -> str:
    """Render a sparse IBP equation as compact LaTeX."""
    pieces = []
    for idx, coeff in sorted(equation.terms.items(), key=lambda kv: kv[0].powers):
        c = sp.factor(coeff)
        term = integral_latex(idx, symbol)
        if c == 1:
            body = term
        elif c == -1:
            body = "-" + term
        else:
            body = sp.latex(c) + r"\," + term
        pieces.append(body)
    if not pieces:
        return "0=0"
    expr = pieces[0]
    for body in pieces[1:]:
        if body.startswith("-"):
            expr += body
        else:
            expr += "+" + body
    return expr + "=0"


def reduction_rule_latex(rule: ReductionRule, symbol="J") -> str:
    rhs_pieces = []
    for idx, coeff in sorted(rule.rhs.items(), key=lambda kv: kv[0].powers):
        c = sp.factor(coeff)
        term = integral_latex(idx, symbol)
        if c == 1:
            body = term
        elif c == -1:
            body = "-" + term
        else:
            body = sp.latex(c) + r"\," + term
        rhs_pieces.append(body)
    rhs = "0" if not rhs_pieces else rhs_pieces[0]
    for body in rhs_pieces[1:]:
        rhs += body if body.startswith("-") else "+" + body
    return integral_latex(rule.lhs, symbol) + "=" + rhs


def sector_signature(index: IntegralIndex | Sequence[int]) -> tuple[int, ...]:
    """Return 1/0 flags indicating which denominators have positive powers."""
    idx = index if isinstance(index, IntegralIndex) else IntegralIndex(index)
    return tuple(1 if n > 0 else 0 for n in idx.powers)


def sector_id(index: IntegralIndex | Sequence[int]) -> int:
    """Binary sector identifier; denominator 0 is the least-significant bit."""
    sig = sector_signature(index)
    return sum(bit << i for i, bit in enumerate(sig))


def sector_rank(index: IntegralIndex | Sequence[int]):
    """Laporta sector-aware complexity rank (harder integrals rank higher).

    The sector itself is ordered primarily by the number of positive
    denominators.  Within a sector, raised propagator powers and irreducible
    numerator degree determine the complexity.
    """
    idx = index if isinstance(index, IntegralIndex) else IntegralIndex(index)
    sig = sector_signature(idx)
    active = sum(sig)
    dots = sum(max(n - 1, 0) for n in idx.powers)
    numerator = sum(max(-n, 0) for n in idx.powers)
    positive = sum(max(n, 0) for n in idx.powers)
    return (active, dots + numerator, numerator, positive, sector_id(idx), idx.powers)


def _denominator_has_external_scale(family: IntegralFamily, denominator_index: int) -> bool:
    """Conservative test: does a denominator explicitly involve an external momentum?"""
    expr = family.denominator_exprs[denominator_index]
    externals = set(family.external_momenta)
    for atom in expr.free_symbols:
        name = str(atom)
        if not name.startswith("SP__"):
            # A non-SP symbol in a raw denominator is an explicit mass/invariant scale.
            return True
        _, a, b = name.split("__", 2)
        if a in externals or b in externals:
            return True
    return False


def is_scaleless_zero_sector(family: IntegralFamily, index_or_signature) -> bool:
    """Return True only for sectors that are provably scale-free by structure.

    This is deliberately conservative.  A sector is declared zero when it has
    at least one positive denominator and every active denominator depends only
    on loop scalar products, with no explicit mass/invariant symbol and no
    external momentum.  Such a homogeneous massless vacuum integral is
    scaleless in dimensional regularization.
    """
    if isinstance(index_or_signature, IntegralIndex):
        sig = sector_signature(index_or_signature)
    else:
        vals = tuple(index_or_signature)
        if len(vals) != family.size:
            raise ValueError("Sector signature length does not match family size.")
        # Accept either a 0/1 signature or an ordinary power tuple.
        sig = tuple(1 if n > 0 else 0 for n in vals)
    active = [i for i, bit in enumerate(sig) if bit]
    if not active:
        return True
    return all(not _denominator_has_external_scale(family, i) for i in active)


def zero_sector_ids(family: IntegralFamily) -> tuple[int, ...]:
    """Enumerate structurally scaleless sectors for a modest-size family."""
    if family.size > 20:
        raise ValueError("zero_sector_ids exhaustive enumeration is limited to 20 denominators.")
    out = []
    for sid in range(1 << family.size):
        sig = tuple((sid >> i) & 1 for i in range(family.size))
        if is_scaleless_zero_sector(family, sig):
            out.append(sid)
    return tuple(out)


def prune_zero_sectors(family: IntegralFamily, equations: Sequence[IBPEquation]) -> tuple[IBPEquation, ...]:
    """Set structurally scaleless-sector integrals to zero and drop empty rows."""
    out = []
    for eq in equations:
        terms = {idx: coeff for idx, coeff in eq.terms.items()
                 if not is_scaleless_zero_sector(family, idx)}
        if terms:
            out.append(IBPEquation(terms, eq.label).simplified())
    return tuple(out)


def bounded_seed_domain(index: IntegralIndex | Sequence[int], max_extra_degree: int = 1,
                        include_numerator_slots: bool = True) -> tuple[IntegralIndex, ...]:
    """Generate a bounded Laporta seed domain around one reference integral.

    Each positive denominator may be raised by non-negative shifts; each
    non-positive slot may receive numerator powers.  The sum of all added
    powers is bounded by ``max_extra_degree``.  Degree 1 reproduces the old
    first-neighbor set, while degree 2 provides the next closure layer without
    constructing the full Cartesian cube.
    """
    idx = index if isinstance(index, IntegralIndex) else IntegralIndex(index)
    max_extra_degree = int(max_extra_degree)
    if max_extra_degree < 0:
        raise ValueError("max_extra_degree must be non-negative.")
    seeds = {idx}

    moves = []
    for i, n in enumerate(idx.powers):
        if n > 0:
            moves.append((i, +1))
        elif include_numerator_slots:
            moves.append((i, -1))

    def rec(current, start, remaining):
        if remaining == 0:
            seeds.add(current)
            return
        for j in range(start, len(moves)):
            i, delta = moves[j]
            rec(current.shifted({i: delta}), j, remaining - 1)

    for degree in range(1, max_extra_degree + 1):
        rec(idx, 0, degree)
    return tuple(sorted(seeds, key=lambda x: (sector_rank(x), x.powers)))


def laporta_eliminate_sectorwise(equations: Sequence[IBPEquation], family: IntegralFamily | None = None,
                                  protected: Iterable[IntegralIndex | Sequence[int]] = (),
                                  prune_scaleless: bool = True) -> tuple[ReductionRule, ...]:
    """Sector-aware wrapper around the finite sparse Laporta core."""
    eqs = tuple(equations)
    if family is not None and prune_scaleless:
        eqs = prune_zero_sectors(family, eqs)
    return laporta_eliminate(eqs, rank=sector_rank, protected=protected)


def first_neighbor_seeds(index: IntegralIndex | Sequence[int], include_numerator_slots=True) -> tuple[IntegralIndex, ...]:
    """Generate the degree-1 bounded Laporta neighborhood."""
    return bounded_seed_domain(index, max_extra_degree=1,
                               include_numerator_slots=include_numerator_slots)


def specialize_ibp_system(equations: Sequence[IBPEquation], substitutions: Mapping[sp.Symbol, sp.Expr],
                          drop_empty: bool = True) -> tuple[IBPEquation, ...]:
    """Evaluate IBP coefficients at an exact rational/symbolic probe point.

    This is intended for fast generic-rank diagnostics and finite-field-style
    development checks.  Integral indices are untouched; only coefficients are
    specialized.  It must not be confused with a symbolic reduction valid for
    arbitrary kinematics.
    """
    subs = {sp.sympify(k): sp.sympify(v) for k, v in substitutions.items()}
    out = []
    for eq in equations:
        terms = {}
        for idx, coeff in eq.terms.items():
            value = _fast_coeff(sp.sympify(coeff).subs(subs))
            if value != 0:
                terms[idx] = value
        if terms or not drop_empty:
            out.append(IBPEquation(terms, eq.label))
    return tuple(out)


def symmetry_reduction_stats(indices: Iterable[IntegralIndex | Sequence[int]],
                             symmetries: Sequence[IntegralSymmetry]) -> dict[str, int]:
    """Return raw/canonical counts for a collection of integral indices."""
    raw = {i if isinstance(i, IntegralIndex) else IntegralIndex(i) for i in indices}
    canonical = {canonicalize_integral(i, symmetries) for i in raw}
    return {"raw": len(raw), "canonical": len(canonical)}


# --- v0.30: target-aware closure diagnostics ---
@dataclass(frozen=True)
class ClosureRound:
    """One target-aware seed-closure diagnostic round."""
    round_index: int
    seed_count: int
    equation_count: int
    integral_count: int
    pivot_counts: tuple[int, ...]
    unsolved_targets_by_probe: tuple[tuple[IntegralIndex, ...], ...]
    stable_across_probes: bool
    target_count: int

    @property
    def unsolved_targets(self) -> tuple[IntegralIndex, ...]:
        if not self.unsolved_targets_by_probe:
            return ()
        return self.unsolved_targets_by_probe[0]

    @property
    def solved_target_count(self) -> int:
        return self.target_count - len(self.unsolved_targets)


@dataclass(frozen=True)
class ClosureResult:
    """Result of iterative target-aware generic-point closure diagnostics."""
    targets: tuple[IntegralIndex, ...]
    rounds: tuple[ClosureRound, ...]
    final_seeds: tuple[IntegralIndex, ...]
    status: str

    @property
    def stable_candidates(self) -> tuple[IntegralIndex, ...]:
        if not self.rounds or self.status != "stable_candidates":
            return ()
        return self.rounds[-1].unsolved_targets

    @property
    def all_targets_solved(self) -> bool:
        return self.status == "solved"


def _canonical_index_set(indices, symmetries=()):
    return {
        canonicalize_integral(i if isinstance(i, IntegralIndex) else IntegralIndex(i), symmetries)
        for i in indices
    }


def target_aware_closure(
    family: IntegralFamily,
    targets: Iterable[IntegralIndex | Sequence[int]],
    probe_points: Sequence[Mapping[sp.Symbol, sp.Expr]],
    symmetries: Sequence[IntegralSymmetry] = (),
    vectors: Sequence[str] | None = None,
    neighborhood_degree: int = 1,
    max_rounds: int = 4,
) -> ClosureResult:
    """Iteratively expand only around unreduced target integrals.

    This is a diagnostic closure driver, not yet a proof of a physical master
    basis.  Each round builds symbolic IBPs for the current seed set, applies
    family symmetries and conservative zero-sector pruning, then measures the
    reduction at several exact-rational generic probe points.  A candidate set
    is called stable only when every probe gives the same unreduced targets and
    expanding their bounded neighborhood adds no new canonical seed.
    """
    if not probe_points:
        raise ValueError("At least one exact-rational probe point is required.")
    if max_rounds < 1:
        raise ValueError("max_rounds must be at least 1.")
    neighborhood_degree = int(neighborhood_degree)
    if neighborhood_degree < 1:
        raise ValueError("neighborhood_degree must be at least 1.")

    ctargets = _canonical_index_set(targets, symmetries)
    if not ctargets:
        raise ValueError("At least one target integral is required.")
    seeds = set(ctargets)
    rounds = []
    status = "max_rounds"

    for rno in range(int(max_rounds)):
        cseeds = canonicalize_seed_set(seeds, symmetries)
        eqs = generate_ibp_system(family, cseeds, vectors=vectors)
        if symmetries:
            eqs = canonicalize_ibp_system(eqs, symmetries)
        eqs = prune_zero_sectors(family, eqs)
        integrals = {idx for eq in eqs for idx in eq.terms}

        pivot_counts = []
        unsolved_sets = []
        for point in probe_points:
            peqs = specialize_ibp_system(eqs, point)
            rules = laporta_forward_eliminate(peqs, family=None, prune_scaleless=False)
            solved = {rule.lhs for rule in rules}
            unsolved = tuple(sorted(ctargets - solved, key=lambda x: x.powers))
            pivot_counts.append(len(rules))
            unsolved_sets.append(unsolved)

        stable_probes = all(u == unsolved_sets[0] for u in unsolved_sets[1:])
        round_info = ClosureRound(
            round_index=rno,
            seed_count=len(cseeds),
            equation_count=len(eqs),
            integral_count=len(integrals),
            pivot_counts=tuple(pivot_counts),
            unsolved_targets_by_probe=tuple(unsolved_sets),
            stable_across_probes=stable_probes,
            target_count=len(ctargets),
        )
        rounds.append(round_info)

        if stable_probes and not unsolved_sets[0]:
            status = "solved"
            break

        expand_targets = set().union(*(set(u) for u in unsolved_sets))
        expanded = set(seeds)
        for idx in expand_targets:
            expanded.update(bounded_seed_domain(idx, neighborhood_degree))
        expanded = _canonical_index_set(expanded, symmetries)

        if stable_probes and expanded == set(cseeds):
            status = "stable_candidates"
            seeds = expanded
            break
        seeds = expanded

    return ClosureResult(
        targets=tuple(sorted(ctargets, key=lambda x: x.powers)),
        rounds=tuple(rounds),
        final_seeds=tuple(sorted(_canonical_index_set(seeds, symmetries), key=lambda x: x.powers)),
        status=status,
    )

# --- v0.31: exact multivariate rational-function reconstruction ---
@dataclass(frozen=True)
class RationalReconstructionResult:
    """Exact rational-function reconstruction with training/holdout metadata."""
    expression: sp.Expr
    numerator_degree: int
    denominator_degree: int
    variables: tuple[sp.Symbol, ...]
    training_count: int
    holdout_count: int


def total_degree_monomials(variables: Sequence[sp.Symbol], max_degree: int) -> tuple[sp.Expr, ...]:
    """Return all monomials of total degree <= max_degree in deterministic order."""
    vars_ = tuple(sp.sympify(v) for v in variables)
    max_degree = int(max_degree)
    if max_degree < 0:
        raise ValueError("max_degree must be non-negative.")
    if not vars_:
        return (sp.Integer(1),)
    out = []
    def rec(pos, remaining, exponents):
        if pos == len(vars_) - 1:
            for e in range(remaining + 1):
                exps = exponents + [e]
                mon = sp.Integer(1)
                for v, p in zip(vars_, exps):
                    mon *= v**p
                out.append(mon)
            return
        for e in range(remaining + 1):
            rec(pos + 1, remaining - e, exponents + [e])
    # Generate exact total-degree shells to avoid duplicates.
    shell_out = []
    for degree in range(max_degree + 1):
        current = []
        def shell(pos, remaining, exponents):
            if pos == len(vars_) - 1:
                exps = exponents + [remaining]
                mon = sp.Integer(1)
                for v, p in zip(vars_, exps):
                    mon *= v**p
                current.append(mon)
                return
            for e in range(remaining + 1):
                shell(pos + 1, remaining - e, exponents + [e])
        shell(0, degree, [])
        shell_out.extend(current)
    return tuple(shell_out)


def _normalize_reconstructed_rational(expr: sp.Expr, variables: Sequence[sp.Symbol]) -> sp.Expr:
    expr = sp.cancel(sp.sympify(expr))
    num, den = sp.fraction(expr)
    # Normalize a rational numeric denominator/content when possible.
    num = sp.expand(num)
    den = sp.expand(den)
    if den.could_extract_minus_sign():
        num, den = -num, -den
    return sp.factor(sp.cancel(num / den))


def reconstruct_rational_function(
    samples: Sequence[tuple[Sequence[sp.Expr], sp.Expr]],
    variables: Sequence[sp.Symbol],
    max_numerator_degree: int = 3,
    max_denominator_degree: int = 3,
    holdout_samples: Sequence[tuple[Sequence[sp.Expr], sp.Expr]] = (),
) -> RationalReconstructionResult:
    """Reconstruct an exact multivariate rational function from exact samples.

    For each degree pair this solves the homogeneous linear system

        P(x) - f(x) Q(x) = 0

    with total-degree polynomial ansaetze for P and Q.  The first unique
    nullspace solution that also passes all holdout samples is returned.
    Samples should be exact rationals/algebraic SymPy values; floating-point
    samples are intentionally rejected.
    """
    vars_ = tuple(sp.sympify(v) for v in variables)
    if not vars_:
        raise ValueError("At least one reconstruction variable is required.")
    train = tuple(samples)
    hold = tuple(holdout_samples)
    if not train:
        raise ValueError("At least one training sample is required.")

    def normalize_sample(sample):
        coords, value = sample
        coords = tuple(sp.sympify(c) for c in coords)
        value = sp.sympify(value)
        if len(coords) != len(vars_):
            raise ValueError("Sample coordinate count does not match variable count.")
        if any(c.has(sp.Float) for c in coords) or value.has(sp.Float):
            raise ValueError("Rational reconstruction requires exact, non-Float samples.")
        return coords, value

    train = tuple(normalize_sample(s) for s in train)
    hold = tuple(normalize_sample(s) for s in hold)

    for pdeg in range(int(max_numerator_degree) + 1):
        pmon = total_degree_monomials(vars_, pdeg)
        for qdeg in range(int(max_denominator_degree) + 1):
            qmon = total_degree_monomials(vars_, qdeg)
            rows = []
            for coords, value in train:
                subs = dict(zip(vars_, coords))
                rows.append(
                    [sp.sympify(m).subs(subs) for m in pmon]
                    + [-value * sp.sympify(m).subs(subs) for m in qmon]
                )
            nullspace = sp.Matrix(rows).nullspace()
            if len(nullspace) != 1:
                continue
            vec = nullspace[0]
            P = sp.Add(*(vec[i] * pmon[i] for i in range(len(pmon))))
            Q = sp.Add(*(vec[len(pmon) + j] * qmon[j] for j in range(len(qmon))))
            if sp.simplify(Q) == 0:
                continue
            expr = _normalize_reconstructed_rational(P / Q, vars_)
            valid = True
            for coords, value in train + hold:
                subs = dict(zip(vars_, coords))
                den_value = sp.denom(sp.cancel(expr)).subs(subs)
                if sp.simplify(den_value) == 0 or sp.simplify(expr.subs(subs) - value) != 0:
                    valid = False
                    break
            if valid:
                return RationalReconstructionResult(
                    expression=expr,
                    numerator_degree=pdeg,
                    denominator_degree=qdeg,
                    variables=vars_,
                    training_count=len(train),
                    holdout_count=len(hold),
                )
    raise ValueError(
        "No unique rational reconstruction passed validation within the requested degree bounds."
    )


def reconstruct_reduction_coefficients(
    reductions: Sequence[Mapping[IntegralIndex, sp.Expr]],
    sample_points: Sequence[Mapping[sp.Symbol, sp.Expr]],
    masters: Sequence[IntegralIndex | Sequence[int]],
    variables: Sequence[sp.Symbol],
    holdout_reductions: Sequence[Mapping[IntegralIndex, sp.Expr]] = (),
    holdout_points: Sequence[Mapping[sp.Symbol, sp.Expr]] = (),
    max_numerator_degree: int = 3,
    max_denominator_degree: int = 3,
) -> Mapping[IntegralIndex, RationalReconstructionResult]:
    """Reconstruct all nonzero master coefficients of a sampled reduction."""
    if len(reductions) != len(sample_points):
        raise ValueError("reductions and sample_points must have the same length.")
    if len(holdout_reductions) != len(holdout_points):
        raise ValueError("holdout_reductions and holdout_points must have the same length.")
    vars_ = tuple(sp.sympify(v) for v in variables)
    master_indices = tuple(m if isinstance(m, IntegralIndex) else IntegralIndex(m) for m in masters)
    out = {}
    for master in master_indices:
        train_samples = []
        for red, point in zip(reductions, sample_points):
            coords = tuple(sp.sympify(point[v]) for v in vars_)
            train_samples.append((coords, sp.sympify(red.get(master, 0))))
        hold_samples = []
        for red, point in zip(holdout_reductions, holdout_points):
            coords = tuple(sp.sympify(point[v]) for v in vars_)
            hold_samples.append((coords, sp.sympify(red.get(master, 0))))
        if all(value == 0 for _, value in train_samples + hold_samples):
            continue
        out[master] = reconstruct_rational_function(
            train_samples,
            vars_,
            max_numerator_degree=max_numerator_degree,
            max_denominator_degree=max_denominator_degree,
            holdout_samples=hold_samples,
        )
    return out


# --- v0.41: denominator-guided exact reconstruction ---
def infer_allowed_univariate_denominator(
    samples: Sequence[tuple[sp.Expr, sp.Expr]],
    variable: sp.Symbol,
    allowed_factors: Sequence[sp.Expr],
    max_numerator_degree: int | None = None,
) -> sp.Expr:
    """Infer the simplest denominator composed only of allowed linear factors.

    The samples must be exact and have distinct coordinates.  Numerator degrees
    are scanned upward.  The first rational interpolation whose denominator
    factorization contains only ``allowed_factors`` is returned, normalized to
    a monic polynomial.  This is useful when IBP structure already constrains
    possible singular factors (for example D-4, D-3, z, z-4).
    """
    var = sp.sympify(variable)
    data = tuple((sp.sympify(x), sp.sympify(y)) for x, y in samples)
    if not data:
        raise ValueError("At least one sample is required.")
    if len({x for x, _ in data}) != len(data):
        raise ValueError("Univariate sample coordinates must be distinct.")
    if any(x.has(sp.Float) or y.has(sp.Float) for x, y in data):
        raise ValueError("Exact reconstruction does not accept Float samples.")
    allowed = {sp.Poly(sp.sympify(f), var).monic().as_expr() for f in allowed_factors}
    max_degree = len(data) - 1 if max_numerator_degree is None else min(int(max_numerator_degree), len(data) - 1)

    def denominator_is_allowed(den: sp.Expr) -> bool:
        poly = sp.Poly(den, var)
        if poly.degree() <= 0:
            return True
        _, factors = sp.factor_list(poly.as_expr(), var)
        return all(sp.Poly(f, var).monic().as_expr() in allowed for f, _ in factors)

    for degree in range(max_degree + 1):
        expr = sp.cancel(rational_interpolate(data, degree, X=var))
        _, den = sp.fraction(expr)
        if not denominator_is_allowed(den):
            continue
        # Verify because the returned expression may simplify nontrivially.
        if all(sp.simplify(expr.subs(var, x) - y) == 0 for x, y in data):
            return sp.factor(sp.Poly(den, var).monic().as_expr())
    raise ValueError("No rational interpolation with the allowed denominator factors was found.")


def reconstruct_bivariate_with_known_denominator(
    grid_samples: Mapping[tuple[sp.Expr, sp.Expr], sp.Expr],
    x_values: Sequence[sp.Expr],
    y_values: Sequence[sp.Expr],
    variables: Sequence[sp.Symbol],
    denominator: sp.Expr,
    holdout_samples: Sequence[tuple[Sequence[sp.Expr], sp.Expr]] = (),
) -> RationalReconstructionResult:
    """Reconstruct P(x,y)/Q(x,y) on an exact Cartesian grid with known Q.

    The numerator is reconstructed by exact tensor-product polynomial
    interpolation.  Every grid point and every holdout point is then checked
    exactly.  This avoids high-dimensional homogeneous nullspace searches once
    the denominator factors are known from IBP singularity structure.
    """
    vars_ = tuple(sp.sympify(v) for v in variables)
    if len(vars_) != 2:
        raise ValueError("This reconstruction helper currently requires exactly two variables.")
    x, y = vars_
    xs = tuple(sp.sympify(v) for v in x_values)
    ys = tuple(sp.sympify(v) for v in y_values)
    if not xs or not ys:
        raise ValueError("Both grid axes must be non-empty.")
    if len(set(xs)) != len(xs) or len(set(ys)) != len(ys):
        raise ValueError("Grid coordinates must be distinct on each axis.")
    Q = sp.sympify(denominator)
    values = {(sp.sympify(a), sp.sympify(b)): sp.sympify(v) for (a, b), v in grid_samples.items()}
    expected = {(a, b) for a in xs for b in ys}
    if set(values) != expected:
        missing = expected.difference(values)
        extra = set(values).difference(expected)
        raise ValueError(f"grid_samples must cover the full Cartesian grid; missing={len(missing)}, extra={len(extra)}")
    if any(a.has(sp.Float) or b.has(sp.Float) or values[(a, b)].has(sp.Float) for a, b in expected):
        raise ValueError("Exact reconstruction does not accept Float samples.")
    for a, b in expected:
        if sp.simplify(Q.subs({x: a, y: b})) == 0:
            raise ValueError("Known denominator vanishes on a reconstruction grid point.")

    # First interpolate in x for every fixed y.
    x_polys: list[tuple[sp.Expr, sp.Expr]] = []
    for b in ys:
        data = []
        for a in xs:
            numerator_value = sp.cancel(values[(a, b)] * Q.subs({x: a, y: b}))
            data.append((a, numerator_value))
        x_polys.append((b, sp.expand(sp.interpolate(data, x))))

    max_x_degree = max((sp.Poly(p, x).degree() if p != 0 else -1) for _, p in x_polys)
    P = sp.Integer(0)
    for degree in range(max_x_degree + 1):
        y_data = []
        for b, px in x_polys:
            y_data.append((b, sp.Poly(px, x).coeff_monomial(x**degree)))
        P += sp.expand(sp.interpolate(y_data, y)) * x**degree
    expr = _normalize_reconstructed_rational(P / Q, vars_)

    normalized_holdout = []
    for coords, value in holdout_samples:
        coords = tuple(sp.sympify(c) for c in coords)
        value = sp.sympify(value)
        if len(coords) != 2:
            raise ValueError("Holdout coordinate count must be two.")
        if any(c.has(sp.Float) for c in coords) or value.has(sp.Float):
            raise ValueError("Exact reconstruction does not accept Float holdouts.")
        normalized_holdout.append((coords, value))

    for a, b in expected:
        if sp.simplify(expr.subs({x: a, y: b}) - values[(a, b)]) != 0:
            raise ValueError("Reconstructed expression failed an exact grid validation point.")
    for coords, value in normalized_holdout:
        subs = {x: coords[0], y: coords[1]}
        if sp.simplify(sp.denom(sp.cancel(expr)).subs(subs)) == 0:
            raise ValueError("Reconstructed denominator vanishes on a holdout point.")
        if sp.simplify(expr.subs(subs) - value) != 0:
            raise ValueError("Reconstructed expression failed an exact holdout validation point.")

    num, den = sp.fraction(sp.cancel(expr))
    num_degree = sp.Poly(num, x, y).total_degree() if num != 0 else 0
    den_degree = sp.Poly(den, x, y).total_degree() if den != 0 else 0
    return RationalReconstructionResult(
        expression=expr,
        numerator_degree=int(num_degree),
        denominator_degree=int(den_degree),
        variables=vars_,
        training_count=len(expected),
        holdout_count=len(normalized_holdout),
    )

# --- v0.32: batch reconstruction and residue diagnostics ---
@dataclass(frozen=True)
class TargetReconstructionStatus:
    """Status of one target in a sampled symbolic-reconstruction batch."""
    target: IntegralIndex
    status: str
    coefficients: Mapping[IntegralIndex, RationalReconstructionResult]
    residuals: tuple[IntegralIndex, ...] = ()
    message: str = ""


@dataclass(frozen=True)
class BatchReconstructionResult:
    """Batch result for target-to-candidate symbolic reconstruction."""
    targets: tuple[IntegralIndex, ...]
    masters: tuple[IntegralIndex, ...]
    entries: tuple[TargetReconstructionStatus, ...]
    training_points: tuple[Mapping[sp.Symbol, sp.Expr], ...]
    holdout_points: tuple[Mapping[sp.Symbol, sp.Expr], ...]

    @property
    def reconstructed(self) -> tuple[TargetReconstructionStatus, ...]:
        return tuple(e for e in self.entries if e.status == "reconstructed")

    @property
    def residual(self) -> tuple[TargetReconstructionStatus, ...]:
        return tuple(e for e in self.entries if e.status == "residual")

    @property
    def master_entries(self) -> tuple[TargetReconstructionStatus, ...]:
        return tuple(e for e in self.entries if e.status == "master")


def reduction_residuals(
    target: IntegralIndex | Sequence[int],
    rules: Sequence[ReductionRule],
    masters: Iterable[IntegralIndex | Sequence[int]],
) -> tuple[IntegralIndex, ...]:
    """Return non-master integrals left after recursively applying a reduction rule set."""
    tgt = target if isinstance(target, IntegralIndex) else IntegralIndex(target)
    master_set = {m if isinstance(m, IntegralIndex) else IntegralIndex(m) for m in masters}
    reduced = reduce_integral(tgt, rules)
    return tuple(sorted((set(reduced) - master_set), key=lambda x: x.powers))


def sampled_target_reductions(
    target: IntegralIndex | Sequence[int],
    rule_sets: Sequence[Sequence[ReductionRule]],
    masters: Iterable[IntegralIndex | Sequence[int]],
) -> tuple[tuple[Mapping[IntegralIndex, sp.Expr], ...], tuple[IntegralIndex, ...]]:
    """Reduce one target at every probe and report the union of non-master residues."""
    tgt = target if isinstance(target, IntegralIndex) else IntegralIndex(target)
    master_set = {m if isinstance(m, IntegralIndex) else IntegralIndex(m) for m in masters}
    reductions = []
    residual_union = set()
    for rules in rule_sets:
        red = reduce_integral(tgt, rules)
        reductions.append(red)
        residual_union.update(set(red) - master_set)
    return tuple(reductions), tuple(sorted(residual_union, key=lambda x: x.powers))


def batch_reconstruct_targets(
    targets: Iterable[IntegralIndex | Sequence[int]],
    masters: Iterable[IntegralIndex | Sequence[int]],
    rule_sets: Sequence[Sequence[ReductionRule]],
    sample_points: Sequence[Mapping[sp.Symbol, sp.Expr]],
    variables: Sequence[sp.Symbol],
    training_count: int,
    max_numerator_degree: int = 4,
    max_denominator_degree: int = 4,
) -> BatchReconstructionResult:
    """Reconstruct every target that closes on the supplied candidate basis.

    Targets that still contain non-master residues after recursive reduction are
    deliberately *not* interpolated.  This prevents a finite seed-domain
    artifact from being mistaken for a symbolic master-basis reduction.
    """
    targets_ = tuple(t if isinstance(t, IntegralIndex) else IntegralIndex(t) for t in targets)
    masters_ = tuple(m if isinstance(m, IntegralIndex) else IntegralIndex(m) for m in masters)
    master_set = set(masters_)
    points = tuple(sample_points)
    if len(rule_sets) != len(points):
        raise ValueError("rule_sets and sample_points must have the same length.")
    training_count = int(training_count)
    if training_count < 1 or training_count >= len(points):
        raise ValueError("training_count must leave at least one holdout point.")
    train_points = points[:training_count]
    hold_points = points[training_count:]
    entries = []
    for target in targets_:
        if target in master_set:
            entries.append(TargetReconstructionStatus(target, "master", {}, (), "Candidate-basis element."))
            continue
        # Cheap safety screen: one non-master residue at any exact probe is
        # already sufficient to forbid symbolic reconstruction.  Test the
        # first probe before expanding the target at every sample point.
        first_red = reduce_integral(target, rule_sets[0])
        first_residuals = tuple(sorted((set(first_red) - master_set), key=lambda x: x.powers))
        if first_residuals:
            entries.append(TargetReconstructionStatus(
                target, "residual", {}, first_residuals,
                "A non-candidate residue is present at the first exact probe; reconstruction skipped.",
            ))
            continue
        reductions, residuals = sampled_target_reductions(target, rule_sets, masters_)
        if residuals:
            entries.append(TargetReconstructionStatus(
                target, "residual", {}, residuals,
                "Reduction fails to close on the candidate basis at one or more exact probes; reconstruction skipped.",
            ))
            continue
        try:
            recon = reconstruct_reduction_coefficients(
                reductions[:training_count], train_points, masters_, variables,
                holdout_reductions=reductions[training_count:],
                holdout_points=hold_points,
                max_numerator_degree=max_numerator_degree,
                max_denominator_degree=max_denominator_degree,
            )
            entries.append(TargetReconstructionStatus(target, "reconstructed", recon))
        except ValueError as exc:
            entries.append(TargetReconstructionStatus(
                target, "failed_reconstruction", {}, (), str(exc),
            ))
    return BatchReconstructionResult(
        targets=targets_, masters=masters_, entries=tuple(entries),
        training_points=train_points, holdout_points=hold_points,
    )

# --- v0.33: residue-aware sector scheduler ---
@dataclass(frozen=True)
class ResidueImpact:
    """Impact metadata for one terminal non-candidate residue."""
    residue: IntegralIndex
    blocked_targets: tuple[IntegralIndex, ...]
    sector: int
    already_seeded: bool

    @property
    def impact(self) -> int:
        return len(self.blocked_targets)


@dataclass(frozen=True)
class ResidueSectorImpact:
    """Aggregated residue impact for one sector."""
    sector: int
    residues: tuple[IntegralIndex, ...]
    blocked_targets: tuple[IntegralIndex, ...]
    new_residues: tuple[IntegralIndex, ...]

    @property
    def impact(self) -> int:
        return len(self.blocked_targets)

    @property
    def new_seed_cost(self) -> int:
        return len(self.new_residues)

    @property
    def score(self) -> sp.Rational:
        # Existing-only sectors cannot enlarge the seed domain and therefore
        # receive zero scheduling priority.
        if self.new_seed_cost == 0:
            return sp.Rational(0)
        return sp.Rational(self.impact, self.new_seed_cost)


@dataclass(frozen=True)
class ResidueScheduleBatch:
    """One bounded scheduler proposal."""
    selected_sectors: tuple[ResidueSectorImpact, ...]
    new_seeds: tuple[IntegralIndex, ...]
    blocked_target_union: tuple[IntegralIndex, ...]

    @property
    def predicted_impact(self) -> int:
        return len(self.blocked_target_union)


def residue_impact_profile(
    targets: Iterable[IntegralIndex | Sequence[int]],
    rules: Sequence[ReductionRule],
    masters: Iterable[IntegralIndex | Sequence[int]],
    symmetries: Sequence[IntegralSymmetry] = (),
    existing_seeds: Iterable[IntegralIndex | Sequence[int]] = (),
) -> tuple[ResidueImpact, ...]:
    """Collect terminal non-master residues and the targets they obstruct.

    This function deliberately analyzes a *finished* probe reduction.  It does
    not generate new IBPs.  The result is therefore cheap enough to run after
    every closure round and can be used to decide which residue sector should
    receive the next bounded seed budget.
    """
    master_set = _canonical_index_set(masters, symmetries)
    seed_set = _canonical_index_set(existing_seeds, symmetries)
    target_map: dict[IntegralIndex, set[IntegralIndex]] = {}
    for target in targets:
        ct = canonicalize_integral(
            target if isinstance(target, IntegralIndex) else IntegralIndex(target),
            symmetries,
        )
        if ct in master_set:
            continue
        red = reduce_integral(ct, rules)
        for residue in set(red) - master_set:
            cr = canonicalize_integral(residue, symmetries)
            target_map.setdefault(cr, set()).add(ct)
    impacts = []
    for residue, blocked in target_map.items():
        impacts.append(ResidueImpact(
            residue=residue,
            blocked_targets=tuple(sorted(blocked, key=lambda x: x.powers)),
            sector=sector_id(residue),
            already_seeded=residue in seed_set,
        ))
    return tuple(sorted(
        impacts,
        key=lambda x: (-x.impact, x.already_seeded, sector_rank(x.residue), x.residue.powers),
    ))


def residue_sector_profile(impacts: Sequence[ResidueImpact]) -> tuple[ResidueSectorImpact, ...]:
    """Aggregate residue impacts by sector and rank sectors by impact/cost."""
    buckets: dict[int, dict[str, set[IntegralIndex]]] = {}
    for item in impacts:
        bucket = buckets.setdefault(item.sector, {"residues": set(), "targets": set(), "new": set()})
        bucket["residues"].add(item.residue)
        bucket["targets"].update(item.blocked_targets)
        if not item.already_seeded:
            bucket["new"].add(item.residue)
    sectors = []
    for sid, bucket in buckets.items():
        sectors.append(ResidueSectorImpact(
            sector=sid,
            residues=tuple(sorted(bucket["residues"], key=lambda x: x.powers)),
            blocked_targets=tuple(sorted(bucket["targets"], key=lambda x: x.powers)),
            new_residues=tuple(sorted(bucket["new"], key=lambda x: (sector_rank(x), x.powers))),
        ))
    return tuple(sorted(
        sectors,
        key=lambda x: (-x.score, -x.impact, x.new_seed_cost, x.sector),
    ))


def schedule_residue_sectors(
    sector_impacts: Sequence[ResidueSectorImpact],
    max_new_seeds: int = 2,
    max_sectors: int | None = None,
) -> ResidueScheduleBatch:
    """Choose a bounded residue-sector batch without expanding neighborhoods.

    The scheduler first inserts terminal residues themselves.  Neighborhood
    expansion is intentionally a later step and should be attempted only after
    direct residue seeds have been shown to improve the reduction.  This keeps
    the IBP growth controlled.
    """
    budget = int(max_new_seeds)
    if budget < 1:
        raise ValueError("max_new_seeds must be at least 1.")
    chosen = []
    new_seeds = []
    blocked = set()
    for sector in sector_impacts:
        if sector.new_seed_cost == 0:
            continue
        if max_sectors is not None and len(chosen) >= int(max_sectors):
            break
        available = budget - len(new_seeds)
        if available <= 0:
            break
        selected = sector.new_residues[:available]
        if not selected:
            continue
        chosen.append(sector)
        new_seeds.extend(selected)
        blocked.update(sector.blocked_targets)
    return ResidueScheduleBatch(
        selected_sectors=tuple(chosen),
        new_seeds=tuple(new_seeds),
        blocked_target_union=tuple(sorted(blocked, key=lambda x: x.powers)),
    )

# --- v0.34: incremental Laporta extension for bounded residue scheduling ---
def build_integral_reducer(rules: Sequence[ReductionRule]):
    """Return a persistent recursive reducer for one triangular rule set.

    Unlike :func:`reduce_integral`, the returned callable shares one rule map
    and one memoization cache across many integrals/IBP rows.  This is crucial
    for incremental Laporta extensions where hundreds of new rows are reduced
    through the same large baseline rule set.
    """
    rule_map = {r.lhs: r.rhs for r in rules}

    @lru_cache(maxsize=None)
    def rec(i: IntegralIndex):
        if i not in rule_map:
            return ((i, sp.Integer(1)),)
        out: dict[IntegralIndex, sp.Expr] = {}
        for j, c in rule_map[i].items():
            for k, v in rec(j):
                val = _fast_coeff(out.get(k, 0) + c * v)
                if val == 0:
                    out.pop(k, None)
                else:
                    out[k] = val
        return tuple(sorted(out.items(), key=lambda kv: kv[0].powers))

    def reduce_one(index: IntegralIndex | Sequence[int]) -> Mapping[IntegralIndex, sp.Expr]:
        idx = index if isinstance(index, IntegralIndex) else IntegralIndex(index)
        return dict(rec(idx))

    reduce_one.cache_info = rec.cache_info
    reduce_one.cache_clear = rec.cache_clear
    return reduce_one


def reduce_ibp_equation_with_rules(
    equation: IBPEquation,
    rules: Sequence[ReductionRule],
    reducer=None,
) -> IBPEquation:
    """Reduce one IBP row through an existing triangular rule set.

    ``reducer`` may be a persistent callable created by
    :func:`build_integral_reducer`; when omitted, a temporary reducer is built.
    """
    reducer = reducer or build_integral_reducer(rules)
    out: dict[IntegralIndex, sp.Expr] = {}
    for idx, coeff in equation.terms.items():
        red = reducer(idx)
        for ridx, rcoeff in red.items():
            val = _fast_coeff(out.get(ridx, 0) + coeff * rcoeff)
            if val == 0:
                out.pop(ridx, None)
            else:
                out[ridx] = val
    return IBPEquation(out, equation.label)


def extend_laporta_rules_incrementally(
    base_rules: Sequence[ReductionRule],
    new_equations: Sequence[IBPEquation],
    protected: Iterable[IntegralIndex | Sequence[int]] = (),
    rank=None,
) -> tuple[ReductionRule, ...]:
    """Extend an existing triangular Laporta system using only new IBP rows.

    The new rows are first reduced by ``base_rules``.  A forward sparse
    elimination is then performed only on the residual rows.  The returned rule
    set is ``base_rules + new_rules`` and remains acyclic because all previously
    solved pivots have been removed before new pivots are selected.
    """
    if rank is None:
        rank = sector_rank
    reduced_rows = []
    reducer = build_integral_reducer(base_rules)
    for eq in new_equations:
        req = reduce_ibp_equation_with_rules(eq, base_rules, reducer=reducer)
        if req.terms:
            reduced_rows.append(req)
    new_rules = laporta_forward_eliminate(
        reduced_rows,
        rank=rank,
        protected=protected,
        family=None,
        prune_scaleless=False,
    )
    # A residual row cannot pivot on an already solved lhs because those lhs
    # were recursively removed above.  Keep deterministic harder-first order.
    combined = list(base_rules) + list(new_rules)
    dedup: dict[IntegralIndex, ReductionRule] = {}
    for rule in combined:
        dedup.setdefault(rule.lhs, rule)
    return tuple(sorted(dedup.values(), key=lambda r: rank(r.lhs), reverse=True))

@dataclass(frozen=True)
class NeighborhoodSeedImpact:
    """Cheap phase-2 score for one neighborhood seed.

    The score is based only on whether newly generated pivots solve terminal
    residues already known to block targets.  Full target recursion is delayed
    until a small batch has been selected.
    """
    seed: IntegralIndex
    new_pivot_count: int
    hit_residues: tuple[IntegralIndex, ...]
    blocked_targets: tuple[IntegralIndex, ...]

    @property
    def direct_impact(self) -> int:
        return len(self.blocked_targets)


@dataclass(frozen=True)
class NeighborhoodSeedBatch:
    selected: tuple[NeighborhoodSeedImpact, ...]
    covered_targets: tuple[IntegralIndex, ...]


def evaluate_neighborhood_seed_candidates(
    family: IntegralFamily,
    candidates: Iterable[IntegralIndex | Sequence[int]],
    base_rules: Sequence[ReductionRule],
    residue_impacts: Sequence[ResidueImpact],
    probe_substitutions: Mapping[sp.Symbol, sp.Expr],
    symmetries: Sequence[IntegralSymmetry] = (),
    protected: Iterable[IntegralIndex | Sequence[int]] = (),
    vectors: Sequence[str] | None = None,
) -> tuple[NeighborhoodSeedImpact, ...]:
    """Evaluate candidate seeds without recursively reducing every target.

    Each candidate contributes only its own IBP rows.  Those rows are reduced
    through ``base_rules`` using :func:`extend_laporta_rules_incrementally`.
    A candidate is valuable when one of the newly solved pivots is a terminal
    residue already known to block corrected targets.
    """
    impact_map = {item.residue: set(item.blocked_targets) for item in residue_impacts}
    residue_set = set(impact_map)
    base_lhs = {r.lhs for r in base_rules}
    out = []
    seen = set()
    for raw_seed in candidates:
        seed = canonicalize_integral(
            raw_seed if isinstance(raw_seed, IntegralIndex) else IntegralIndex(raw_seed),
            symmetries,
        )
        if seed in seen:
            continue
        seen.add(seed)
        eqs = generate_ibp_system(family, (seed,), vectors=vectors)
        if symmetries:
            eqs = canonicalize_ibp_system(eqs, symmetries)
        eqs = prune_zero_sectors(family, eqs)
        peqs = specialize_ibp_system(eqs, probe_substitutions)
        extended = extend_laporta_rules_incrementally(
            base_rules, peqs, protected=protected,
        )
        new_lhs = {r.lhs for r in extended} - base_lhs
        hits = tuple(sorted(new_lhs & residue_set, key=lambda x: x.powers))
        blocked = set()
        for residue in hits:
            blocked.update(impact_map[residue])
        out.append(NeighborhoodSeedImpact(
            seed=seed,
            new_pivot_count=len(new_lhs),
            hit_residues=hits,
            blocked_targets=tuple(sorted(blocked, key=lambda x: x.powers)),
        ))
    return tuple(sorted(
        out,
        key=lambda x: (-x.direct_impact, -len(x.hit_residues), x.new_pivot_count, sector_rank(x.seed), x.seed.powers),
    ))


def schedule_neighborhood_seeds(
    impacts: Sequence[NeighborhoodSeedImpact],
    max_new_seeds: int = 3,
) -> NeighborhoodSeedBatch:
    """Greedily choose seeds by marginal coverage of currently blocked targets."""
    budget = int(max_new_seeds)
    if budget < 1:
        raise ValueError("max_new_seeds must be at least 1.")
    remaining = list(impacts)
    chosen = []
    covered = set()
    while remaining and len(chosen) < budget:
        best = None
        best_key = None
        for item in remaining:
            marginal = len(set(item.blocked_targets) - covered)
            key = (marginal, item.direct_impact, len(item.hit_residues), -item.new_pivot_count)
            if best_key is None or key > best_key:
                best_key = key
                best = item
        if best is None or best_key[0] <= 0:
            break
        chosen.append(best)
        covered.update(best.blocked_targets)
        remaining.remove(best)
    return NeighborhoodSeedBatch(
        selected=tuple(chosen),
        covered_targets=tuple(sorted(covered, key=lambda x: x.powers)),
    )

# --- v0.35: free-loop zero sectors and factorized lower subtopologies ---
@dataclass(frozen=True)
class FactorizedSubtopology:
    """Structural factorization of an L-loop sector into L one-denominator factors.

    This object is deliberately kinematic/convention neutral.  It records that
    an invertible linear loop-momentum transformation can assign one active
    rank-one quadratic denominator to each new loop variable.  Wick-rotation,
    i factors, (2*pi)^D normalization, and the actual one-loop master values
    remain the responsibility of the integral/convention layer.
    """
    index: IntegralIndex
    denominator_indices: tuple[int, ...]
    denominator_names: tuple[str, ...]
    powers: tuple[int, ...]
    loop_directions: tuple[tuple[sp.Expr, ...], ...]
    direction_determinant: sp.Expr

    @property
    def unimodular(self) -> bool:
        return sp.simplify(abs(self.direction_determinant) - 1) == 0


def _loop_quadratic_matrix(family: IntegralFamily, denominator_index: int) -> sp.Matrix:
    """Quadratic-form matrix in loop-momentum space for one denominator."""
    expr = sp.expand(family.denominator_exprs[int(denominator_index)])
    loops = family.loop_momenta
    n = len(loops)
    Q = sp.zeros(n, n)
    for i, a in enumerate(loops):
        Q[i, i] = sp.expand(expr).coeff(sp_atom(a, a))
        for j in range(i + 1, n):
            b = loops[j]
            c = sp.expand(expr).coeff(sp_atom(a, b))
            Q[i, j] = sp.simplify(c / 2)
            Q[j, i] = Q[i, j]
    return Q


def _primitive_direction_from_rank1_matrix(Q: sp.Matrix) -> tuple[sp.Expr, ...] | None:
    """Return a canonical primitive loop-direction vector for a rank-one Q."""
    if Q.rank() != 1:
        return None
    row = None
    pivot = None
    for i in range(Q.rows):
        for j in range(Q.cols):
            if Q[i, j] != 0:
                row = list(Q.row(i))
                pivot = row[j]
                break
        if row is not None:
            break
    ratios = [sp.cancel(x / pivot) for x in row]
    # For Q=c*a*a^T, a row normalized by one nonzero element is proportional
    # to a.  Convert rational directions to primitive integers when possible.
    if all(x.is_Rational for x in ratios):
        den_lcm = sp.ilcm(*[int(sp.denom(x)) for x in ratios]) if ratios else 1
        ints = [int(x * den_lcm) for x in ratios]
        nonzero = [abs(x) for x in ints if x]
        g = nonzero[0] if nonzero else 1
        for x in nonzero[1:]:
            g = sp.igcd(g, x)
        ints = [x // int(g) for x in ints]
        for x in ints:
            if x:
                if x < 0:
                    ints = [-y for y in ints]
                break
        return tuple(sp.Integer(x) for x in ints)
    # Symbolic fallback: normalize the first nonzero component to +1.
    first = next(x for x in ratios if x != 0)
    out = tuple(sp.cancel(x / first) for x in ratios)
    return out


def denominator_loop_direction(family: IntegralFamily, denominator_index: int) -> tuple[sp.Expr, ...] | None:
    """Return the rank-one loop direction carried by a propagator denominator."""
    return _primitive_direction_from_rank1_matrix(
        _loop_quadratic_matrix(family, denominator_index)
    )


def loop_denominator_rank(family: IntegralFamily, index: IntegralIndex | Sequence[int]) -> int:
    """Rank of loop directions constrained by positive denominators."""
    idx = family.validate_index(index)
    dirs = []
    for i, n in enumerate(idx.powers):
        if n <= 0:
            continue
        d = denominator_loop_direction(family, i)
        if d is None:
            # A higher-rank denominator constrains every direction in its row
            # space; include the quadratic-form rows directly.
            Q = _loop_quadratic_matrix(family, i)
            dirs.extend(tuple(row) for row in Q.tolist() if any(x != 0 for x in row))
        else:
            dirs.append(d)
    if not dirs:
        return 0
    return int(sp.Matrix(dirs).rank())


def has_free_scaleless_loop_direction(family: IntegralFamily, index: IntegralIndex | Sequence[int]) -> bool:
    """Detect a loop direction unconstrained by every positive denominator.

    A missing loop direction leaves an integration over a polynomial with no
    denominator scale.  In dimensional regularization that free integration is
    scaleless and vanishes.  This catches sectors such as a two-loop family
    containing only one massive electron denominator, which the older
    massless-vacuum-only zero-sector test could not see.
    """
    idx = family.validate_index(index)
    if not any(n > 0 for n in idx.powers):
        return True
    return loop_denominator_rank(family, idx) < len(family.loop_momenta)


def _linear_external_vectors(family: IntegralFamily, denominator_index: int):
    expr = sp.expand(family.denominator_exprs[int(denominator_index)])
    loops = family.loop_momenta
    out = {}
    for p in family.external_momenta:
        out[p] = sp.Matrix([expr.coeff(sp_atom(l, p)) for l in loops])
    return out


def factorized_one_denominator_per_loop(
    family: IntegralFamily,
    index: IntegralIndex | Sequence[int],
) -> FactorizedSubtopology | None:
    """Recognize sectors that factor into one one-denominator integral per loop.

    The test is intentionally strict: there must be exactly L positive
    denominators, no numerator slots, each denominator must carry a rank-one
    quadratic form, the L loop directions must be independent, and every
    external-linear term of a denominator must be parallel to that same loop
    direction.  Under these conditions an invertible linear change of loop
    variables separates the denominators completely.
    """
    idx = family.validate_index(index)
    if any(n < 0 for n in idx.powers):
        return None
    active = [i for i, n in enumerate(idx.powers) if n > 0]
    L = len(family.loop_momenta)
    if len(active) != L:
        return None
    directions = []
    for i in active:
        d = denominator_loop_direction(family, i)
        if d is None:
            return None
        dv = sp.Matrix(d)
        # Any external linear vector must be parallel to the denominator's
        # rank-one loop direction; otherwise it cannot be completed to one
        # shifted square in that single new loop variable.
        for b in _linear_external_vectors(family, i).values():
            if b == sp.zeros(L, 1):
                continue
            if sp.Matrix.hstack(dv, b).rank() > 1:
                return None
        directions.append(tuple(d))
    A = sp.Matrix(directions)
    if A.rank() != L:
        return None
    return FactorizedSubtopology(
        index=idx,
        denominator_indices=tuple(active),
        denominator_names=tuple(family.denominator_names[i] for i in active),
        powers=tuple(idx.powers[i] for i in active),
        loop_directions=tuple(directions),
        direction_determinant=sp.factor(A.det()),
    )


def is_scaleless_zero_sector_extended(family: IntegralFamily, index_or_signature) -> bool:
    """Extended zero-sector diagnostic including a free loop direction.

    The main Laporta pruning path keeps the older conservative criterion for
    performance and backward reproducibility.  Schedulers can opt into this
    stronger structural test when classifying terminal lower sectors.
    """
    if isinstance(index_or_signature, IntegralIndex):
        idx = family.validate_index(index_or_signature)
    else:
        vals = tuple(index_or_signature)
        if len(vals) != family.size:
            raise ValueError("Sector signature length does not match family size.")
        idx = IntegralIndex(tuple(1 if n > 0 else 0 for n in vals))
    if is_scaleless_zero_sector(family, idx):
        return True
    return has_free_scaleless_loop_direction(family, idx)

def factorized_euclidean_scalar_value(
    subtopology: FactorizedSubtopology,
    dimension=None,
    delta=None,
):
    r"""Return the convention-free Euclidean product for a factorized sector.

    All factors are assumed to share the supplied ``delta`` scale.  This is
    exactly the ordinary-ladder lower-sector situation for electron
    denominators E1..E4, where a shift turns each denominator into the same
    massive one-loop tadpole family.  Overall i factors, (2*pi)^D measures and
    Wick-rotation signs are intentionally not included.
    """
    from qedcalc.operations.integral import euclidean_scalar_loop_integral

    D = sp.Symbol("D") if dimension is None else sp.sympify(dimension)
    Delta = sp.Symbol("Delta", positive=True) if delta is None else sp.sympify(delta)
    jac = sp.Abs(sp.sympify(subtopology.direction_determinant)) ** (-D)
    value = jac
    for power in subtopology.powers:
        value *= euclidean_scalar_loop_integral(power, 0, D, Delta)
    return sp.simplify(value)

# --- v0.36: bounded local-irreducibility diagnostics for terminal residues ---
@dataclass(frozen=True)
class LocalIrreducibilityDiagnostic:
    """First-neighborhood IBP test for one terminal residue.

    This is deliberately a *local* diagnostic, not a proof of master-integral
    status.  A residue is locally irreducible when none of the newly generated
    first-neighbor seed rows can create that residue as a new Laporta pivot
    after reduction through the existing triangular rule set.
    """
    residue: IntegralIndex
    tested_seeds: tuple[IntegralIndex, ...]
    pivoting_seeds: tuple[IntegralIndex, ...]
    max_new_pivots: int

    @property
    def locally_irreducible(self) -> bool:
        return not self.pivoting_seeds


def diagnose_first_neighbor_irreducibility(
    family: IntegralFamily,
    residue: IntegralIndex | Sequence[int],
    base_rules: Sequence[ReductionRule],
    probe_substitutions: Mapping[sp.Symbol, sp.Expr],
    symmetries: Sequence[IntegralSymmetry] = (),
    existing_seeds: Iterable[IntegralIndex | Sequence[int]] = (),
    protected: Iterable[IntegralIndex | Sequence[int]] = (),
    vectors: Sequence[str] | None = None,
) -> LocalIrreducibilityDiagnostic:
    """Test every new canonical first-neighbor seed of ``residue``.

    The test is inexpensive because each seed contributes only its own IBP rows
    and those rows are reduced through ``base_rules`` incrementally.  It is a
    bounded scheduler diagnostic: failure to find a pivot does *not* constitute
    a global proof that the integral is a true master.
    """
    r = canonicalize_integral(
        residue if isinstance(residue, IntegralIndex) else IntegralIndex(residue),
        symmetries,
    )
    existing = set(canonicalize_seed_set(existing_seeds, symmetries))
    candidates = []
    for raw in first_neighbor_seeds(r):
        c = canonicalize_integral(raw, symmetries)
        if c not in existing:
            candidates.append(c)
    candidates = tuple(sorted(set(candidates), key=lambda x: (sector_rank(x), x.powers)))

    pivoting = []
    max_new = 0
    base_lhs = {rule.lhs for rule in base_rules}
    for seed in candidates:
        eqs = generate_ibp_system(family, (seed,), vectors=vectors)
        if symmetries:
            eqs = canonicalize_ibp_system(eqs, symmetries)
        eqs = prune_zero_sectors(family, eqs)
        peqs = specialize_ibp_system(eqs, probe_substitutions)
        extended = extend_laporta_rules_incrementally(
            base_rules, peqs, protected=protected,
        )
        new_lhs = {rule.lhs for rule in extended} - base_lhs
        max_new = max(max_new, len(new_lhs))
        if r in new_lhs:
            pivoting.append(seed)

    return LocalIrreducibilityDiagnostic(
        residue=r,
        tested_seeds=candidates,
        pivoting_seeds=tuple(pivoting),
        max_new_pivots=max_new,
    )


def promote_local_master_candidates(
    diagnostics: Sequence[LocalIrreducibilityDiagnostic],
) -> tuple[IntegralIndex, ...]:
    """Return residues passing the bounded local-irreducibility test.

    The name intentionally says *candidates*: callers should retain provenance
    and must not present these as globally proven IBP masters without a stronger
    closure argument or an independent reduction system.
    """
    return tuple(sorted(
        {d.residue for d in diagnostics if d.locally_irreducible},
        key=lambda x: x.powers,
    ))


# --- v0.37: directional depth-2 and multi-probe local master diagnostics ---
@dataclass(frozen=True)
class DirectionalDepth2Diagnostic:
    """Second-step local IBP diagnostic along individual index directions.

    This bounded test complements the first-neighborhood diagnostic without
    opening the full degree-2 Cartesian seed domain.  Each admissible index
    direction is moved by two units in the same direction and tested
    incrementally against an existing triangular Laporta rule set.
    """
    residue: IntegralIndex
    tested_seeds: tuple[IntegralIndex, ...]
    pivoting_seeds: tuple[IntegralIndex, ...]
    max_new_pivots: int

    @property
    def directionally_irreducible(self) -> bool:
        return not self.pivoting_seeds


def directional_depth2_seeds(
    index: IntegralIndex | Sequence[int],
    symmetries: Sequence[IntegralSymmetry] = (),
    existing_seeds: Iterable[IntegralIndex | Sequence[int]] = (),
    include_numerator_slots: bool = True,
) -> tuple[IntegralIndex, ...]:
    """Return canonical seeds two steps away along one index direction.

    Positive denominator powers are raised by two.  Non-positive slots are
    lowered by two when ``include_numerator_slots`` is true.  The construction
    is intentionally much smaller than the full degree-2 Cartesian domain and
    is useful for bounded local-master audits.
    """
    idx = index if isinstance(index, IntegralIndex) else IntegralIndex(index)
    idx = canonicalize_integral(idx, symmetries)
    existing = set(canonicalize_seed_set(existing_seeds, symmetries))
    out = set()
    for i, n in enumerate(idx.powers):
        if n > 0:
            delta = 2
        elif include_numerator_slots:
            delta = -2
        else:
            continue
        c = canonicalize_integral(idx.shifted({i: delta}), symmetries)
        if c != idx and c not in existing:
            out.add(c)
    return tuple(sorted(out, key=lambda x: (sector_rank(x), x.powers)))


def diagnose_directional_depth2_irreducibility(
    family: IntegralFamily,
    residue: IntegralIndex | Sequence[int],
    base_rules: Sequence[ReductionRule],
    probe_substitutions: Mapping[sp.Symbol, sp.Expr],
    symmetries: Sequence[IntegralSymmetry] = (),
    existing_seeds: Iterable[IntegralIndex | Sequence[int]] = (),
    protected: Iterable[IntegralIndex | Sequence[int]] = (),
    vectors: Sequence[str] | None = None,
) -> DirectionalDepth2Diagnostic:
    """Test directional second-step seeds for a terminal residue.

    As with the first-neighborhood diagnostic, this is a bounded local test and
    not a proof of global master-integral status.
    """
    r = canonicalize_integral(
        residue if isinstance(residue, IntegralIndex) else IntegralIndex(residue),
        symmetries,
    )
    candidates = directional_depth2_seeds(
        r, symmetries=symmetries, existing_seeds=existing_seeds,
    )
    pivoting = []
    max_new = 0
    base_lhs = {rule.lhs for rule in base_rules}
    for seed in candidates:
        eqs = generate_ibp_system(family, (seed,), vectors=vectors)
        if symmetries:
            eqs = canonicalize_ibp_system(eqs, symmetries)
        eqs = prune_zero_sectors(family, eqs)
        peqs = specialize_ibp_system(eqs, probe_substitutions)
        extended = extend_laporta_rules_incrementally(
            base_rules, peqs, protected=protected,
        )
        new_lhs = {rule.lhs for rule in extended} - base_lhs
        max_new = max(max_new, len(new_lhs))
        if r in new_lhs:
            pivoting.append(seed)
    return DirectionalDepth2Diagnostic(
        residue=r,
        tested_seeds=candidates,
        pivoting_seeds=tuple(pivoting),
        max_new_pivots=max_new,
    )


def build_specialized_laporta_rules(
    family: IntegralFamily,
    seeds: Iterable[IntegralIndex | Sequence[int]],
    probe_substitutions: Mapping[sp.Symbol, sp.Expr],
    symmetries: Sequence[IntegralSymmetry] = (),
    protected: Iterable[IntegralIndex | Sequence[int]] = (),
    vectors: Sequence[str] | None = None,
) -> tuple[ReductionRule, ...]:
    """Build one exact-rational Laporta rule set from a fixed seed domain.

    This helper is primarily for independent multi-probe audits: the same
    canonical seed domain can be rebuilt at several exact rational points and
    compared without changing the symbolic family definition.
    """
    cseeds = canonicalize_seed_set(seeds, symmetries)
    eqs = generate_ibp_system(family, cseeds, vectors=vectors)
    if symmetries:
        eqs = canonicalize_ibp_system(eqs, symmetries)
    eqs = prune_zero_sectors(family, eqs)
    peqs = specialize_ibp_system(eqs, probe_substitutions)
    return laporta_forward_eliminate(
        peqs, family=None, prune_scaleless=False, protected=protected,
    )


# --- v0.38: full Cartesian degree-2 audit and portable Laporta checkpoints ---
@dataclass(frozen=True)
class MixedDegree2Diagnostic:
    """Audit result for the previously untested mixed degree-2 seed domain.

    First-neighbor and same-direction depth-2 seeds are deliberately excluded;
    this diagnostic covers the remaining Cartesian degree-2 combinations in
    which two admissible index moves are combined.  As with the earlier local
    diagnostics, absence of a pivot is bounded evidence rather than a global
    proof of master-integral status.
    """
    residue: IntegralIndex
    tested_seeds: tuple[IntegralIndex, ...]
    pivoting_seeds: tuple[IntegralIndex, ...]
    max_new_pivots: int

    @property
    def mixed_degree2_irreducible(self) -> bool:
        return not self.pivoting_seeds


def mixed_degree2_seeds(
    index: IntegralIndex | Sequence[int],
    symmetries: Sequence[IntegralSymmetry] = (),
    existing_seeds: Iterable[IntegralIndex | Sequence[int]] = (),
    include_numerator_slots: bool = True,
) -> tuple[IntegralIndex, ...]:
    """Return the untested mixed part of the full Cartesian degree-2 domain.

    The full bounded degree-2 domain contains the center, first neighbors,
    same-direction depth-2 seeds and mixed two-direction moves.  This helper
    returns only the final class after symmetry canonicalization and removal of
    already-existing seeds.
    """
    idx = index if isinstance(index, IntegralIndex) else IntegralIndex(index)
    center = canonicalize_integral(idx, symmetries)
    existing = set(canonicalize_seed_set(existing_seeds, symmetries))
    full = set(canonicalize_seed_set(
        bounded_seed_domain(center, max_extra_degree=2,
                            include_numerator_slots=include_numerator_slots),
        symmetries,
    ))
    first = set(canonicalize_seed_set(
        first_neighbor_seeds(center, include_numerator_slots=include_numerator_slots),
        symmetries,
    ))
    directional = set(directional_depth2_seeds(
        center, symmetries=symmetries, existing_seeds=(),
        include_numerator_slots=include_numerator_slots,
    ))
    mixed = full - {center} - first - directional - existing
    return tuple(sorted(mixed, key=lambda x: (sector_rank(x), x.powers)))


def diagnose_mixed_degree2_irreducibility(
    family: IntegralFamily,
    residue: IntegralIndex | Sequence[int],
    base_rules: Sequence[ReductionRule],
    probe_substitutions: Mapping[sp.Symbol, sp.Expr],
    symmetries: Sequence[IntegralSymmetry] = (),
    existing_seeds: Iterable[IntegralIndex | Sequence[int]] = (),
    protected: Iterable[IntegralIndex | Sequence[int]] = (),
    vectors: Sequence[str] | None = None,
) -> MixedDegree2Diagnostic:
    """Test every new mixed Cartesian degree-2 seed for one residue."""
    r = canonicalize_integral(
        residue if isinstance(residue, IntegralIndex) else IntegralIndex(residue),
        symmetries,
    )
    candidates = mixed_degree2_seeds(
        r, symmetries=symmetries, existing_seeds=existing_seeds,
    )
    pivoting = []
    max_new = 0
    base_lhs = {rule.lhs for rule in base_rules}
    for seed in candidates:
        eqs = generate_ibp_system(family, (seed,), vectors=vectors)
        if symmetries:
            eqs = canonicalize_ibp_system(eqs, symmetries)
        eqs = prune_zero_sectors(family, eqs)
        peqs = specialize_ibp_system(eqs, probe_substitutions)
        extended = extend_laporta_rules_incrementally(
            base_rules, peqs, protected=protected,
        )
        new_lhs = {rule.lhs for rule in extended} - base_lhs
        max_new = max(max_new, len(new_lhs))
        if r in new_lhs:
            pivoting.append(seed)
    return MixedDegree2Diagnostic(
        residue=r,
        tested_seeds=candidates,
        pivoting_seeds=tuple(pivoting),
        max_new_pivots=max_new,
    )


def write_laporta_rule_checkpoint(
    path: str | Path,
    rules: Sequence[ReductionRule],
    metadata: Mapping[str, object] | None = None,
) -> Path:
    """Write a portable JSON checkpoint for an exact/symbolic rule set.

    Coefficients are stored as SymPy-readable strings.  This format is intended
    for QEDCalc's own reproducible checkpoints and avoids Python pickle/module
    coupling.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "format": "qedcalc-laporta-rules-v1",
        "metadata": dict(metadata or {}),
        "rules": [],
    }
    for rule in rules:
        payload["rules"].append({
            "lhs": list(rule.lhs.powers),
            "rhs": [
                {"index": list(idx.powers), "coefficient": sp.sstr(coeff)}
                for idx, coeff in sorted(rule.rhs.items(), key=lambda kv: kv[0].powers)
            ],
        })
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def read_laporta_rule_checkpoint(
    path: str | Path,
    local_symbols: Mapping[str, object] | None = None,
) -> tuple[tuple[ReductionRule, ...], dict]:
    """Read a checkpoint produced by :func:`write_laporta_rule_checkpoint`."""
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if payload.get("format") != "qedcalc-laporta-rules-v1":
        raise ValueError("Unsupported QEDCalc Laporta checkpoint format.")
    locals_map = dict(local_symbols or {})
    rules = []
    for item in payload.get("rules", []):
        lhs = IntegralIndex(item["lhs"])
        rhs = {}
        for term in item.get("rhs", []):
            idx = IntegralIndex(term["index"])
            coeff = sp.sympify(term["coefficient"], locals=locals_map)
            if coeff != 0:
                rhs[idx] = coeff
        rules.append(ReductionRule(lhs, rhs))
    return tuple(rules), dict(payload.get("metadata") or {})

# --- v0.40: full bounded degree-3 sector-batched audit ---
@dataclass(frozen=True)
class Degree3SectorAudit:
    """One sector batch in the new degree-3 shell around a candidate."""
    sector: int
    tested_seeds: tuple[IntegralIndex, ...]
    new_pivots: int
    candidate_pivoted: bool


@dataclass(frozen=True)
class FullDegree3Diagnostic:
    """Bounded full degree-3 Cartesian audit for one provisional candidate.

    Only the *new shell* at extra degree 3 is tested; degree <=2 is assumed to
    have been audited already.  New seeds are canonicalized by family
    symmetries, grouped by sector, and added incrementally to an existing
    triangular Laporta rule set.
    """
    residue: IntegralIndex
    tested_seeds: tuple[IntegralIndex, ...]
    sector_audits: tuple[Degree3SectorAudit, ...]

    @property
    def pivoting_seeds(self) -> tuple[IntegralIndex, ...]:
        # Sector-batched mode detects whether the candidate becomes a pivot in
        # a batch.  Individual seed attribution is intentionally not claimed.
        return () if not any(x.candidate_pivoted for x in self.sector_audits) else self.tested_seeds

    @property
    def full_degree3_irreducible(self) -> bool:
        return not any(x.candidate_pivoted for x in self.sector_audits)

    @property
    def total_new_pivots(self) -> int:
        return sum(x.new_pivots for x in self.sector_audits)


def degree3_shell_seeds(
    index: IntegralIndex | Sequence[int],
    symmetries: Sequence[IntegralSymmetry] = (),
    existing_seeds: Iterable[IntegralIndex | Sequence[int]] = (),
    include_numerator_slots: bool = True,
) -> tuple[IntegralIndex, ...]:
    """Return only the new canonical shell at bounded extra degree 3.

    This is ``bounded_seed_domain(..., 3) - bounded_seed_domain(..., 2)``
    after symmetry canonicalization and removal of an optional existing seed
    set.  It therefore includes directional and mixed cubic moves without
    reopening already-audited degree <=2 seeds.
    """
    idx = index if isinstance(index, IntegralIndex) else IntegralIndex(index)
    center = canonicalize_integral(idx, symmetries)
    d2 = set(canonicalize_seed_set(
        bounded_seed_domain(center, max_extra_degree=2,
                            include_numerator_slots=include_numerator_slots),
        symmetries,
    ))
    d3 = set(canonicalize_seed_set(
        bounded_seed_domain(center, max_extra_degree=3,
                            include_numerator_slots=include_numerator_slots),
        symmetries,
    ))
    existing = set(canonicalize_seed_set(existing_seeds, symmetries))
    shell = d3 - d2 - existing
    return tuple(sorted(shell, key=lambda x: (sector_rank(x), x.powers)))


def diagnose_full_degree3_irreducibility(
    family: IntegralFamily,
    residue: IntegralIndex | Sequence[int],
    base_rules: Sequence[ReductionRule],
    probe_substitutions: Mapping[sp.Symbol, sp.Expr],
    symmetries: Sequence[IntegralSymmetry] = (),
    existing_seeds: Iterable[IntegralIndex | Sequence[int]] = (),
    protected: Iterable[IntegralIndex | Sequence[int]] = (),
    vectors: Sequence[str] | None = None,
) -> FullDegree3Diagnostic:
    """Audit the complete new bounded degree-3 shell, sector by sector.

    Each sector is generated and specialized separately, then appended through
    incremental Laporta elimination.  This keeps the audit bounded and avoids
    rebuilding the baseline rule system for every seed.  As with the degree-2
    diagnostics, a non-pivot result is strong bounded evidence, not a global
    proof of master-integral status.
    """
    r = canonicalize_integral(
        residue if isinstance(residue, IntegralIndex) else IntegralIndex(residue),
        symmetries,
    )
    seeds = degree3_shell_seeds(
        r, symmetries=symmetries, existing_seeds=existing_seeds,
    )
    groups: dict[int, list[IntegralIndex]] = {}
    for seed in seeds:
        groups.setdefault(sector_id(seed), []).append(seed)

    current = tuple(base_rules)
    audits: list[Degree3SectorAudit] = []
    # Larger sectors first is a useful deterministic heuristic for the ladder
    # family; the result does not rely on the ordering if the full shell is run.
    for sid, batch in sorted(groups.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        eqs = generate_ibp_system(family, tuple(batch), vectors=vectors)
        if symmetries:
            eqs = canonicalize_ibp_system(eqs, symmetries)
        eqs = prune_zero_sectors(family, eqs)
        peqs = specialize_ibp_system(eqs, probe_substitutions)
        before = {rule.lhs for rule in current}
        extended = extend_laporta_rules_incrementally(
            current, peqs, protected=protected,
        )
        new_lhs = {rule.lhs for rule in extended} - before
        hit = r in new_lhs
        audits.append(Degree3SectorAudit(
            sector=sid,
            tested_seeds=tuple(sorted(batch, key=lambda x: x.powers)),
            new_pivots=len(new_lhs),
            candidate_pivoted=hit,
        ))
        current = extended
        if hit:
            break
    return FullDegree3Diagnostic(
        residue=r,
        tested_seeds=seeds,
        sector_audits=tuple(audits),
    )
