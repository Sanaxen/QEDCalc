from pathlib import Path
from functools import lru_cache
import sympy as sp

from qedcalc.parser.qed_latex import parse_loop_integral_latex
from qedcalc.operations.ladder import (
    analyze_raw_ordinary_ladder,
    ladder_general_q_projector_result,
    load_ladder_coefficient_table,
    compare_ladder_integral_tables,
    LadderIntegralIndex,
)

ROOT = Path(__file__).parents[1]


@lru_cache(maxsize=1)
def _raw():
    source = (ROOT / "input" / "ordinary_ladder_2loop_bare.tex").read_text(encoding="utf-8")
    return analyze_raw_ordinary_ladder(parse_loop_integral_latex(source))


@lru_cache(maxsize=1)
def _archived():
    return ladder_general_q_projector_result(_raw(), "archived")


@lru_cache(maxsize=1)
def _corrected():
    return ladder_general_q_projector_result(_raw(), "spin_sum")


def test_archived_general_q_raw_trace_regenerates_75_terms():
    result = _archived()
    assert len(result.integral_table) == 75


def test_archived_general_q_raw_trace_matches_reference_csv_exactly():
    result = _archived()
    reference = load_ladder_coefficient_table(ROOT / "data" / "ladder_Ddim_75_coefficients.csv")
    diff = compare_ladder_integral_tables(result.integral_table, reference)
    assert diff == {"missing": [], "extra": [], "mismatched": []}


def test_archived_general_q_representative_coefficients():
    result = _archived()
    D, z = sp.symbols("D z")
    t = result.integral_table
    assert sp.simplify(t[LadderIntegralIndex(1,1,0,1,1,1,1)] + 16*(z-2)) == 0
    assert sp.simplify(t[LadderIntegralIndex(1,0,-1,1,1,1,1)] - 8*(D-4)/(z-4)) == 0
    assert sp.simplify(t[LadderIntegralIndex(0,0,-1,1,1,1,1)] - 8*(D-2)*(D-1)/(z-4)**2) == 0


def test_corrected_spin_sum_route_is_kept_separate_from_archived_75_table():
    result = _corrected()
    reference = load_ladder_coefficient_table(ROOT / "data" / "ladder_Ddim_75_coefficients.csv")
    corrected_checkpoint = load_ladder_coefficient_table(ROOT / "data" / "ladder_corrected_spin_sum_72_coefficients.csv")
    diff = compare_ladder_integral_tables(result.integral_table, reference)
    checkpoint_diff = compare_ladder_integral_tables(result.integral_table, corrected_checkpoint)
    assert len(result.integral_table) == 72
    assert diff["missing"] or diff["extra"] or diff["mismatched"]
    assert checkpoint_diff == {"missing": [], "extra": [], "mismatched": []}
