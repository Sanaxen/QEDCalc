from pathlib import Path
import sympy as sp

from qedcalc import render_latex
from qedcalc.config import load_symbol_table, load_conventions
from qedcalc.core.expression import (
    Symbol, Vector, Index, Gamma, Slash, ScalarProduct, Add, ScalarMul,
    Product, NCProduct, Power, Fraction, VectorComponent
)
from qedcalc.history import MarkdownSession
from qedcalc.operations.multiloop import (
    declare_loop_momenta,
    complete_multiloop_square,
    shifted_multiloop_denominator,
    shift_multiloop_momenta_in_numerator,
)
from qedcalc.operations.denominator import feynman_parameterize_n, feynman_parameterize_powers
from qedcalc.operations.integral import euclidean_scalar_loop_integral, dimensional_regularized_loop_series
from qedcalc.operations.loop import symmetric_even_rank
from qedcalc.operations.renormalization import dimreg_scale_factor, renormalized_dimreg_series
from qedcalc.operations.dimreg import bookkeep_uv_ir
from qedcalc.operations.counterterm import (
    make_counterterm, replace_factor_with_counterterm, qed_counterterm_library,
    counterterm_contribution,
)


def main():
    root = Path(__file__).resolve().parents[1]
    symbols = load_symbol_table(root / "symbols.txt")
    conventions = load_conventions(root / "conventions.txt")
    loops = declare_loop_momenta(symbols, ("k", "l"))

    k, l, p, q = Vector("k"), Vector("l"), Vector("p"), Vector("q")
    quadratic = Add(
        ScalarMul(-1, ScalarProduct(k, k)),
        ScalarMul(-1, ScalarProduct(l, l)),
        ScalarProduct(k, l),
        ScalarMul(2, ScalarProduct(k, p)),
        ScalarMul(4, ScalarProduct(l, q)),
        Product(Symbol("m"), Symbol("m")),
    )
    completed = complete_multiloop_square(quadratic, ("k", "l"))
    shifted = shifted_multiloop_denominator(completed, ("ell1", "ell2"))

    mu = Index("mu", "down")
    numerator = NCProduct(Slash(k), Gamma(mu), Slash(l))
    shifted_numerator = shift_multiloop_momenta_in_numerator(
        numerator, completed, ("ell1", "ell2")
    )

    den = Product(*(Symbol(f"D{i}") for i in range(1, 6)))
    fp_unit = feynman_parameterize_n(Fraction(Symbol("N"), den))

    den_powers = Product(
        Power(Symbol("D1"), 2),
        Symbol("D2"),
        Power(Symbol("D3"), 3),
    )
    fp_powers = feynman_parameterize_powers(Fraction(Symbol("N"), den_powers))

    D, Delta, epsilon = sp.symbols("D Delta epsilon", positive=True)
    d_integral = euclidean_scalar_loop_integral(3, 1, D, Delta)
    dr_series = dimensional_regularized_loop_series(2, 0, epsilon, Delta, order=0)

    chain = NCProduct(
        Gamma(Index("rho", "up")),
        Gamma(mu),
        Gamma(Index("rho", "down")),
    )
    vertex_ct = make_counterterm("delta_Z1", Symbol("deltaZ1"), Gamma(mu), 1)
    ct_replacement = replace_factor_with_counterterm(chain, 1, vertex_ct)

    # General even-rank tensor reduction (rank 6 example).
    rank6_indices = [Index(x, "up") for x in ("mu", "nu", "rho", "sigma", "alpha", "beta")]
    rank6_input = Product(*(VectorComponent(Vector("ell1"), idx) for idx in rank6_indices))
    rank6_reduced = symmetric_even_rank(rank6_input, "ell1", 4)

    # Explicit dimensional-regularization convention layer.
    mu_scale = sp.Symbol("mu_R", positive=True)
    msbar_scale = dimreg_scale_factor(2, epsilon, mu_scale, conventions=conventions)
    bare_example = 1/epsilon + sp.Symbol("C0")
    msbar_example = renormalized_dimreg_series(
        bare_example, 2, epsilon, mu_scale, conventions=conventions, expansion_order=0
    )

    # Independent UV/IR bookkeeping, including mixed poles.
    eps_uv, eps_ir = sp.symbols("epsilon_UV epsilon_IR")
    uvir_input = sp.Symbol("A")/eps_uv**2 + sp.Symbol("B")/eps_ir + sp.Symbol("C")/(eps_uv*eps_ir) + sp.Symbol("F")
    uvir = bookkeep_uv_ir(uvir_input)

    # Standard QED counterterm building blocks.
    ct_library = qed_counterterm_library("mu", "nu", "p", "k", 1)

    print("=== QEDCalc multi-loop foundation demo ===")
    print("Loop momenta:", render_latex(loops))
    print("Completed quadratic form:", render_latex(completed))
    print("Shifted denominator:", render_latex(shifted))
    print("Shifted numerator:", render_latex(shifted_numerator))
    print("Unit-power Feynman parameterization:", render_latex(fp_unit))
    print("General-power Feynman parameterization:", render_latex(fp_powers))
    print("D-dimensional scalar loop integral:", sp.sstr(d_integral))
    print("D=4-2 epsilon Laurent series:", sp.sstr(dr_series))
    print("Counterterm replacement:", render_latex(ct_replacement.result))
    print("Rank-6 tensor reduction:", render_latex(rank6_reduced))
    print("Two-loop MS-bar scale factor:", sp.sstr(msbar_scale))
    print("MS-bar subtracted example:", sp.sstr(msbar_example["subtracted"]))
    print("UV terms:", sp.sstr(sum(uvir.uv_terms)))
    print("IR terms:", sp.sstr(sum(uvir.ir_terms)))
    print("Mixed UV/IR terms:", sp.sstr(sum(uvir.mixed_terms)))

    out = root / "output" / "multiloop_foundation.md"
    session = MarkdownSession(out, "QEDCalc multi-loop foundation demo")
    session.text("Loaded conventions", conventions.to_markdown())
    session.text(
        "Purpose",
        "Reusable algebra foundation for two-loop and higher-loop calculations. "
        "This demo verifies individual processing functions; it is not yet a complete two-loop diagram evaluation.",
    )
    session.equation("Declared loop momenta", loops)
    session.equation("Input quadratic form", quadratic)
    session.equation("Matrix square completion", completed)
    session.equation("Shifted quadratic denominator", shifted)
    session.equation("Input two-loop numerator", numerator)
    session.equation("Simultaneously shifted numerator", shifted_numerator)
    session.equation("Five-denominator unit-power Feynman parameterization", fp_unit)
    session.equation("General denominator-power Feynman parameterization", fp_powers)
    session.equation("General D-dimensional Euclidean scalar loop integral", sp.latex(d_integral))
    session.equation("Dimensional-regularization example around D=4-2 epsilon", sp.latex(dr_series.removeO()))
    session.equation("Vertex counterterm", vertex_ct)
    session.equation("Explicit counterterm replacement result", ct_replacement.result)
    session.equation("General rank-6 symmetric tensor reduction", rank6_reduced)
    session.equation("Two-loop MS-bar scale factor", sp.latex(msbar_scale))
    session.equation("MS-bar Laurent series before subtraction", sp.latex(msbar_example["series"]))
    session.equation("MS-bar pole part", sp.latex(msbar_example["pole_part"]))
    session.equation("MS-bar result after minimal subtraction", sp.latex(msbar_example["subtracted"]))
    session.equation("UV pole bookkeeping", sp.latex(sum(uvir.uv_terms)))
    session.equation("IR pole bookkeeping", sp.latex(sum(uvir.ir_terms)))
    session.equation("Mixed UV/IR pole bookkeeping", sp.latex(sum(uvir.mixed_terms)))
    for name, ct in ct_library.items():
        session.equation(f"QED counterterm library: {name}", counterterm_contribution(ct))
    session.save()
    print(f"Markdown session written to: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
