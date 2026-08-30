from qedcalc.operations.ibp import IntegralIndex
from three_loop.ibp_frontier import build_ibp_derivative_templates
from three_loop.integral_family import q01_integral_family
from three_loop.local_block_elimination import local_same_seed_equations, blocker_locally_solved


def test_local_same_seed_equations_count():
    family = q01_integral_family()
    templates = build_ibp_derivative_templates(family)
    seed = IntegralIndex((1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0))
    equations = local_same_seed_equations(family, seed, templates=templates)
    assert len(equations) == 15


def test_blocker_locally_solved_api():
    family = q01_integral_family()
    templates = build_ibp_derivative_templates(family)
    blocker = IntegralIndex((2, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0))
    solved, rule_count = blocker_locally_solved(family, blocker, templates=templates)
    assert isinstance(solved, bool)
    assert isinstance(rule_count, int)
    assert rule_count >= 0
