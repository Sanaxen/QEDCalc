from qedcalc.operations.ibp import IntegralIndex
from three_loop import q01_integral_family
from three_loop.ibp_frontier import (
    build_ibp_derivative_templates,
    one_step_ibp_frontier,
    profile_ibp_frontier,
)


def test_q01_ibp_templates_cover_all_loop_vector_denominator_choices():
    family = q01_integral_family()
    templates = build_ibp_derivative_templates(family)
    assert len(templates) == 3 * 5 * 12


def test_one_step_ibp_frontier_includes_seed_and_generates_neighbors():
    family = q01_integral_family()
    seed = IntegralIndex((1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0))
    frontier = one_step_ibp_frontier(family, (seed,))
    assert seed in frontier
    assert len(frontier) > 1


def test_one_step_ibp_frontier_can_generate_dot_integrals():
    family = q01_integral_family()
    seed = IntegralIndex((1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0))
    frontier = one_step_ibp_frontier(family, (seed,))
    profile = profile_ibp_frontier((seed,), frontier)
    assert profile.max_dot_degree >= 1
    assert profile.generated_index_count >= profile.seed_count
