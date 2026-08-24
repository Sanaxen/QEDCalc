from pathlib import Path
import sys

from qedcalc import Symbol, Index, Gamma, render_latex, __version__
from qedcalc.core.expression import ScalarMul, Product
from qedcalc.operations.topology_amplitude import (
    TopologyFactor, QEDAmplitudeTemplate, build_bare_amplitude,
    build_contracted_amplitude,
)
from qedcalc.operations.subdiagram import Subdiagram
from qedcalc.operations.forest import contract_graph
from qedcalc.operations.multiloop import complete_multiloop_square, symmetric_multiloop_tensor
from qedcalc.core.expression import Vector, ScalarProduct, Add
from qedcalc.history.markdown_session import MarkdownSession


def main():
    root = Path(__file__).resolve().parents[1]
    out = root / 'output' / 'topology_amplitude_demo.md'

    rho = Index('rho', 'up')
    mu = Index('mu', 'down')
    sigma = Index('sigma', 'down')

    template = QEDAmplitudeTemplate('two_loop_demo', [
        TopologyFactor('vL', Gamma(rho)),
        TopologyFactor('S_left', Symbol('S_left')),
        TopologyFactor('vSub', Gamma(mu)),
        TopologyFactor('S_right', Symbol('S_right')),
        TopologyFactor('vR', Gamma(sigma)),
        TopologyFactor('D_outer', Symbol('D_outer'), commutative=True),
    ])
    bare = build_bare_amplitude(template)

    sub = Subdiagram('vertex_sub', 'vertex', 1, {'vSub'})
    contracted = contract_graph(template.graph_name, template.member_ids, (sub,))
    local_vertex = Product(Symbol('deltaZ1'), Gamma(mu))
    contracted_amp = build_contracted_amplitude(
        template, contracted, (sub,), {'vertex_sub': local_vertex}
    )

    k, l = Vector('k'), Vector('l')
    quadratic = Add(
        ScalarMul(2, ScalarProduct(k, k)),
        ScalarMul(3, ScalarProduct(l, l)),
        ScalarMul(2, ScalarProduct(k, l)),
    )
    completed = complete_multiloop_square(quadratic, loops=('k', 'l'))
    mixed_rank2 = symmetric_multiloop_tensor(
        (('k', Index('alpha', 'up')), ('l', Index('beta', 'up'))),
        completed,
        dimension=4,
    )
    mixed_rank4 = symmetric_multiloop_tensor(
        (
            ('k', Index('alpha', 'up')),
            ('l', Index('beta', 'up')),
            ('k', Index('rho', 'up')),
            ('l', Index('sigma', 'up')),
        ),
        completed,
        dimension=4,
    )

    print(f'=== QEDCalc v{__version__} topology/amplitude demo ===')
    print('Bare amplitude:')
    print(render_latex(bare.expression))
    print('\nContracted amplitude:')
    print(render_latex(contracted_amp.expression))
    print('\nMixed rank-2 tensor average:')
    print(render_latex(mixed_rank2))
    print('\nMixed rank-4 tensor average:')
    print(render_latex(mixed_rank4))

    s = MarkdownSession(out, 'Topology-to-amplitude and mixed multi-loop tensor demo')
    s.text('Version', f'QEDCalc v{__version__}')
    s.text('Design rule',
           'The topology-to-amplitude bridge uses an explicit ordered factor template. '
           'QEDCalc does not reconstruct lost graph ordering from a bare algebraic expression.')
    s.equation('Bare amplitude assembled from topology factors', bare.expression)
    s.text('Contracted topology members', '`' + ', '.join(contracted_amp.contracted_members) + '`')
    s.equation('Amplitude after explicit local vertex replacement', contracted_amp.expression)
    s.equation('Two-loop quadratic form', quadratic)
    s.equation('Mixed rank-2 tensor reduction', mixed_rank2)
    s.equation('Mixed rank-4 tensor reduction', mixed_rank4)
    s.text('Tensor convention',
           'The mixed tensor reducer is used only after square completion, when the loop dependence '
           'is through Q = L^T M L. It uses M^{-1} and the isotropic average in n*D dimensions.')
    s.save()
    print(f'\nMarkdown written to: {out}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
