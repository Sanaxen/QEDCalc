from pathlib import Path

from three_loop.master_basis_api import (
    PropagatorSpec,
    FamilySpec,
    Seed,
    find_master_list,
    render_jobs_yaml,
)


def _spec() -> FamilySpec:
    return FamilySpec(
        family_id="QXX_full",
        representative="QXX",
        diagrams=("QXX",),
        topology_family="quenched",
        propagators=tuple(PropagatorSpec(f"k{i}", "0") for i in range(12)),
        top_sector=255,
        unique_physical_count=8,
        auxiliary_names=("a", "b", "c", "d"),
        raw_to_unique=(),
        duplicate_groups=(),
        baseline_seed=Seed(8, 3, 0),
    )


def test_masters_solver_stops_after_initiate():
    text = render_jobs_yaml(_spec(), Seed(8, 3, 0), solver="masters")
    assert "run_initiate: true" in text
    assert "run_triangular: false" in text
    assert "run_back_substitution: false" in text
    assert "run_firefly: false" in text


def test_firefly_solver_behavior_is_unchanged():
    text = render_jobs_yaml(_spec(), Seed(8, 3, 0), solver="firefly")
    assert "run_initiate: true" in text
    assert "run_triangular: false" in text
    assert "run_back_substitution: false" in text
    assert "run_firefly: true" in text


def test_find_master_list_accepts_initiate_only_master_file(tmp_path: Path):
    master = tmp_path / "results" / "QXX_full" / "master"
    master.parent.mkdir(parents=True)
    master.write_text(
        "1: QXX_full[1,1,1,1,1,1,1,1,0,0,0,0]\n"
        "2: QXX_full[1,1,1,1,1,1,1,0,1,0,0,0]\n",
        encoding="utf-8",
    )
    path, masters = find_master_list(tmp_path, "QXX_full")
    assert path == master
    assert masters == [
        "QXX_full[1,1,1,1,1,1,1,1,0,0,0,0]",
        "QXX_full[1,1,1,1,1,1,1,0,1,0,0,0]",
    ]
