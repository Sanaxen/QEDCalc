from qedcalc.operations.ibp import IntegralIndex
from three_loop.remaining_target_classification import (
    classify_remaining_targets,
    corrected_total_complexity,
    full_numerator_degree,
    physical_negative_degree,
)


def test_physical_negative_power_counts_as_numerator():
    index = IntegralIndex((1, 1, 1, 0, 1, 1, 0, -1, 1, 0, 0, 0))
    assert physical_negative_degree(index) == 1
    assert full_numerator_degree(index) == 1
    assert corrected_total_complexity(index) == 1


def test_scalar_subtopology_is_zero_corrected_complexity():
    index = IntegralIndex((1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 0, 0))
    record = classify_remaining_targets((index,))[0]
    assert record.corrected_complexity == 0
    assert record.is_scalar_subtopology
