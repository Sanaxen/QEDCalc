from three_loop.master_basis_api import PropagatorSpec, FamilySpec, Seed
from three_loop.master_basis_sparse_discovery import build_sparse_target_plan


def _spec(p: int) -> FamilySpec:
    a = 12 - p
    return FamilySpec(
        family_id="T_full",
        representative="T",
        diagrams=("T",),
        topology_family="quenched",
        propagators=tuple(
            PropagatorSpec(f"k{i}", "0") for i in range(12)
        ),
        top_sector=(1 << p) - 1,
        unique_physical_count=p,
        auxiliary_names=tuple(f"A{i}" for i in range(a)),
        raw_to_unique=tuple(range(1, p + 1)),
        duplicate_groups=(),
        baseline_seed=Seed(p, 3, 0),
    )


def test_sparse_level0_covers_every_nonempty_sector_once():
    plan = build_sparse_target_plan(_spec(4), level=0)
    assert plan.sector_count == 15
    assert plan.target_count == 15
    assert plan.envelope == Seed(4, 0, 0)


def test_sparse_level1_is_small_and_has_expected_envelope():
    plan = build_sparse_target_plan(_spec(8), level=1)
    # 255 sector corners plus one-dot and one-ISP probes.  The exact total is
    # deterministic and remains tiny compared with recursive r8s3d0 selection.
    assert plan.sector_count == 255
    assert plan.target_count == 255 + (8 * 2**7) + (4 * 255)
    assert plan.envelope == Seed(9, 1, 1)


def test_sparse_level2_strictly_extends_level1():
    spec = _spec(8)
    l1 = build_sparse_target_plan(spec, level=1)
    l2 = build_sparse_target_plan(spec, level=2)
    assert set(l1.targets) < set(l2.targets)
    assert l2.envelope.r >= l1.envelope.r
    assert l2.envelope.s >= l1.envelope.s
    assert l2.envelope.d >= l1.envelope.d
