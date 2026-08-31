from qedcalc.operations.ibp import IntegralIndex
from three_loop.integral_family import q01_integral_family
from three_loop.terminal_boundary_classification import classify_terminal_boundary


def test_terminal_boundary_marks_known_manifest_before_structure():
    family = q01_integral_family()
    index = IntegralIndex((1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0))
    profile = classify_terminal_boundary(family, (index,), known_manifest_indices=(index,))
    assert profile.terminal_count == 1
    assert profile.known_manifest_count == 1
    assert profile.records[0].category == "known-29-manifest"


def test_terminal_boundary_classifies_generic_nonscalar():
    family = q01_integral_family()
    index = IntegralIndex((1, 1, 1, 1, 1, 1, 1, 1, 1, -1, 0, 0))
    profile = classify_terminal_boundary(family, (index,))
    assert profile.nonscalar_count == 1
    assert profile.records[0].full_numerator_degree == 1
