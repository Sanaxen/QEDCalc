import csv
from pathlib import Path
import sympy as sp

from qedcalc.operations.ibp import (
    IntegralIndex,
    degree3_shell_seeds,
    diagnose_full_degree3_irreducibility,
    read_laporta_rule_checkpoint,
)
from qedcalc.operations.ladder import (
    ordinary_ladder_ibp_family,
    ordinary_ladder_integral_symmetries,
)

ROOT = Path(__file__).parents[1]


def _load_indices(path):
    with path.open(newline='', encoding='utf-8') as f:
        r = csv.DictReader(f)
        return [IntegralIndex(tuple(int(row[k]) for k in ('nK','nL','nH','n1','n2','n3','n4'))) for row in r]


def test_degree3_shell_counts_for_three_ladder_candidates():
    syms = ordinary_ladder_integral_symmetries()
    existing = _load_indices(ROOT/'data'/'ladder_phase2_116_seeds.csv')
    cands = _load_indices(ROOT/'data'/'ladder_phase6_full_degree2_checkpoint.csv')
    assert [len(degree3_shell_seeds(c, syms, existing)) for c in cands] == [72, 84, 84]


def test_full_degree3_diagnostic_small_tadpole_is_bounded():
    # Exercise the API on a tiny one-denominator family rather than the full
    # ladder checkpoint, keeping the unit test fast.
    from qedcalc.operations.ibp import IntegralFamily, sp_atom, generate_ibp_equation, specialize_ibp_system, laporta_forward_eliminate
    D, m2 = sp.symbols('D m2')
    k2 = sp_atom('k','k')
    fam = IntegralFamily(
        name='tadpole-v040',
        denominator_names=('T',),
        denominator_exprs=(k2-m2,),
        loop_momenta=('k',), external_momenta=(),
        scalar_product_rules={k2: sp.Symbol('T')+m2},
        dimension_symbol=D,
    )
    probe={D:sp.Rational(7,2),m2:1}
    eq=generate_ibp_equation(fam,(1,),'k','k')
    base=laporta_forward_eliminate(specialize_ibp_system((eq,),probe),protected=(IntegralIndex((1,)),))
    diag=diagnose_full_degree3_irreducibility(
        fam, IntegralIndex((1,)), base, probe,
        existing_seeds=(IntegralIndex((1,)),),
        protected=(IntegralIndex((1,)),), vectors=('k',),
    )
    assert diag.residue == IntegralIndex((1,))
    assert len(diag.tested_seeds) == 1
    assert isinstance(diag.full_degree3_irreducible, bool)
