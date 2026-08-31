import sympy as sp

from qedcalc.operations.ibp import IBPEquation, IntegralIndex
from three_loop.modp_pivot_trace import forward_eliminate_mod_p_with_trace
from three_loop.modp_replay_closure_profile import profile_replay_closure_sizes


def test_profile_replay_closure_sizes_counts_solved_and_unsolved_targets():
    a = IntegralIndex((3, 0))
    b = IntegralIndex((2, 0))
    c = IntegralIndex((1, 0))
    t = IntegralIndex((0, 0))
    equations = (
        IBPEquation({a: sp.Integer(1), b: sp.Integer(1)}, "eq0"),
        IBPEquation({b: sp.Integer(1), c: sp.Integer(1)}, "eq1"),
        IBPEquation({c: sp.Integer(1), t: sp.Integer(1)}, "eq2"),
    )
    trace = forward_eliminate_mod_p_with_trace(equations, 1000003)
    profile = profile_replay_closure_sizes(trace, (a, b, t))
    assert profile.requested_target_count == 3
    assert profile.solved_target_count == 2
    assert profile.unsolved_target_count == 1
    assert profile.max_replay_pivot_count >= profile.min_replay_pivot_count >= 1
