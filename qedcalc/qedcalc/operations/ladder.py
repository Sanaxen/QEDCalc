from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import csv
import sympy as sp

from qedcalc.core.expression import (
    QEDExpr, Symbol, Gamma, Metric, Index, NCProduct, ScalarMul, Add
)


@dataclass(frozen=True, order=True)
class LadderIntegralIndex:
    """Index tuple for the ordinary-ladder scalar integral family.

    J(nK,nL,nH,n1,n2,n3,n4) = ∫ d^Dk d^Dl /
      [K^nK L^nL H^nH E1^n1 E2^n2 E3^n3 E4^n4].

    Negative exponents represent numerator powers.
    """
    nK: int
    nL: int
    nH: int
    n1: int
    n2: int
    n3: int
    n4: int

    def as_tuple(self):
        return (self.nK, self.nL, self.nH, self.n1, self.n2, self.n3, self.n4)


def ladder_projector_coefficients(D=None, z=None):
    """Return the D-dimensional Pauli-projector coefficients (a,b).

    The projector convention is
      P_mu = (1/m^2)(/p'+m)[a gamma_mu + b r_mu/m](/p+m),
    with z=q^2/m^2.
    """
    D = sp.Symbol("D") if D is None else sp.sympify(D)
    z = sp.Symbol("z") if z is None else sp.sympify(z)
    a = sp.simplify(2 / (z * (D - 2) * (z - 4)))
    b = sp.simplify((D*z - 2*z + 4) / (z * (D - 2) * (z - 4)**2))
    return a, b


def contract_outer_gamma_ddim_one(expr: QEDExpr, D_name="D") -> QEDExpr:
    """Apply gamma^a gamma^b gamma_a = (2-D) gamma^b.

    This deliberately implements only the one-inner-gamma D-dimensional
    identity and rejects unrelated structures by returning them unchanged.
    """
    if not isinstance(expr, NCProduct) or len(expr.factors) != 3:
        return expr
    a, b, c = expr.factors
    if not (isinstance(a, Gamma) and isinstance(b, Gamma) and isinstance(c, Gamma)):
        return expr
    if a.index.name != c.index.name or a.index.position == c.index.position:
        return expr
    return ScalarMul(sp.Symbol(D_name) * -1 + 2, b)


def contract_outer_gamma_ddim_two(expr: QEDExpr, D_name="D") -> QEDExpr:
    """Apply gamma^a gamma^b gamma^c gamma_a in D dimensions.

    gamma^a gamma^b gamma^c gamma_a
      = 4 g^{bc} + (D-4) gamma^b gamma^c.
    """
    if not isinstance(expr, NCProduct) or len(expr.factors) != 4:
        return expr
    a, b, c, d = expr.factors
    if not all(isinstance(x, Gamma) for x in (a,b,c,d)):
        return expr
    if a.index.name != d.index.name or a.index.position == d.index.position:
        return expr
    return Add(
        ScalarMul(4, Metric(b.index, c.index)),
        ScalarMul(sp.Symbol(D_name)-4, NCProduct(b,c)),
    )


def ladder_scalar_product_symbols():
    """Return the standard ordinary-ladder denominator/scalar-product symbols."""
    names = "K L H E1 E2 E3 E4 pk ppk pl ppl kl k2 l2"
    return dict(zip(names.split(), sp.symbols(names)))


def ladder_scalar_product_rules():
    """Return the q^2=0/on-shell scalar-product-to-denominator rules.

    Keys are symbolic scalar-product placeholders:
      k2,l2,kl,ppk,pk,ppl,pl
    where ppk=p'·k, pk=p·k, ppl=p'·l, pl=p·l.
    """
    s = ladder_scalar_product_symbols()
    K,L,H,E1,E2,E3,E4 = (s[n] for n in ("K","L","H","E1","E2","E3","E4"))
    return {
        s["k2"]: -K,
        s["l2"]: -L,
        s["kl"]: (K + L - H)/2,
        s["ppk"]: (E1 - K)/2,
        s["pk"]: (E4 - K)/2,
        s["ppl"]: (E2 - H - E1 + K)/2,
        s["pl"]: (E3 - H - E4 + K)/2,
    }


def reduce_ladder_scalar_products(expr):
    """Replace the standard scalar-product placeholders by denominator variables."""
    return sp.expand(sp.sympify(expr).subs(ladder_scalar_product_rules()))


def load_ladder_coefficient_table(path) -> dict[LadderIntegralIndex, sp.Expr]:
    """Load the reproducible 75-term ordinary-ladder coefficient table."""
    path = Path(path)
    out = {}
    D,z = sp.symbols("D z")
    with path.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            idx = LadderIntegralIndex(*(int(row[k]) for k in ("nK","nL","nH","n1","n2","n3","n4")))
            coeff = sp.sympify(row["coefficient"], locals={"D":D,"z":z})
            if idx in out:
                raise ValueError(f"Duplicate ladder integral index in coefficient table: {idx}")
            out[idx] = sp.factor(coeff)
    return out


def ladder_coefficient(table, *index):
    idx = index[0] if len(index) == 1 and isinstance(index[0], LadderIntegralIndex) else LadderIntegralIndex(*index)
    if idx not in table:
        raise KeyError(f"Ladder integral index not present: {idx.as_tuple()}")
    return table[idx]


def one_loop_f2_dimensional(D=None):
    """D-dimensional one-loop Pauli form factor used by ladder subtraction."""
    D = sp.Symbol("D") if D is None else sp.sympify(D)
    return sp.simplify((5-D)/(2*(D-3)))


def one_loop_z1_dimensional(D=None):
    """One-loop on-shell vertex renormalization factor in the ladder convention."""
    D = sp.Symbol("D") if D is None else sp.sympify(D)
    return sp.simplify(-sp.Rational(1,2)*(D-1)/((D-3)*(D-4)))


def ladder_subtraction_series(delta=None, order=1):
    """Laurent-expand Z1^(1l) F2^(1l) around D=4+delta."""
    delta = sp.Symbol("delta") if delta is None else sp.sympify(delta)
    D = 4 + delta
    expr = sp.simplify(one_loop_z1_dimensional(D) * one_loop_f2_dimensional(D))
    return sp.series(expr, delta, 0, order+1)


def ladder_bare_checkpoint(delta=None):
    """Bare ordinary-ladder checkpoint from the independently reduced masters."""
    delta = sp.Symbol("delta") if delta is None else sp.sympify(delta)
    return -sp.Rational(3,4)/delta + sp.Rational(107,48) + sp.pi**2/18


def ladder_renormalized_checkpoint(delta=None):
    """Combine bare and subtraction checkpoints and return the finite result."""
    delta = sp.Symbol("delta") if delta is None else sp.sympify(delta)
    bare = ladder_bare_checkpoint(delta)
    sub_exact = sp.simplify(one_loop_z1_dimensional(4+delta) * one_loop_f2_dimensional(4+delta))
    ren = sp.series(bare - sub_exact, delta, 0, 1).removeO()
    return sp.simplify(ren)

# --- v0.24: raw ordinary-ladder bridge ---
from typing import Tuple
from qedcalc.core.expression import Fraction, Vector, Slash, Product, Power, ScalarProduct, LoopIntegralExpression
from qedcalc.operations.propagator import recognize_propagators, scalarize_fermion_propagators, separate_numerator_denominator


@dataclass(frozen=True)
class RawLadderStructure:
    """Structural information extracted from a bare ordinary-ladder diagram."""
    electron_momenta: Tuple[QEDExpr, ...]
    electron_labels: Tuple[str, ...]
    photon_labels: Tuple[str, ...]
    base_integral_index: LadderIntegralIndex
    scalarized_integrand: Fraction


def _linear_vector_coeffs(expr: QEDExpr) -> dict[str, int]:
    """Return integer coefficients of a linear combination of Vector objects."""
    out: dict[str, int] = {}
    terms = expr.terms if isinstance(expr, Add) else (expr,)
    for term in terms:
        coeff = 1
        obj = term
        if isinstance(term, ScalarMul):
            try:
                coeff = int(term.coeff)
            except Exception as exc:
                raise ValueError("Non-integer momentum coefficient is not supported in the raw ladder bridge.") from exc
            obj = term.expr
        if not isinstance(obj, Vector):
            raise ValueError(f"Expected a linear momentum combination, found {type(obj).__name__}.")
        out[obj.name] = out.get(obj.name, 0) + coeff
    return {name: coeff for name, coeff in out.items() if coeff != 0}


def _fermion_momentum_from_fraction(frac: Fraction) -> QEDExpr:
    """Infer P from a raw denominator m-/P-i eps without importing topology code."""
    coeffs: dict[str, int] = {}
    terms = frac.denominator.terms if isinstance(frac.denominator, Add) else (frac.denominator,)
    for term in terms:
        coeff = 1
        obj = term
        if isinstance(term, ScalarMul):
            try:
                coeff = int(term.coeff)
            except Exception:
                continue
            obj = term.expr
        if isinstance(obj, Slash) and isinstance(obj.arg, Vector):
            coeffs[obj.arg.name] = coeffs.get(obj.arg.name, 0) + coeff
    pieces = []
    for name, den_coeff in coeffs.items():
        physical_coeff = -den_coeff
        if physical_coeff == 0:
            continue
        vec = Vector(name)
        pieces.append(vec if physical_coeff == 1 else ScalarMul(physical_coeff, vec))
    if not pieces:
        raise ValueError("Could not infer fermion momentum from raw propagator denominator.")
    return pieces[0] if len(pieces) == 1 else Add(*pieces)


def _raw_ladder_electron_label(momentum: QEDExpr) -> str:
    c = _linear_vector_coeffs(momentum)
    expected = {
        (("k", -1), ("p'", 1)): "E1",
        (("k", -1), ("l", -1), ("p'", 1)): "E2",
        (("k", -1), ("l", -1), ("p", 1)): "E3",
        (("k", -1), ("p", 1)): "E4",
    }
    key = tuple(sorted(c.items()))
    if key not in expected:
        raise ValueError(f"Unrecognized ordinary-ladder electron momentum pattern: {c}")
    return expected[key]


def _fraction_square_loop_name(frac: Fraction) -> str | None:
    """Return k for a scalar denominator proportional to -k^2 plus regulators."""
    squares = []
    for node in frac.denominator.walk():
        if isinstance(node, ScalarProduct) and isinstance(node.left, Vector) and isinstance(node.right, Vector):
            if node.left.name == node.right.name:
                squares.append(node.left.name)
    unique = sorted(set(squares))
    return unique[0] if len(unique) == 1 else None


def derive_ladder_scalar_product_rules_from_family():
    """Derive the ordinary-ladder scalar-product basis from denominator equations.

    The returned dictionary has the same placeholders as ``ladder_scalar_product_rules``
    but is obtained by solving the K,L,H,E1..E4 definitions instead of storing the
    replacement formulas directly.
    """
    s = ladder_scalar_product_symbols()
    K,L,H,E1,E2,E3,E4 = (s[n] for n in ("K","L","H","E1","E2","E3","E4"))
    k2,l2,kl,ppk,pk,ppl,pl = (s[n] for n in ("k2","l2","kl","ppk","pk","ppl","pl"))
    equations = [
        sp.Eq(K, -k2),
        sp.Eq(L, -l2),
        sp.Eq(H, -(k2 + l2 + 2*kl)),
        sp.Eq(E1, 2*ppk - k2),
        sp.Eq(E2, 2*ppk + 2*ppl - (k2 + l2 + 2*kl)),
        sp.Eq(E3, 2*pk + 2*pl - (k2 + l2 + 2*kl)),
        sp.Eq(E4, 2*pk - k2),
    ]
    unknowns = (k2,l2,kl,ppk,pk,ppl,pl)
    sol = sp.solve(equations, unknowns, dict=True)
    if len(sol) != 1:
        raise ValueError("Ordinary-ladder denominator equations did not have a unique scalar-product solution.")
    return {u: sp.simplify(sol[0][u]) for u in unknowns}


def analyze_raw_ordinary_ladder(diagram: LoopIntegralExpression) -> RawLadderStructure:
    """Extract the seven-denominator ordinary-ladder family from bare LaTeX input.

    The bridge validates the ordered electron momenta E1..E4 and the two photon
    denominators K,L.  H=-(k+l)^2 is introduced as the standard auxiliary family
    denominator with exponent zero in the bare graph.
    """
    loop_names = tuple(v.name for v in diagram.loops)
    if loop_names != ("k", "l"):
        raise ValueError(f"Ordinary-ladder raw bridge expects loop order (k,l), found {loop_names}.")
    factors = diagram.integrand.factors if isinstance(diagram.integrand, NCProduct) else (diagram.integrand,)
    fermions = [f for f in factors if isinstance(f, Fraction) and any(isinstance(n, Slash) for n in f.denominator.walk())]
    if len(fermions) != 4:
        raise ValueError(f"Expected four electron propagators in ordinary ladder, found {len(fermions)}.")
    momenta = tuple(_fermion_momentum_from_fraction(f) for f in fermions)
    labels = tuple(_raw_ladder_electron_label(p) for p in momenta)
    if labels != ("E1", "E2", "E3", "E4"):
        raise ValueError(f"Unexpected ordinary-ladder electron-line ordering: {labels}.")

    scalar_fracs = [
        f for f in factors
        if isinstance(f, Fraction)
        and isinstance(f.numerator, Symbol) and f.numerator.name == "1"
        and not any(isinstance(n, Slash) for n in f.denominator.walk())
    ]
    photon_names = [_fraction_square_loop_name(f) for f in scalar_fracs]
    photon_names = [n for n in photon_names if n in ("k", "l")]
    if sorted(photon_names) != ["k", "l"]:
        raise ValueError(f"Expected scalar photon denominators for k and l, found {photon_names}.")
    photon_labels = tuple("K" if n == "k" else "L" for n in photon_names)

    recognized = recognize_propagators(diagram.integrand)
    scalarized = scalarize_fermion_propagators(recognized)
    frac = separate_numerator_denominator(scalarized)
    if not isinstance(frac, Fraction):
        raise TypeError("Scalarized ordinary ladder did not produce a Fraction.")

    return RawLadderStructure(
        electron_momenta=momenta,
        electron_labels=labels,
        photon_labels=photon_labels,
        base_integral_index=LadderIntegralIndex(1,1,0,1,1,1,1),
        scalarized_integrand=frac,
    )


def raw_ladder_q0_numerator(raw: RawLadderStructure) -> QEDExpr:
    """Set p'=p in the scalarized raw-ladder numerator.

    This is the direct bridge to the A0 branch before the D-dimensional
    projector trace.  It deliberately does not evaluate the long Clifford
    trace; it only generates the q=0 Dirac numerator from the bare graph.
    """
    from qedcalc.operations.momentum import substitute_vector
    from qedcalc.operations.simplify import simplify_expression
    return simplify_expression(substitute_vector(raw.scalarized_integrand.numerator, "p'", Vector("p")))

# --- v0.25: raw A0 projector trace and 29-integral generation ---
@dataclass(frozen=True, order=True)
class LadderA0IntegralIndex:
    """Five-denominator q=0 ordinary-ladder family J(nK,nL,nH,nA,nB)."""
    nK: int
    nL: int
    nH: int
    nA: int
    nB: int

    def as_tuple(self):
        return (self.nK,self.nL,self.nH,self.nA,self.nB)


from functools import lru_cache

@lru_cache(maxsize=16)
def ladder_a0_projector_trace_sympy(raw: RawLadderStructure, D_name="D"):
    """Generate the q=0 ordinary-ladder A0 projector trace from raw bare input.

    A0 = Tr[(/P+m) N_mu^(0) (/P+m) gamma^mu].
    The arbitrary-length Clifford trace is evaluated directly to a SymPy scalar
    without materializing the enormous intermediate metric expression.
    """
    from qedcalc.operations.momentum import substitute_vector
    from qedcalc.operations.dirac import dirac_trace_fully_contracted_sympy
    P=Vector("P")
    m=Symbol("m")
    numerator=substitute_vector(raw_ladder_q0_numerator(raw), "p", P)
    trace_expr=NCProduct(
        Add(Slash(P),m),
        numerator,
        Add(Slash(P),m),
        Gamma(Index("mu","up")),
    )
    return dirac_trace_fully_contracted_sympy(trace_expr,D_name=D_name)


def ladder_a0_denominator_polynomial(raw: RawLadderStructure, set_mass_one=True):
    """Convert the raw A0 Clifford trace to the K,L,H,A,B polynomial."""
    tr=ladder_a0_projector_trace_sympy(raw)
    D,m,K,L,H,A,B=sp.symbols("D m K L H A B")
    substitutions={
        sp.Symbol("SP__P__P"): m**2,
        sp.Symbol("SP__P__k"): (A-K)/2,
        sp.Symbol("SP__P__l"): (B-H-A+K)/2,
        sp.Symbol("SP__k__k"): -K,
        sp.Symbol("SP__l__l"): -L,
        sp.Symbol("SP__k__l"): (K+L-H)/2,
    }
    out=sp.expand(tr.subs(substitutions))
    if set_mass_one:
        out=sp.expand(out.subs(m,1))
    return out


def ladder_a0_integral_table(raw: RawLadderStructure) -> dict[LadderA0IntegralIndex, sp.Expr]:
    """Generate the complete 29-term q=0 A0 scalar-integral table from raw input.

    The q=0 bare denominator is K L A^2 B^2.  Every numerator monomial shifts
    these denominator powers and is collected as J(nK,nL,nH,nA,nB).
    """
    K,L,H,A,B=sp.symbols("K L H A B")
    poly=sp.Poly(ladder_a0_denominator_polynomial(raw,set_mass_one=True),K,L,H,A,B)
    table={}
    for monomial,coeff in poly.terms():
        pK,pL,pH,pA,pB=monomial
        idx=LadderA0IntegralIndex(1-pK,1-pL,-pH,2-pA,2-pB)
        table[idx]=sp.factor(table.get(idx,0)+coeff)
    return dict(sorted(table.items(), key=lambda kv: kv[0].as_tuple()))


def write_ladder_a0_integral_table_csv(table, path):
    """Write a generated A0 integral table for independent inspection."""
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8",newline="") as f:
        w=csv.writer(f)
        w.writerow(["nK","nL","nH","nA","nB","coefficient"])
        for idx,coeff in sorted(table.items(),key=lambda kv:kv[0].as_tuple()):
            w.writerow([*idx.as_tuple(),str(sp.factor(coeff))])
    return path

# --- v0.26: general-q^2 raw projector trace and coefficient-table regeneration ---
@dataclass(frozen=True)
class LadderGeneralQTraceResult:
    """General-q^2 ordinary-ladder projector result.

    ``trace_order`` is either ``archived`` (the historical projector-first
    trace used to generate the stored 75-term audit CSV) or ``spin_sum`` (the
    corrected spin-sum trace order used by the physical finite-q projector
    analysis in the later audit).
    """
    trace_order: str
    A: sp.Expr
    B: sp.Expr
    projected: sp.Expr
    denominator_polynomial: sp.Expr
    integral_table: dict[LadderIntegralIndex, sp.Expr]


def ladder_corrected_projector_coefficients(D=None, z=None):
    """Return the corrected finite-q projector coefficients after trace-order audit.

    In the notation of the audited ladder derivation,
      a(z) = -2/[z(D-2)(z-4)],
      b(z) = -(Dz-2z+4)/[z(D-2)(z-4)^2].
    """
    a, b = ladder_projector_coefficients(D, z)
    return sp.simplify(-a), sp.simplify(-b)


def _replace_external_mu_by_rslash(expr: QEDExpr) -> QEDExpr:
    """Contract the unique external vertex index mu with r=p'+p.

    For the ordinary ladder numerator the external photon vertex occurs once
    as gamma_mu.  Replacing that factor by /p' + /p implements r^mu N_mu.
    """
    from qedcalc.core.expression import Product
    pp = Vector("p'")
    p = Vector("p")
    if isinstance(expr, Gamma) and expr.index.name == "mu":
        return Add(Slash(pp), Slash(p))
    if isinstance(expr, Add):
        return Add(*(_replace_external_mu_by_rslash(t) for t in expr.terms))
    if isinstance(expr, Product):
        return Product(*(_replace_external_mu_by_rslash(f) for f in expr.factors))
    if isinstance(expr, NCProduct):
        return NCProduct(*(_replace_external_mu_by_rslash(f) for f in expr.factors))
    if isinstance(expr, ScalarMul):
        return ScalarMul(expr.coeff, _replace_external_mu_by_rslash(expr.expr))
    return expr


def _ladder_general_q_scalar_substitutions():
    """Return on-shell/general-q scalar-product substitutions at m=1."""
    D, z = sp.symbols("D z")
    K,L,H,E1,E2,E3,E4 = sp.symbols("K L H E1 E2 E3 E4")
    return {
        sp.Symbol("SP__p__p"): sp.Integer(1),
        sp.Symbol("SP__p'__p'"): sp.Integer(1),
        sp.Symbol("SP__p__p'"): 1 - z/2,
        sp.Symbol("SP__k__k"): -K,
        sp.Symbol("SP__l__l"): -L,
        sp.Symbol("SP__k__l"): (K + L - H)/2,
        sp.Symbol("SP__k__p'"): (E1 - K)/2,
        sp.Symbol("SP__k__p"): (E4 - K)/2,
        sp.Symbol("SP__l__p'"): (E2 - H - E1 + K)/2,
        sp.Symbol("SP__l__p"): (E3 - H - E4 + K)/2,
        sp.Symbol("m"): sp.Integer(1),
    }


def _ladder_general_q_integral_table_from_projected(projected: sp.Expr):
    """Convert a projected general-q scalar polynomial to the 7-denominator family."""
    K,L,H,E1,E2,E3,E4 = sp.symbols("K L H E1 E2 E3 E4")
    numerator, common = sp.together(projected).as_numer_denom()
    poly = sp.Poly(sp.expand(numerator), K,L,H,E1,E2,E3,E4)
    table: dict[LadderIntegralIndex, sp.Expr] = {}
    for monomial, coeff in poly.terms():
        pK,pL,pH,p1,p2,p3,p4 = monomial
        idx = LadderIntegralIndex(1-pK, 1-pL, -pH, 1-p1, 1-p2, 1-p3, 1-p4)
        table[idx] = sp.factor(table.get(idx, 0) + coeff/common)
    return dict(sorted(table.items(), key=lambda kv: kv[0].as_tuple()))


@lru_cache(maxsize=4)
def ladder_general_q_projector_result(raw: RawLadderStructure, trace_order="archived") -> LadderGeneralQTraceResult:
    """Regenerate the general-q ordinary-ladder projector polynomial from raw input.

    Parameters
    ----------
    raw:
        Structure returned by ``analyze_raw_ordinary_ladder``.
    trace_order:
        ``"archived"`` reproduces the historical 75-term audit CSV exactly.
        It uses the projector-first trace order that was later identified as
        unsuitable for the physical spin-sum projector.

        ``"spin_sum"`` uses the corrected order
          Tr[(/p'+m) Gamma_L^mu (/p+m) O_mu]
        together with the corrected finite-q projector coefficients.  This
        route is kept separate deliberately and is not compared against the
        historical 75-term CSV.
    """
    from qedcalc.operations.dirac import dirac_trace_fully_contracted_sympy

    if trace_order not in {"archived", "spin_sum"}:
        raise ValueError("trace_order must be 'archived' or 'spin_sum'.")

    numerator = raw.scalarized_integrand.numerator
    pp = Vector("p'")
    p = Vector("p")
    m = Symbol("m")
    spin_pp = Add(Slash(pp), m)
    spin_p = Add(Slash(p), m)
    gamma_mu_up = Gamma(Index("mu", "up"))
    r_contracted = _replace_external_mu_by_rslash(numerator)

    if trace_order == "archived":
        # Historical audit-table ordering:
        # Tr[(/p'+m) O_mu (/p+m) Gamma_L^mu].
        A_expr = NCProduct(spin_pp, gamma_mu_up, spin_p, numerator)
        B_expr = NCProduct(spin_pp, spin_p, r_contracted)
        a, b = ladder_projector_coefficients()
    else:
        # Correct spin-sum ordering:
        # Tr[(/p'+m) Gamma_L^mu (/p+m) O_mu].
        A_expr = NCProduct(spin_pp, numerator, spin_p, gamma_mu_up)
        B_expr = NCProduct(spin_pp, r_contracted, spin_p)
        a, b = ladder_corrected_projector_coefficients()

    A = dirac_trace_fully_contracted_sympy(A_expr)
    B = dirac_trace_fully_contracted_sympy(B_expr)
    subs = _ladder_general_q_scalar_substitutions()
    Ared = sp.expand(A.subs(subs))
    Bred = sp.expand(B.subs(subs))
    leftover = [s for s in Ared.free_symbols | Bred.free_symbols if str(s).startswith("SP__")]
    if leftover:
        raise ValueError(f"Unreduced scalar products in general-q ladder trace: {leftover}")

    projected = sp.factor(a*Ared + b*Bred)
    table = _ladder_general_q_integral_table_from_projected(projected)
    # Expose the numerator polynomial after the universal projector denominator.
    denominator_polynomial = sp.factor(sp.together(projected).as_numer_denom()[0])
    return LadderGeneralQTraceResult(trace_order, Ared, Bred, projected, denominator_polynomial, table)


def compare_ladder_integral_tables(generated, reference):
    """Return exact structural/value differences between two ladder tables."""
    gen_keys = set(generated)
    ref_keys = set(reference)
    missing = sorted(ref_keys-gen_keys, key=lambda x: x.as_tuple())
    extra = sorted(gen_keys-ref_keys, key=lambda x: x.as_tuple())
    mismatched = []
    for idx in sorted(gen_keys & ref_keys, key=lambda x: x.as_tuple()):
        if sp.simplify(generated[idx]-reference[idx]) != 0:
            mismatched.append((idx, sp.factor(generated[idx]), sp.factor(reference[idx])))
    return {"missing": missing, "extra": extra, "mismatched": mismatched}


def write_ladder_general_q_integral_table_csv(table, path):
    """Write a generated seven-denominator general-q ladder table."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["nK","nL","nH","n1","n2","n3","n4","coefficient"])
        for idx, coeff in sorted(table.items(), key=lambda kv: kv[0].as_tuple()):
            w.writerow([*idx.as_tuple(), str(sp.factor(coeff))])
    return path

# --- v0.27: ordinary-ladder IBP family bridge ---
def ordinary_ladder_ibp_family(D=None, z=None, mass_squared=None):
    """Build the seven-denominator ordinary-ladder family for generic IBP generation.

    The denominator basis is (K,L,H,E1,E2,E3,E4), with on-shell external
    invariants p^2=p'^2=m^2 and p·p'=m^2(1-z/2).
    """
    from qedcalc.operations.ibp import IntegralFamily, sp_atom

    D = sp.Symbol("D") if D is None else sp.sympify(D)
    z = sp.Symbol("z") if z is None else sp.sympify(z)
    m2 = sp.Symbol("m2") if mass_squared is None else sp.sympify(mass_squared)
    K,L,H,E1,E2,E3,E4 = sp.symbols("K L H E1 E2 E3 E4")

    kk = sp_atom("k","k")
    ll = sp_atom("l","l")
    kl = sp_atom("k","l")
    kpp = sp_atom("k","p'")
    kp = sp_atom("k","p")
    lpp = sp_atom("l","p'")
    lp = sp_atom("l","p")

    denominator_exprs = (
        -kk,
        -ll,
        -(kk + ll + 2*kl),
        2*kpp - kk,
        2*kpp + 2*lpp - kk - ll - 2*kl,
        2*kp + 2*lp - kk - ll - 2*kl,
        2*kp - kk,
    )
    rules = {
        kk: -K,
        ll: -L,
        kl: (K+L-H)/2,
        kpp: (E1-K)/2,
        kp: (E4-K)/2,
        lpp: (E2-H-E1+K)/2,
        lp: (E3-H-E4+K)/2,
        sp_atom("p","p"): m2,
        sp_atom("p'","p'"): m2,
        sp_atom("p","p'"): m2*(1-z/2),
    }
    return IntegralFamily(
        name="ordinary_ladder",
        denominator_names=("K","L","H","E1","E2","E3","E4"),
        denominator_exprs=denominator_exprs,
        loop_momenta=("k","l"),
        external_momenta=("p","p'"),
        scalar_product_rules=rules,
        dimension_symbol=D,
    )


def ladder_ibp_seed_equations(index=None, D=None, z=None, mass_squared=None):
    """Generate the eight canonical IBPs for one ordinary-ladder seed.

    For each derivative loop k,l use vectors k,l,p,p'.
    """
    from qedcalc.operations.ibp import IntegralIndex, generate_ibp_system
    family = ordinary_ladder_ibp_family(D=D, z=z, mass_squared=mass_squared)
    if index is None:
        index = IntegralIndex((1,1,0,1,1,1,1))
    elif isinstance(index, LadderIntegralIndex):
        index = IntegralIndex(index.as_tuple())
    return family, generate_ibp_system(family, (index,), vectors=("k","l","p","p'"))


# --- v0.29: ordinary-ladder family symmetries ---
def ordinary_ladder_integral_symmetries():
    """Return the four-element denominator-permutation symmetry group.

    Generators:
      * external exchange p <-> p': E1<->E4, E2<->E3;
      * loop reparametrization k -> k+l, l -> -l:
        K<->H, E1<->E2, E3<->E4.
    """
    from qedcalc.operations.ibp import IntegralSymmetry, close_symmetry_group
    external_exchange = IntegralSymmetry(
        "external_exchange",
        (0, 1, 2, 6, 5, 4, 3),
    )
    loop_reparametrization = IntegralSymmetry(
        "loop_reparametrization",
        (2, 1, 0, 4, 3, 6, 5),
    )
    return close_symmetry_group((external_exchange, loop_reparametrization), size=7)


def canonicalize_ordinary_ladder_integral(index):
    """Canonical representative of an ordinary-ladder integral under graph symmetries."""
    from qedcalc.operations.ibp import canonicalize_integral
    return canonicalize_integral(index, ordinary_ladder_integral_symmetries())
