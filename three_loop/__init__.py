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
from .onshell import (
    OnShellScalarReduction,
    ExternalBasisReduction,
    finite_q_onshell_substitutions,
    finite_q_pq_basis_substitutions,
    apply_finite_q_onshell,
    rewrite_to_pq_external_basis,
)
from .integral_family import (
    Q01_PHYSICAL_DENOMINATOR_COUNT,
    Q01_FAMILY_SIZE,
    Q01_SEED,
    q01_denominator_expressions,
    q01_scalar_product_rules,
    q01_integral_family,
    q01_family_checkpoint,
)
from .integral_mapping import (
    IntegralLinearCombination,
    scalar_numerator_to_integrals,
    q01_scalar_numerator_to_integrals,
)
from .laporta_plan import (
    SectorDemandProfile,
    physical_sector,
    dot_degree,
    numerator_degree,
    total_complexity,
    build_sector_demand_profiles,
)
from .ibp_frontier import (
    IBPDerivativeTemplate,
    IBPFrontierProfile,
    build_ibp_derivative_templates,
    one_step_ibp_frontier,
    profile_ibp_frontier,
)
from .seed_pruning import (
    SeedPruningPolicy,
    SeedPruningProfile,
    descendant_sector_closure,
    prune_seed_indices,
    profile_seed_pruning,
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
    "OnShellScalarReduction", "ExternalBasisReduction",
    "finite_q_onshell_substitutions", "finite_q_pq_basis_substitutions",
    "apply_finite_q_onshell", "rewrite_to_pq_external_basis",
    "Q01_PHYSICAL_DENOMINATOR_COUNT", "Q01_FAMILY_SIZE", "Q01_SEED",
    "q01_denominator_expressions", "q01_scalar_product_rules",
    "q01_integral_family", "q01_family_checkpoint",
    "IntegralLinearCombination", "scalar_numerator_to_integrals",
    "q01_scalar_numerator_to_integrals",
    "SectorDemandProfile", "physical_sector", "dot_degree",
    "numerator_degree", "total_complexity", "build_sector_demand_profiles",
    "IBPDerivativeTemplate", "IBPFrontierProfile",
    "build_ibp_derivative_templates", "one_step_ibp_frontier",
    "profile_ibp_frontier",
    "SeedPruningPolicy", "SeedPruningProfile", "descendant_sector_closure",
    "prune_seed_indices", "profile_seed_pruning",
    "DivergentSubgraph", "discover_candidate_subgraphs",
]
