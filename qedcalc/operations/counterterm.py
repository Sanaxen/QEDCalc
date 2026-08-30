from __future__ import annotations

from qedcalc.core.expression import QEDExpr, Counterterm, Product, Add
from qedcalc.operations.simplify import simplify_expression


def make_counterterm(name: str, coefficient: QEDExpr, structure: QEDExpr, loop_order=1):
    if loop_order < 1:
        raise ValueError("loop_order must be at least 1.")
    return Counterterm(name, coefficient, structure, loop_order)


def counterterm_contribution(term: Counterterm):
    """Convert a Counterterm object into its algebraic contribution."""
    if not isinstance(term, Counterterm):
        raise TypeError("counterterm_contribution expects Counterterm.")
    return simplify_expression(Product(term.coefficient, term.structure))


def add_counterterms(expr: QEDExpr, *terms: Counterterm):
    """Add explicit counterterm contributions without hiding their origin."""
    additions = [counterterm_contribution(t) for t in terms]
    return simplify_expression(Add(expr, *additions))


def replace_factor_with_counterterm(expr: QEDExpr, factor_index: int, term: Counterterm):
    """Replace one top-level Product/NCProduct factor by a counterterm contribution.

    This is intentionally explicit: QEDCalc never guesses which vertex or
    propagator should receive a counterterm.  The caller selects the factor.
    """
    from qedcalc.core.expression import NCProduct, CountertermInsertion
    if not isinstance(term, Counterterm):
        raise TypeError("term must be a Counterterm.")
    if isinstance(expr, NCProduct):
        factors = list(expr.factors)
        constructor = NCProduct
    elif isinstance(expr, Product):
        factors = list(expr.factors)
        constructor = Product
    else:
        raise TypeError("Counterterm replacement requires a top-level Product or NCProduct.")
    if factor_index < 0 or factor_index >= len(factors):
        raise IndexError("factor_index is outside the factor chain.")
    factors[factor_index] = counterterm_contribution(term)
    result = simplify_expression(constructor(*factors))
    return CountertermInsertion(term, factor_index, "replace", result)


def insert_counterterm_factor(expr: QEDExpr, factor_index: int, term: Counterterm, before=True):
    """Insert a counterterm contribution before/after a selected top-level factor."""
    from qedcalc.core.expression import NCProduct, CountertermInsertion
    if not isinstance(term, Counterterm):
        raise TypeError("term must be a Counterterm.")
    if isinstance(expr, NCProduct):
        factors = list(expr.factors)
        constructor = NCProduct
    elif isinstance(expr, Product):
        factors = list(expr.factors)
        constructor = Product
    else:
        raise TypeError("Counterterm insertion requires a top-level Product or NCProduct.")
    if factor_index < 0 or factor_index >= len(factors):
        raise IndexError("factor_index is outside the factor chain.")
    pos = factor_index if before else factor_index + 1
    factors.insert(pos, counterterm_contribution(term))
    result = simplify_expression(constructor(*factors))
    mode = "insert_before" if before else "insert_after"
    return CountertermInsertion(term, factor_index, mode, result)


def qed_vertex_counterterm(index, coefficient=None, loop_order=1):
    """Return the QED vertex counterterm delta_Z1 gamma_mu."""
    from qedcalc.core.expression import Symbol, Gamma, Index
    if isinstance(index, str):
        index = Index(index, "down")
    coeff = Symbol("deltaZ1") if coefficient is None else coefficient
    return make_counterterm("delta_Z1", coeff, Gamma(index), loop_order)


def qed_electron_wavefunction_counterterm(momentum="p", coefficient=None, loop_order=1):
    """Return the electron kinetic counterterm delta_Z2 slash(p)."""
    from qedcalc.core.expression import Symbol, Slash, Vector
    p = Vector(momentum) if isinstance(momentum, str) else momentum
    coeff = Symbol("deltaZ2") if coefficient is None else coefficient
    return make_counterterm("delta_Z2", coeff, Slash(p), loop_order)


def qed_mass_counterterm(coefficient=None, loop_order=1):
    """Return the scalar electron mass counterterm delta_m * 1."""
    from qedcalc.core.expression import Symbol
    coeff = Symbol("delta_m") if coefficient is None else coefficient
    return make_counterterm("delta_m", coeff, Symbol("1"), loop_order)


def qed_photon_wavefunction_counterterm(mu, nu, momentum="k", coefficient=None, loop_order=1):
    r"""Return delta_Z3 [k^2 g_{mu nu} - k_mu k_nu]."""
    from qedcalc.core.expression import (
        Symbol, Vector, Index, Metric, ScalarProduct, VectorComponent,
        Add, Product, ScalarMul
    )
    if isinstance(mu, str):
        mu = Index(mu, "down")
    if isinstance(nu, str):
        nu = Index(nu, "down")
    k = Vector(momentum) if isinstance(momentum, str) else momentum
    coeff = Symbol("deltaZ3") if coefficient is None else coefficient
    structure = Add(
        Product(ScalarProduct(k, k), Metric(mu, nu)),
        ScalarMul(-1, Product(VectorComponent(k, mu), VectorComponent(k, nu))),
    )
    return make_counterterm("delta_Z3", coeff, structure, loop_order)


def qed_counterterm_library(index="mu", photon_index="nu", electron_momentum="p",
                            photon_momentum="k", loop_order=1):
    """Return the standard QED counterterm building blocks used by QEDCalc."""
    return {
        "vertex": qed_vertex_counterterm(index, loop_order=loop_order),
        "electron_wavefunction": qed_electron_wavefunction_counterterm(electron_momentum, loop_order=loop_order),
        "mass": qed_mass_counterterm(loop_order=loop_order),
        "photon_wavefunction": qed_photon_wavefunction_counterterm(index, photon_index, photon_momentum, loop_order=loop_order),
    }
