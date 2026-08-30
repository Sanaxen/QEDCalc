from qedcalc.operations.ibp import IntegralIndex
from three_loop.seed_pruning import (
    SeedPruningPolicy,
    descendant_sector_closure,
    prune_seed_indices,
    profile_seed_pruning,
)


def test_descendant_sector_closure_contains_all_subsectors():
    closure = descendant_sector_closure([(1, 0, 1)])
    assert closure == frozenset({(0, 0, 0), (1, 0, 0), (0, 0, 1), (1, 0, 1)})


def test_seed_pruning_enforces_dot_and_numerator_bounds():
    indices = [
        IntegralIndex((1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)),
        IntegralIndex((2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)),
        IntegralIndex((1, 1, 0, 0, 0, 0, 0, 0, 0, -4, 0, 0)),
        IntegralIndex((3, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)),
        IntegralIndex((1, 1, 0, 0, 0, 0, 0, 0, 0, -5, 0, 0)),
    ]
    policy = SeedPruningPolicy(max_dot_degree=1, max_numerator_degree=4)
    accepted = prune_seed_indices(indices, policy)
    assert len(accepted) == 3
    profile = profile_seed_pruning(indices, policy)
    assert profile.input_count == 5
    assert profile.accepted_count == 3
    assert profile.rejected_for_dot_count == 1
    assert profile.rejected_for_numerator_count == 1


def test_seed_pruning_respects_allowed_sector_closure():
    target_sector = (1, 1, 0, 0, 0, 0, 0, 0, 0)
    allowed = descendant_sector_closure([target_sector])
    indices = [
        IntegralIndex((1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)),
        IntegralIndex((1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)),
        IntegralIndex((0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)),
        IntegralIndex((0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0)),
    ]
    policy = SeedPruningPolicy(1, 4, allowed)
    accepted = prune_seed_indices(indices, policy)
    assert len(accepted) == 3
    assert IntegralIndex((0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0)) not in accepted
