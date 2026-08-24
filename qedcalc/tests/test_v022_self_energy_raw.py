from pathlib import Path
import sympy as sp

from qedcalc import parse_loop_integral_latex, render_latex
from qedcalc.operations.bare_diagram import (
    find_self_energy_subdiagrams,
    contract_self_energy_subdiagram,
    contract_self_energy_to_outer_loop,
)
from qedcalc.operations.self_energy import uv_cancellation_numerator

ROOT = Path(__file__).resolve().parents[1]


def _diagram(name):
    return parse_loop_integral_latex((ROOT / "input" / name).read_text(encoding="utf-8"))


def test_raw_right_self_energy_detection():
    d = _diagram("self_energy_insertion_right_2loop_bare.tex")
    m = find_self_energy_subdiagrams(d)
    assert len(m) == 1
    assert m[0].side == "right"
    assert m[0].loop_momentum.name == "l"
    assert "p" in render_latex(m[0].external_momentum)


def test_raw_left_self_energy_detection():
    d = _diagram("self_energy_insertion_left_2loop_bare.tex")
    m = find_self_energy_subdiagrams(d)
    assert len(m) == 1
    assert m[0].side == "left"
    assert m[0].loop_momentum.name == "l"
    assert "p'" in render_latex(m[0].external_momentum)


def test_raw_self_energy_numerator_is_canonical():
    d = _diagram("self_energy_insertion_right_2loop_bare.tex")
    r = contract_self_energy_subdiagram(d)
    text = render_latex(r.reduced_numerator)
    assert r"\rlap{/}l" in text
    assert r"\rlap{/}" in text
    assert "4" in text and "2" in text


def test_contracted_outer_loop_removes_subloop_measure():
    d = _diagram("self_energy_insertion_right_2loop_bare.tex")
    compact = contract_self_energy_to_outer_loop(
        d,
        outer_prefactor_latex=r"\frac{e^2}{(2\pi)^4 i}",
        renormalized=True,
    )
    assert [v.name for v in compact.loops] == ["k"]
    text = render_latex(compact)
    assert r"\Sigma_R^{(1)}" in text
    assert r"d^{4}l" not in text


def test_raw_bridge_only_promotes_to_sigma_r_after_uv_check():
    a, m, rslash = sp.symbols("a m rslash")
    assert sp.simplify(uv_cancellation_numerator(a, m, rslash)) == 0
    d = _diagram("self_energy_insertion_left_2loop_bare.tex")
    compact = contract_self_energy_to_outer_loop(
        d,
        outer_prefactor_latex=r"\frac{e^2}{(2\pi)^4 i}",
        renormalized=True,
    )
    assert r"\Sigma_R^{(1)}" in render_latex(compact)


def test_compact_outer_prefactor_can_come_from_conventions():
    from qedcalc.config.conventions import load_conventions
    cfg = load_conventions()
    diagram = parse_loop_integral_latex((ROOT / "input/self_energy_insertion_right_2loop_bare.tex").read_text(encoding="utf-8"))
    compact = contract_self_energy_to_outer_loop(diagram, conventions=cfg, renormalized=False)
    assert compact.prefactor_latex == cfg.compact_outer_one_loop_prefactor_latex()


def test_raw_self_energy_rejects_unsupported_covariant_gauge():
    import pytest
    from qedcalc.config.conventions import QEDConventions
    diagram = parse_loop_integral_latex((ROOT / "input/self_energy_insertion_right_2loop_bare.tex").read_text(encoding="utf-8"))
    cfg = QEDConventions(gauge="covariant").validate()
    with pytest.raises(NotImplementedError, match="gauge=feynman"):
        contract_self_energy_subdiagram(diagram, conventions=cfg)
