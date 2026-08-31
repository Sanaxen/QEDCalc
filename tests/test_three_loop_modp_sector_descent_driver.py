from three_loop.modp_sector_descent_driver import (
    largest_lower_sector_from_saved,
    targets_for_sector_from_saved,
)


def test_largest_lower_sector_from_saved_uses_terminal_count():
    data = {
        "lower_sector_rows": [
            {"sector": [1, 0, 1, 0, 1, 0, 0, 1, 0], "terminal_count": 52},
            {"sector": [1, 0, 1, 0, 1, 1, 0, 0, 0], "terminal_count": 126},
        ]
    }
    assert largest_lower_sector_from_saved(data) == (1, 0, 1, 0, 1, 1, 0, 0, 0)


def test_targets_for_sector_from_saved_filters_and_deduplicates():
    wanted = (1, 0, 1, 0, 1, 1, 0, 0, 0)
    a = [1, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0]
    b = [1, 0, 1, 0, 1, 1, 0, 0, 0, -1, 0, 0]
    other = [1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0]
    data = {"terminal_indices": [a, b, a, other]}
    targets = targets_for_sector_from_saved(data, wanted)
    assert [target.powers for target in targets] == [tuple(a), tuple(b)]
