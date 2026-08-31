from qedcalc.operations.ibp import IBPEquation, IntegralIndex
from three_loop.modp_local_master_rank import conditional_block_rank_mod_p


def test_conditional_block_rank_for_x_plus_y_relation():
    x = IntegralIndex((1,))
    y = IntegralIndex((2,))
    equation = IBPEquation({x: 1, y: 1}, "x+y=0")

    rank_x, free_x = conditional_block_rank_mod_p((equation,), (x,), 1000003)
    assert rank_x == 1
    assert free_x == 0

    rank_xy, free_xy = conditional_block_rank_mod_p((equation,), (x, y), 1000003)
    assert rank_xy == 1
    assert free_xy == 1
