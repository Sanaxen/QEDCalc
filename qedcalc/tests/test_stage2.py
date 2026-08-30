from qedcalc import parse_latex, render_latex, Fraction, Metric
from qedcalc.history import MarkdownSession
from pathlib import Path

def test_fraction_parse():
    e = parse_latex(r"\frac{1}{m-\rlap{/}p+\rlap{/}k-i\varepsilon}")
    assert isinstance(e, Fraction)
    out = render_latex(e)
    assert r"\frac" in out and r"\rlap{/}p" in out

def test_metric_parse():
    e = parse_latex(r"g_{\rho\sigma}")
    assert isinstance(e, Metric)
    assert render_latex(e) == r"g_{\rho\sigma}"

def test_markdown_blank_lines(tmp_path):
    p = tmp_path / "x.md"
    s = MarkdownSession(p)
    s.equation("Eq", r"a=b")
    s.save()
    text = p.read_text(encoding="utf-8")
    assert "## Eq\n\n$$\na=b\n$$\n" in text

def test_metric_indices_are_counted():
    from qedcalc.validation.validator import validate_indices
    e = parse_latex(r"\gamma^\rho\gamma^\sigma g_{\rho\sigma}")
    msgs = {m.message for m in validate_indices(e)}
    assert any("rho: appears twice" in m for m in msgs)
    assert any("sigma: appears twice" in m for m in msgs)
