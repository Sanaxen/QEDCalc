from pathlib import Path
import pytest

from qedcalc import parse_latex, render_latex
from qedcalc.config import load_symbol_table


def write_symbols(tmp_path: Path, text: str):
    p = tmp_path / "symbols.txt"
    p.write_text(text, encoding="utf-8")
    return p


def test_custom_vector_and_index_are_accepted(tmp_path):
    path = write_symbols(tmp_path, r'''
[Scalar]
m
\varepsilon

[Constants]
i

[Vector]
a
q

[Index]
\omega
\eta
''')
    table = load_symbol_table(path)
    expr = parse_latex(
        r"\gamma^\omega\frac{1}{m-\rlap{/}a+\rlap{/}q-i\varepsilon}\gamma_\eta g_{\omega\eta}",
        symbol_table=table,
    )
    out = render_latex(expr)
    assert r"\gamma^{\omega}" in out
    assert r"\rlap{/}a" in out
    assert r"\rlap{/}q" in out
    assert r"g_{\omega\eta}" in out


def test_unknown_index_is_error(tmp_path):
    path = write_symbols(tmp_path, r'''
[Scalar]
m
[Constants]
i
[Vector]
p
[Index]
\mu
''')
    table = load_symbol_table(path)
    with pytest.raises(ValueError, match=r"Undefined Index"):
        parse_latex(r"\gamma^\omega", symbol_table=table)


def test_unknown_vector_in_slash_is_error(tmp_path):
    path = write_symbols(tmp_path, r'''
[Scalar]
m
[Constants]
i
[Vector]
p
[Index]
\mu
''')
    table = load_symbol_table(path)
    with pytest.raises(ValueError, match=r"Undefined Vector"):
        parse_latex(r"\rlap{/}q", symbol_table=table)


def test_same_greek_can_be_scalar_and_index(tmp_path):
    path = write_symbols(tmp_path, r'''
[Scalar]
\alpha
[Constants]
i
[Vector]
p
[Index]
\alpha
''')
    table = load_symbol_table(path)
    scalar = parse_latex(r"\alpha", symbol_table=table)
    index = parse_latex(r"\gamma^\alpha", symbol_table=table)
    assert render_latex(scalar) == r"\alpha"
    assert render_latex(index) == r"\gamma^{\alpha}"
