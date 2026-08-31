from qedcalc.operations.ibp import IntegralIndex
from three_loop.integral_family import q01_integral_family
from three_loop.scalar_subtopology_factorization import (
    factorization_label,
    free_loops_for_index,
    loop_components_for_index,
)


def test_factorization_labels_cover_q01_loop_partitions():
    assert factorization_label((3,)) == "connected-3loop"
    assert factorization_label((2, 1)) == "factorized-2+1"
    assert factorization_label((1, 1, 1)) == "factorized-1+1+1"


def test_full_q01_seed_connects_all_three_loop_momenta():
    family = q01_integral_family()
    seed = IntegralIndex((1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0))
    components = loop_components_for_index(family, seed)
    assert components == (("k", "l", "r"),)
    assert free_loops_for_index(family, seed) == ()
