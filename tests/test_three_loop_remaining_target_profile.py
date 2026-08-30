from qedcalc.operations.ibp import IntegralIndex
from three_loop.integral_family import q01_integral_family
from three_loop.remaining_target_profile import RemainingTargetRecord
from three_loop.laporta_plan import dot_degree, numerator_degree, total_complexity


def test_remaining_target_record_complexity_helpers_agree():
    index = IntegralIndex((2, 0, 1, 0, 1, 1, 1, 1, 1, -1, 0, 0))
    record = RemainingTargetRecord(
        index=index.powers,
        sector=(1, 0, 1, 0, 1, 1, 1, 1, 1),
        dot_degree=dot_degree(index),
        numerator_degree=numerator_degree(index),
        total_complexity=total_complexity(index),
        active_physical_lines=7,
    )
    assert record.dot_degree == 1
    assert record.numerator_degree == 1
    assert record.total_complexity == 2


def test_q01_family_accepts_profile_index_shape():
    family = q01_integral_family()
    index = IntegralIndex((1,) * 9 + (0, 0, 0))
    assert family.validate_index(index) == index
