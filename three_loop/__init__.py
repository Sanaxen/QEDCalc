"""Three-loop stages 1-3 foundation and QEDCalc integration bridge."""
from .registry import PhotonEdge, ThreeLoopRegistry, ThreeLoopTopology
from .amplitude import Factor, OrderedAmplitude, build_ordered_amplitude
from .projector import (
    MagneticProjector,
    three_loop_magnetic_projector,
    project_f2_from_reduced_current,
    schwinger_gordon_checkpoint,
)
from .qedexpr_bridge import (
    ProjectorReadyAmplitude,
    ordered_amplitude_to_qedexpr,
    build_projector_ready_amplitude,
    q01_bridge_checkpoint,
)
from .projected_trace import (
    ProjectedTraceStructure,
    ScalarProjectedNumerator,
    magnetic_projector_kernel,
    build_projected_trace,
    build_topology_projected_trace,
    reduce_projected_trace_to_scalar_products,
    projected_trace_checkpoint,
)
from .divergence import DivergentSubgraph, discover_candidate_subgraphs

__all__ = [
    "PhotonEdge", "ThreeLoopRegistry", "ThreeLoopTopology",
    "Factor", "OrderedAmplitude", "build_ordered_amplitude",
    "MagneticProjector", "three_loop_magnetic_projector",
    "project_f2_from_reduced_current", "schwinger_gordon_checkpoint",
    "ProjectorReadyAmplitude", "ordered_amplitude_to_qedexpr",
    "build_projector_ready_amplitude", "q01_bridge_checkpoint",
    "ProjectedTraceStructure", "ScalarProjectedNumerator",
    "magnetic_projector_kernel", "build_projected_trace",
    "build_topology_projected_trace", "reduce_projected_trace_to_scalar_products",
    "projected_trace_checkpoint",
    "DivergentSubgraph", "discover_candidate_subgraphs",
]
