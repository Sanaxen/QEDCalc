from qedcalc.core.expression import (
    QEDExpr, ScalarProduct, Vector, Symbol, Power, Add, Product, NCProduct, ScalarMul, Fraction
)

def apply_scalar_onshell(expr: QEDExpr, mass_name="m"):
    """
    Replace p.p and p'.p' by m^2.
    In v0.1 m^2 is kept as a symbolic token 'm^2' for rendering simplicity.
    """
    if isinstance(expr, ScalarProduct):
        if (
            isinstance(expr.left, Vector) and isinstance(expr.right, Vector)
            and expr.left.name == expr.right.name
            and expr.left.name in ("p", "p'")
        ):
            return Power(Symbol(mass_name), 2)
        return expr

    if isinstance(expr, Add):
        return Add(*(apply_scalar_onshell(t, mass_name) for t in expr.terms))
    if isinstance(expr, Product):
        return Product(*(apply_scalar_onshell(f, mass_name) for f in expr.factors))
    if isinstance(expr, Fraction):
        return Fraction(apply_scalar_onshell(expr.numerator, mass_name), apply_scalar_onshell(expr.denominator, mass_name))
    if isinstance(expr, NCProduct):
        return NCProduct(*(apply_scalar_onshell(f, mass_name) for f in expr.factors))
    if isinstance(expr, ScalarMul):
        return ScalarMul(expr.coeff, apply_scalar_onshell(expr.expr, mass_name))
    return expr
