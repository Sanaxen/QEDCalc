from pathlib import Path

from three_loop import (
    ThreeLoopRegistry,
    build_ordered_amplitude,
    discover_candidate_subgraphs,
)


DATA = Path(__file__).resolve().parents[1] / "data" / "three_loop_topologies.json"


def registry():
    return ThreeLoopRegistry.from_json(DATA)


def test_stage1_registers_all_72_diagrams():
    reg = registry()
    assert len(reg) == 72
    assert len(reg.by_family("quenched")) == 50
    assert len(reg.by_family("vp1_insert")) == 12
    assert len(reg.by_family("vp2_insert")) == 3
    assert len(reg.by_family("vp1_double")) == 1
    assert len(reg.by_family("external_lbl")) == 6


def test_stage1_q01_topology_matches_reference():
    q01 = registry().get("Q01")
    assert q01.external_vertex == 2
    assert [(e.label, e.a, e.b) for e in q01.photon_edges] == [
        ("k", 1, 4),
        ("l", 3, 6),
        ("r", 5, 7),
    ]


def test_stage2_q01_order_and_momentum_routing():
    amp = build_ordered_amplitude(registry().get("Q01"))
    assert amp.sign == 1
    assert [f.value for f in amp.open_line] == [
        "gamma_k_L", "p' - k",
        "gamma_mu", "p - k",
        "gamma_l_L", "p - k - l",
        "gamma_k_R", "p - l",
        "gamma_r_L", "p - l - r",
        "gamma_l_R", "p - r",
        "gamma_r_R",
    ]


def test_stage2_closed_loop_signs():
    reg = registry()
    assert build_ordered_amplitude(reg.get("VP01")).sign == -1
    assert build_ordered_amplitude(reg.get("VP22")).sign == 1
    assert build_ordered_amplitude(reg.get("LBL01")).sign == -1


def test_stage3_declared_vp_is_discovered():
    candidates = discover_candidate_subgraphs(registry().get("VP01"))
    assert any(c.kind == "vacuum_polarization" for c in candidates)


def test_stage3_q01_finds_nested_vertex_candidates():
    candidates = discover_candidate_subgraphs(registry().get("Q01"))
    signatures = {(c.kind, c.vertices, c.photon_labels) for c in candidates}
    assert ("vertex", (5, 6, 7), ("r",)) in signatures
    assert ("vertex", (3, 4, 5, 6, 7), ("l", "r")) in signatures
