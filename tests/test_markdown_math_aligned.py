from qedcalc.reporting import format_markdown_math_aligned


def test_outer_left_right_group_is_kept_balanced():
    source = r'''$$
-\left(
-2(m m \gamma_{\mu})
+ 4(m p_{\mu})
- 4(m x p'_{\mu} + m y p_{\mu})
+ 4(m p'_{\mu})
- 2(2(p'_{\mu}m))
+ 8(y p_{\mu})
\right)
$$'''

    out = format_markdown_math_aligned(source, max_width=32)

    assert r"\begin{aligned}" in out
    assert r"\end{aligned}" in out
    assert out.count(r"\left(") == out.count(r"\right)") == 1
    assert out.index(r"\left(") < out.index(r"\begin{aligned}")
    assert out.index(r"\end{aligned}") < out.index(r"\right)")
    assert "E_{" not in out


def test_continuation_rows_do_not_start_with_operators():
    source = r'''$$
A = a + b + c + d + e + f + g
$$'''

    out = format_markdown_math_aligned(source, max_width=12)
    inside = out.split(r"\begin{aligned}", 1)[1].split(r"\end{aligned}", 1)[0]
    rows = [row.strip() for row in inside.split(r"\\") if row.strip()]

    for row in rows[1:]:
        visible = row.lstrip("&").lstrip()
        if visible.startswith(r"\quad"):
            visible = visible[len(r"\quad"):].lstrip()
        assert not visible.startswith(("=", "+", "-", r"\times", r"\cdot"))


def test_indivisible_long_group_is_left_unchanged_not_cut():
    source = r'''$$
\left(\frac{abcdefghijklmnopqrstuvwxyz}{012345678901234567890123456789}\right)
$$'''

    out = format_markdown_math_aligned(source, max_width=10)

    assert out.count(r"\left(") == 1
    assert out.count(r"\right)") == 1
    assert r"\begin{aligned}" not in out
    assert "E_{" not in out
