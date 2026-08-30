from pathlib import Path
from qedcalc import parse_latex, parse_loop_integral_latex, render_latex
from qedcalc.core.expression import DiracTrace, VectorComponent
from qedcalc.operations.bare_diagram import find_dirac_traces, reduce_single_trace_from_loop_integral_4d
from qedcalc.operations.vacuum_polarization import reduce_vp_subdiagram_from_bare_2loop_4d

ROOT = Path(__file__).resolve().parents[1]


def test_vector_component_parse_and_render():
    expr = parse_latex(r"k_\rho")
    assert isinstance(expr, VectorComponent)
    assert render_latex(expr) == r"k_{\rho}"


def test_dirac_trace_parse_and_render():
    expr = parse_latex(r"\operatorname{tr}\left[\gamma^\alpha\gamma^\beta\right]")
    assert isinstance(expr, DiracTrace)
    text = render_latex(expr)
    assert r"\operatorname{tr}" in text
    assert r"\gamma^{\alpha}" in text


def test_parse_raw_two_loop_vp_integral():
    source = (ROOT / "input" / "vacuum_polarization_2loop_bare.tex").read_text(encoding="utf-8")
    diagram = parse_loop_integral_latex(source)
    assert [v.name for v in diagram.loops] == ["k", "l"]
    assert diagram.dimension == 4
    assert diagram.prefactor_latex.startswith(r"-\frac{e^4}")
    assert len(find_dirac_traces(diagram.integrand)) == 1


def test_reduce_trace_directly_from_raw_two_loop_vp():
    source = (ROOT / "input" / "vacuum_polarization_2loop_bare.tex").read_text(encoding="utf-8")
    diagram = parse_loop_integral_latex(source)
    reduction = reduce_single_trace_from_loop_integral_4d(diagram)
    rendered = render_latex(reduction.traced_numerator)
    assert r"g_{\alpha\beta}" in rendered
    assert r"l^{\alpha}" in rendered
    assert r"k^{\alpha}" in rendered


def test_bare_vp_bridge_reaches_tensor_reduction():
    source = (ROOT / "input" / "vacuum_polarization_2loop_bare.tex").read_text(encoding="utf-8")
    diagram = parse_loop_integral_latex(source)
    result = reduce_vp_subdiagram_from_bare_2loop_4d(diagram)
    assert result.tensor_reduced_trace_numerator is not None
    text = render_latex(result.tensor_reduced_trace_numerator)
    assert "r" in text or "k" in text
