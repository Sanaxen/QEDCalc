from pathlib import Path
import sympy as sp
import pytest

from qedcalc.config.conventions import QEDConventions, load_conventions
from qedcalc.operations.renormalization import dimreg_scale_factor


def test_default_project_conventions_load():
    cfg = load_conventions()
    assert cfg.metric_signature == "+---"
    assert cfg.gauge == "feynman"
    assert cfg.renormalization_scheme == "on_shell"
    assert cfg.dimreg_subtraction == "MSbar"
    assert cfg.compact_outer_one_loop_prefactor_latex() == r"\frac{e^{2}}{(2\pi)^4 i}"


def test_normalization_ownership_changes_outer_prefactor():
    cfg = QEDConventions(
        subdiagram_include_coupling=False,
        subdiagram_include_loop_measure=True,
        subdiagram_include_i=True,
    ).validate()
    out = cfg.compact_outer_one_loop_prefactor_latex()
    assert r"e^{4}" in out
    assert r"(2\pi)^4" in out


def test_unknown_convention_key_rejected(tmp_path: Path):
    p = tmp_path / "conventions.txt"
    p.write_text("[X]\nmagic = yes\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Unknown convention key"):
        load_conventions(p)


def test_dimreg_uses_convention_scheme_and_msbar_factor():
    eps, mu = sp.symbols("epsilon mu", positive=True)
    cfg = QEDConventions(dimreg_subtraction="MSbar", msbar_factor=True).validate()
    f = dimreg_scale_factor(1, eps, mu, conventions=cfg)
    assert sp.simplify(f / (mu**(2*eps) * (4*sp.pi*sp.exp(-sp.EulerGamma))**eps)) == 1
    cfg2 = QEDConventions(dimreg_subtraction="MSbar", msbar_factor=False).validate()
    f2 = dimreg_scale_factor(1, eps, mu, conventions=cfg2)
    assert sp.simplify(f2 - mu**(2*eps)) == 0
