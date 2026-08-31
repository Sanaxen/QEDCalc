from qedcalc.operations.ibp import IntegralIndex
from three_loop.nonscalar_terminal_profile import classify_nonscalar_terminals, profile_histograms


def test_nonscalar_terminal_profile_separates_physical_and_auxiliary_negative_slots():
    physical = IntegralIndex((1, 1, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0))
    auxiliary = IntegralIndex((1, 1, 1, 0, 0, 0, 0, 0, 0, -1, 0, 0))
    mixed = IntegralIndex((1, -1, 1, 0, 0, 0, 0, 0, 0, 0, -2, 0))
    profile = classify_nonscalar_terminals((physical, auxiliary, mixed))
    assert profile.terminal_count == 3
    assert profile.physical_only_count == 1
    assert profile.auxiliary_only_count == 1
    assert profile.mixed_count == 1
    by_index = {record.index: record for record in profile.records}
    assert by_index[physical.powers].physical_negative_slots == (3,)
    assert by_index[physical.powers].auxiliary_negative_slots == ()
    assert by_index[auxiliary.powers].physical_negative_slots == ()
    assert by_index[auxiliary.powers].auxiliary_negative_slots == (10,)
    assert by_index[mixed.powers].negative_slots == (2, 11)
    assert by_index[mixed.powers].physical_negative_degree == 1
    assert by_index[mixed.powers].auxiliary_numerator_degree == 2


def test_nonscalar_terminal_profile_histograms_count_slots_and_degrees():
    a = IntegralIndex((1, -1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0))
    b = IntegralIndex((1, -1, 1, 0, 0, 0, 0, 0, 0, -1, 0, 0))
    profile = classify_nonscalar_terminals((a, b))
    hist = profile_histograms(profile)
    assert hist["negative_slot_histogram"][2] == 2
    assert hist["negative_slot_histogram"][10] == 1
    assert hist["physical_aux_degree_histogram"]["(1, 0)"] == 1
    assert hist["physical_aux_degree_histogram"]["(1, 1)"] == 1
