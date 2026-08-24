__version__ = "0.51.0"

from .core.expression import (
    QEDExpr, Symbol, Vector, Index, Gamma, Metric, Slash, ScalarProduct, VectorComponent, Product,
    Add, NCProduct, ScalarMul, Power, FeynmanParamIntegral, Fraction, FermionPropagator, PhotonPropagator, SpinorSandwich, PauliTerm, FormFactorDecomposition, LoopMomentumSet, MultiLoopCompletedSquare, PoleTerm, LaurentResult, Counterterm, GeneralFeynmanParamIntegral, CountertermInsertion, SelfEnergySubdiagram
)
from .parser.qed_latex import parse_latex, parse_loop_integral_latex
from .latex.renderer import render_latex

from .core.expression import DiracTrace, LoopIntegralExpression

from .config import QEDConventions, load_conventions, default_conventions_path
