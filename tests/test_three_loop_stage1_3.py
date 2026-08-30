from pathlib import Path

import sympy as sp

from three_loop import (
    ThreeLoopRegistry,
    build_ordered_amplitude,
    build_projector_ready_amplitude,
    discover_candidate_subgraphs,
    q01_bridge_checkpoint,
    three_loop_magnetic_projector,
    schwinger_gordon_checkpoint,
)
from qedcalc.core.expression import (
    FermionPropagator,
    Gamma,
    LoopIntegralExpression,
    PhotonPropagator,
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


def test_stage3_projector_reuses_qedcalc_ddim_coefficients():
    D, z = sp.symbols("D z")
    projector = three_loop_magnetic_projector(D=D, z=z)
    assert sp.simplify(projector.a - 2/(z*(D-2)*(z-4))) == 0
    assert sp.simplify(
        projector.b - (D*z - 2*z + 4)/(z*(D-2)*(z-4)**2)
    ) == 0


def test_stage3_qzero_is_laurent_not_direct_substitution():
    D, z = sp.symbols("D z")
    projector = three_loop_magnetic_projector(D=D, z=z)
    residues = projector.q_zero_pole_coefficients()
    assert sp.simplify(residues["a_residue"] + 1/(2*(D-2))) == 0
    assert sp.simplify(residues["b_residue"] - 1/(4*(D-2))) == 0
    expansion = projector.q_zero_laurent(order=2)
    assert expansion["a"].has(1/z)
    assert expansion["b"].has(1/z)


def test_stage3_schwinger_normalization_checkpoint():
    alpha = sp.Symbol("alpha")
    assert sp.simplify(schwinger_gordon_checkpoint(alpha=alpha) - alpha/(2*sp.pi)) == 0


def test_q01_qedexpr_bridge_has_expected_graph_content():
    q01 = registry().get("Q01")
    ready = build_projector_ready_amplitude(q01)
    assert isinstance(ready.loop_integral, LoopIntegralExpression)
    assert tuple(v.name for v in ready.loop_integral.loops) == ("k", "l", "r")
    nodes = tuple(ready.loop_integral.integrand.walk())
    assert sum(isinstance(n, Gamma) for n in nodes) == 7
    assert sum(isinstance(n, FermionPropagator) for n in nodes) == 6
    assert sum(isinstance(n, PhotonPropagator) for n in nodes) == 3


def test_q01_bridge_checkpoint_is_projector_ready():
    checkpoint = q01_bridge_checkpoint(registry().get("Q01"))
    assert checkpoint == {
        "diagram_id": "Q01",
        "loop_names": ("k", "l", "r"),
        "gamma_count": 7,
        "fermion_propagator_count": 6,
        "photon_propagator_count": 3,
        "projector_has_finite_q": True,
    }


# The following checks belong to the next renormalization/divergent-subgraph stage.
# They remain here as forward regression coverage because this code was implemented
# before the stage-number correction.
def test_stage4_preview_declared_vp_is_discovered():
    candidates = discover_candidate_subgraphs(registry().get("VP01"))
    assert any(c.kind == "vacuum_polarization" for c in candidates)


def test_stage4_preview_q01_finds_nested_vertex_candidates():
    candidates = discover_candidate_subgraphs(registry().get("Q01"))
    signatures = {(c.kind, c.vertices, c.photon_labels) for c in candidates}
    assert ("vertex", (5, 6, 7), ("r",)) in signatures
    assert ("vertex", (3, 4, 5, 6, 7), ("l", "r")) in signatures
