import sympy as sp
import pytest

from qedcalc.core.expression import (
    Symbol, Vector, Index, Gamma, Product, NCProduct, ScalarProduct,
)
from qedcalc.operations.topology_amplitude import (
    TopologyFactor, QEDAmplitudeTemplate, build_bare_amplitude,
    build_contracted_amplitude,
)
from qedcalc.operations.subdiagram import Subdiagram
from qedcalc.operations.forest import contract_graph
from qedcalc.operations.multiloop import complete_multiloop_square, symmetric_multiloop_tensor
from qedcalc.latex.renderer import render_latex


def test_bare_amplitude_template_preserves_noncommutative_order():
    mu = Index('mu', 'down')
    rho = Index('rho', 'up')
    tpl = QEDAmplitudeTemplate('G', [
        TopologyFactor('v1', Gamma(rho)),
        TopologyFactor('s1', Symbol('S1')),
        TopologyFactor('v2', Gamma(mu)),
        TopologyFactor('d1', Symbol('D1'), commutative=True),
    ])
    built = build_bare_amplitude(tpl)
    assert isinstance(built.expression, Product)
    assert isinstance(built.expression.factors[-1], NCProduct)


def test_contracted_amplitude_replaces_contiguous_subdiagram():
    mu = Index('mu', 'down')
    tpl = QEDAmplitudeTemplate('G', [
        TopologyFactor('a', Symbol('A')),
        TopologyFactor('b', Gamma(mu)),
        TopologyFactor('c', Symbol('C')),
    ])
    sub = Subdiagram('gamma', 'vertex', 1, {'b'})
    cg = contract_graph('G', tpl.member_ids, (sub,))
    built = build_contracted_amplitude(tpl, cg, (sub,), {'gamma': Symbol('CTv')})
    assert 'CT[gamma]' in built.contracted_members
    assert 'CTv' in render_latex(built.expression)


def test_contracted_amplitude_rejects_noncontiguous_guess():
    tpl = QEDAmplitudeTemplate('G', [
        TopologyFactor('a', Symbol('A')),
        TopologyFactor('x', Symbol('X')),
        TopologyFactor('b', Symbol('B')),
    ])
    sub = Subdiagram('gamma', 'vertex', 1, {'a', 'b'})
    cg = contract_graph('G', tpl.member_ids, (sub,))
    with pytest.raises(ValueError, match='not a contiguous block'):
        build_contracted_amplitude(tpl, cg, (sub,), {'gamma': Symbol('CTv')})


def test_mixed_rank2_tensor_reduction_uses_inverse_matrix():
    k, l = Vector('k'), Vector('l')
    expr = Product(
        Symbol('2'), ScalarProduct(k, k),
    )
    # Build a scalar quadratic form: 2 k^2 + 2 l^2 + 2 k.l
    from qedcalc.core.expression import Add, ScalarMul
    quad = Add(
        ScalarMul(2, ScalarProduct(k, k)),
        ScalarMul(2, ScalarProduct(l, l)),
        ScalarMul(2, ScalarProduct(k, l)),
    )
    completed = complete_multiloop_square(quad, loops=('k','l'))
    mu, nu = Index('mu','up'), Index('nu','up')
    reduced = symmetric_multiloop_tensor((('k',mu),('l',nu)), completed, dimension=4)
    text = render_latex(reduced)
    assert 'Q' in text
    assert 'g' in text


def test_mixed_rank4_tensor_reduction_generates_three_pairings():
    k, l = Vector('k'), Vector('l')
    from qedcalc.core.expression import Add, ScalarMul
    quad = Add(
        ScalarMul(2, ScalarProduct(k, k)),
        ScalarMul(3, ScalarProduct(l, l)),
        ScalarMul(2, ScalarProduct(k, l)),
    )
    completed = complete_multiloop_square(quad, loops=('k','l'))
    inds = [Index(x,'up') for x in ('mu','nu','rho','sigma')]
    reduced = symmetric_multiloop_tensor(
        (('k',inds[0]),('l',inds[1]),('k',inds[2]),('l',inds[3])),
        completed, dimension=4,
    )
    text = render_latex(reduced)
    assert text.count('g_{') == 6
