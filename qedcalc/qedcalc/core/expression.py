from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple

class QEDExpr:
    def walk(self):
        yield self

@dataclass(frozen=True)
class Symbol(QEDExpr):
    name: str

@dataclass(frozen=True)
class Vector(QEDExpr):
    name: str

@dataclass(frozen=True)
class Index(QEDExpr):
    name: str
    position: str = "up"
    def flipped(self):
        return Index(self.name, "down" if self.position == "up" else "up")

@dataclass(frozen=True)
class Gamma(QEDExpr):
    index: Index

@dataclass(frozen=True)
class Metric(QEDExpr):
    left: Index
    right: Index

@dataclass(frozen=True)
class Slash(QEDExpr):
    arg: QEDExpr

@dataclass(frozen=True)
class ScalarProduct(QEDExpr):
    left: QEDExpr
    right: QEDExpr

@dataclass(frozen=True)
class VectorComponent(QEDExpr):
    vector: QEDExpr
    index: Index

@dataclass(frozen=True)
class Product(QEDExpr):
    factors: Tuple[QEDExpr, ...]
    def __init__(self, *factors):
        flat = []
        for f in factors:
            flat.extend(f.factors if isinstance(f, Product) else [f])
        object.__setattr__(self, "factors", tuple(flat))
    def walk(self):
        yield self
        for f in self.factors:
            yield from f.walk()


@dataclass(frozen=True)
class VectorLinearCombination(QEDExpr):
    terms: Tuple[Tuple[QEDExpr, Vector], ...]
    def walk(self):
        yield self
        for coeff, vec in self.terms:
            yield from coeff.walk()
            yield from vec.walk()

@dataclass(frozen=True)
class CompletedSquare(QEDExpr):
    loop: Vector
    shift: VectorLinearCombination
    remainder: QEDExpr
    quadratic_sign: int = -1
    def walk(self):
        yield self
        yield from self.loop.walk()
        yield from self.shift.walk()
        yield from self.remainder.walk()

@dataclass(frozen=True)
class Power(QEDExpr):
    base: QEDExpr
    exponent: int

@dataclass(frozen=True)
class Fraction(QEDExpr):
    numerator: QEDExpr
    denominator: QEDExpr
    def walk(self):
        yield self
        yield from self.numerator.walk()
        yield from self.denominator.walk()

@dataclass(frozen=True)
class FermionPropagator(QEDExpr):
    denominator: QEDExpr
    def walk(self):
        yield self
        yield from self.denominator.walk()

@dataclass(frozen=True)
class FeynmanParamIntegral(QEDExpr):
    parameters: Tuple[Symbol, ...]
    numerator: QEDExpr
    combined_denominator: QEDExpr
    power: int
    prefactor: int = 1
    def walk(self):
        yield self
        yield from self.numerator.walk()
        yield from self.combined_denominator.walk()

@dataclass(frozen=True)
class PhotonPropagator(QEDExpr):
    numerator: QEDExpr
    denominator: QEDExpr
    def walk(self):
        yield self
        yield from self.numerator.walk()
        yield from self.denominator.walk()



@dataclass(frozen=True)
class SpinorSandwich(QEDExpr):
    """An operator expression between on-shell external Dirac spinors."""
    operator: QEDExpr
    outgoing: Vector
    incoming: Vector
    def walk(self):
        yield self
        yield from self.operator.walk()

@dataclass(frozen=True)
class PauliTerm(QEDExpr):
    """The magnetic structure i sigma_{mu nu} q^nu."""
    index: Index
    momentum: Vector

@dataclass(frozen=True)
class FormFactorDecomposition(QEDExpr):
    """Coefficients of gamma_mu and i sigma_{mu nu} q^nu/(2m)."""
    index: Index
    momentum_transfer: Vector
    f1: QEDExpr
    f2: QEDExpr
    mass: Symbol
    def walk(self):
        yield self
        yield from self.f1.walk()
        yield from self.f2.walk()


@dataclass(frozen=True)
class LoopMomentumSet(QEDExpr):
    """Declared loop momenta for a multi-loop calculation."""
    momenta: Tuple[Vector, ...]

    def walk(self):
        yield self
        for momentum in self.momenta:
            yield from momentum.walk()


@dataclass(frozen=True)
class MultiLoopCompletedSquare(QEDExpr):
    """Matrix square completion for several loop momenta.

    The original quadratic form convention is
        K^T M K + 2 K.B + C.
    The completed form is
        (K + S)^T M (K + S) + remainder,
    where S = M^{-1} B.
    """
    loops: Tuple[Vector, ...]
    matrix: Tuple[Tuple[QEDExpr, ...], ...]
    shifts: Tuple[VectorLinearCombination, ...]
    remainder: QEDExpr

    def walk(self):
        yield self
        for loop in self.loops:
            yield from loop.walk()
        for row in self.matrix:
            for item in row:
                yield from item.walk()
        for shift in self.shifts:
            yield from shift.walk()
        yield from self.remainder.walk()


@dataclass(frozen=True)
class PoleTerm(QEDExpr):
    """A dimensional-regularization pole such as c/epsilon_UV^n."""
    kind: str
    order: int
    coefficient: QEDExpr
    regulator: str = "epsilon"

    def walk(self):
        yield self
        yield from self.coefficient.walk()


@dataclass(frozen=True)
class LaurentResult(QEDExpr):
    """Finite part plus separated UV/IR Laurent poles."""
    finite: QEDExpr
    poles: Tuple[PoleTerm, ...]

    def walk(self):
        yield self
        yield from self.finite.walk()
        for pole in self.poles:
            yield from pole.walk()


@dataclass(frozen=True)
class Counterterm(QEDExpr):
    """Named counterterm contribution with an explicit coefficient and structure."""
    name: str
    coefficient: QEDExpr
    structure: QEDExpr
    loop_order: int = 1

    def walk(self):
        yield self
        yield from self.coefficient.walk()
        yield from self.structure.walk()

@dataclass(frozen=True)
class ScalarMul(QEDExpr):
    coeff: object
    expr: QEDExpr
    def walk(self):
        yield self
        yield from self.expr.walk()

@dataclass(frozen=True)
class Add(QEDExpr):
    terms: Tuple[QEDExpr, ...]
    def __init__(self, *terms):
        flat = []
        for t in terms:
            flat.extend(t.terms if isinstance(t, Add) else [t])
        object.__setattr__(self, "terms", tuple(flat))
    def walk(self):
        yield self
        for t in self.terms:
            yield from t.walk()

@dataclass(frozen=True)
class NCProduct(QEDExpr):
    factors: Tuple[QEDExpr, ...]
    def __init__(self, *factors):
        flat = []
        for f in factors:
            flat.extend(f.factors if isinstance(f, NCProduct) else [f])
        object.__setattr__(self, "factors", tuple(flat))
    def walk(self):
        yield self
        for f in self.factors:
            yield from f.walk()

def neg(expr: QEDExpr) -> QEDExpr:
    return ScalarMul(-1, expr)



@dataclass(frozen=True)
class DiracTrace(QEDExpr):
    """Explicit Dirac trace container parsed from LaTeX."""
    argument: QEDExpr

    def walk(self):
        yield self
        yield from self.argument.walk()


@dataclass(frozen=True)
class LoopIntegralExpression(QEDExpr):
    """Bare multi-loop integral with a preserved scalar normalization string.

    The normalization is kept as LaTeX text deliberately: early raw-diagram
    parsing is intended to preserve the user's exact convention while the
    integrand is converted to QEDCalc's structural expression tree.
    """
    prefactor_latex: str
    loops: Tuple[Vector, ...]
    integrand: QEDExpr
    dimension: object = 4

    def walk(self):
        yield self
        for loop in self.loops:
            yield from loop.walk()
        yield from self.integrand.walk()



@dataclass(frozen=True)
class SelfEnergySubdiagram(QEDExpr):
    """Open one-loop electron self-energy subdiagram.

    ``external_momentum`` is the momentum flowing through the repeated outer
    fermion propagators.  ``loop_momentum`` identifies the internal photon
    loop.  The object is a structural marker used when a bare two-loop chain
    is contracted to ``S Sigma S``.
    """
    external_momentum: QEDExpr
    loop_momentum: Vector
    order: int = 1
    renormalized: bool = False

    def walk(self):
        yield self
        yield from self.external_momentum.walk()
        yield from self.loop_momentum.walk()


@dataclass(frozen=True)
class GeneralFeynmanParamIntegral(QEDExpr):
    """Feynman parameterization for arbitrary positive integer denominator powers.

    Represents
        prefactor * int_simplex weight(x) * numerator / combined_denominator^total_power.
    """
    parameters: Tuple[Symbol, ...]
    numerator: QEDExpr
    combined_denominator: QEDExpr
    total_power: int
    exponents: Tuple[int, ...]
    parameter_weight: QEDExpr
    prefactor: QEDExpr

    def walk(self):
        yield self
        yield from self.numerator.walk()
        yield from self.combined_denominator.walk()
        yield from self.parameter_weight.walk()
        yield from self.prefactor.walk()


@dataclass(frozen=True)
class CountertermInsertion(QEDExpr):
    """A counterterm replacement/insert operation recorded with its result."""
    counterterm: Counterterm
    factor_index: int
    mode: str
    result: QEDExpr

    def walk(self):
        yield self
        yield from self.counterterm.walk()
        yield from self.result.walk()
