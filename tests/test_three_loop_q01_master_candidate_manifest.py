from qedcalc.operations.ibp import IntegralIndex
from three_loop.q01_master_candidate_manifest import build_q01_master_candidate_manifest


def test_master_candidate_manifest_partitions_categories():
    remaining = (
        IntegralIndex((1,1,1,1,0,1,0,0,0,0,0,0)),
        IntegralIndex((1,1,1,1,1,1,0,0,0,0,0,0)),
        IntegralIndex((1,1,1,0,1,1,0,-1,1,0,0,0)),
    )
    factorization = {
        remaining[0].powers: "factorized-2+1",
        remaining[1].powers: "connected-3loop",
    }
    manifest = build_q01_master_candidate_manifest(remaining, factorization)
    assert manifest.remaining_count == 3
    assert manifest.lower_loop_factorized_count == 1
    assert manifest.connected_scalar_count == 1
    assert manifest.nonscalar_count == 1
    assert manifest.genuine_three_loop_candidate_count == 2


def test_master_candidate_manifest_labels_nonscalar_without_factorization():
    target = IntegralIndex((1,0,1,-1,1,1,0,1,1,0,0,0))
    manifest = build_q01_master_candidate_manifest((target,), {})
    assert manifest.entries[0].category == "nonscalar-master-candidate"
