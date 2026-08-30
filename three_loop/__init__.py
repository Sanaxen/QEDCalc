"""Three-loop stages 1-3 foundation."""
from .registry import PhotonEdge, ThreeLoopRegistry, ThreeLoopTopology
from .amplitude import Factor, OrderedAmplitude, build_ordered_amplitude
from .projector import (
    MagneticProjector,
    three_loop_magnetic_projector,
    project_f2_from_reduced_current,
    schwinger_gordon_checkpoint,
)
from .divergence import DivergentSubgraph, discover_candidate_subgraphs

__all__ = [
    "PhotonEdge", "ThreeLoopRegistry", "ThreeLoopTopology",
    "Factor", "OrderedAmplitude", "build_ordered_amplitude",
    "MagneticProjector", "three_loop_magnetic_projector",
    "project_f2_from_reduced_current", "schwinger_gordon_checkpoint",
    "DivergentSubgraph", "discover_candidate_subgraphs",
]
