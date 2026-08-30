from pathlib import Path
import tempfile
import sympy as sp

from qedcalc.operations.ibp import (
    IntegralIndex, ReductionRule,
    mixed_degree2_seeds,
    write_laporta_rule_checkpoint,
    read_laporta_rule_checkpoint,
)
from qedcalc.operations.ladder import ordinary_ladder_integral_symmetries


def test_mixed_degree2_seed_counts_for_ordinary_ladder_candidates():
    syms = ordinary_ladder_integral_symmetries()
    cases = {
        IntegralIndex((0,1,0,0,1,0,2)): 18,
        IntegralIndex((0,1,1,1,0,1,1)): 21,
        IntegralIndex((0,1,1,1,1,0,2)): 21,
    }
    # Without removing the phase-2 baseline, these are the symmetry-canonical
    # mixed parts of the full bounded degree-2 domain.
    for idx, expected in cases.items():
        assert len(mixed_degree2_seeds(idx, symmetries=syms)) == expected


def test_laporta_rule_checkpoint_roundtrip(tmp_path):
    a = IntegralIndex((2,1))
    b = IntegralIndex((1,1))
    c = IntegralIndex((1,0))
    D = sp.Symbol('D')
    rules = (ReductionRule(a, {b: (D-2)/(D-3), c: sp.Rational(3,7)}),)
    path = tmp_path / 'rules.json'
    write_laporta_rule_checkpoint(path, rules, metadata={'probe':'test'})
    restored, meta = read_laporta_rule_checkpoint(path, local_symbols={'D':D})
    assert restored == rules
    assert meta['probe'] == 'test'
