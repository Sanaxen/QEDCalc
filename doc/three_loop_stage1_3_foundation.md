# Three-loop stages 1–3 foundation

This branch starts the staged three-loop extension without changing the protected v0.90 two-loop baseline.

## Stage 1 — topology registry

`data/three_loop_topologies.json` registers all 72 sixth-order vertex diagrams in five families:

- 50 quenched three-photon-exchange diagrams,
- 12 one-loop vacuum-polarization insertions,
- 3 two-loop vacuum-polarization insertions,
- 1 double one-loop vacuum-polarization insertion,
- 6 external light-by-light diagrams.

The 50 quenched and 12 VP-insertion open-line topologies are transcribed from `3loop_vertex_72_complete_equations.md`. The remaining families are registered by the structural classification used in the same source document.

## Stage 2 — ordered structural amplitude

`three_loop/amplitude.py` converts topology data into an ordered factor stream. It preserves:

- gamma-matrix order on the open electron line,
- segment-by-segment momentum routing,
- photon propagator labels,
- closed-fermion-loop sign,
- declared VP/LBL loop kernels.

The first implementation returns a structural amplitude rather than immediately constructing the existing symbolic expression type. This keeps the topology-to-amplitude layer inspectable and prevents accidental graph-specific simplification.

For Q01 the generated open-line sequence is checked against the reference topology `(2;(1,4),(3,6),(5,7))`.

## Stage 3 — unified magnetic projector

`three_loop/projector.py` connects the three-loop layer to QEDCalc's existing magnetic form-factor machinery rather than introducing a second convention.

The finite-q D-dimensional Pauli projector reuses `qedcalc.operations.ladder.ladder_projector_coefficients`:

$$
\begin{aligned}
a(D,z) &= \frac{2}{z(D-2)(z-4)}, \\
b(D,z) &= \frac{Dz-2z+4}{z(D-2)(z-4)^2}.
\end{aligned}
$$

with $z=q^2/m^2$.

The three-loop-facing API also reuses `qedcalc.operations.projector.project_f2_gordon_basis` for currents already reduced to the Gordon basis.

### Why q -> 0 is not direct substitution

Both finite-q coefficients contain a $1/z$ pole. Therefore stage 3 does not substitute `z=0` into `a` and `b` separately. `MagneticProjector.q_zero_laurent()` exposes their Laurent expansions and `q_zero_pole_coefficients()` exposes the residues so that cancellation can be checked after the projected amplitude has been assembled.

The leading residues are

$$
\begin{aligned}
\operatorname*{Res}_{z=0} a &= -\frac{1}{2(D-2)}, \\
\operatorname*{Res}_{z=0} b &= \frac{1}{4(D-2)}.
\end{aligned}
$$

Only after the amplitude/projector combination is regular may the physical $F_2(0)$ limit be taken.

### One-loop normalization checkpoint

`schwinger_gordon_checkpoint()` checks the normalization convention of the Gordon extractor. If the reduced coefficient of $(p'+p)_\mu$ is

$$
B=-\frac{\alpha}{4\pi m},
$$

then QEDCalc's existing relation

$$
F_2=-2mB
$$

gives

$$
F_2(0)=\frac{\alpha}{2\pi}.
$$

This is only a normalization regression; it does not replace the one-loop integral calculation.

## Q01 integration bridge into QEDCalc

`three_loop/qedexpr_bridge.py` connects the first three-loop reference graph to the restored QEDCalc expression backend:

`topology -> ordered amplitude -> QEDCalc QEDExpr -> magnetic projector metadata`

The bridge is deliberately exact only for the quenched Q01–Q50 family at this point. VP and LBL graphs still need explicit closed-loop builders and are rejected rather than guessed.

For Q01 the bridge fixes the following structural regression targets:

- loop momenta: `k`, `l`, `r`,
- seven gamma matrices on the open electron line,
- six electron propagators,
- three photon propagators,
- distinct Lorentz indices at the two ends of every photon line.

Thus the first photon is represented structurally by gamma endpoints `k_L`, `k_R` connected by the metric pair `(k_L,k_R)`, with analogous pairs for `l` and `r`. This prevents a later Lorentz contraction from confusing the two photon endpoints.

The overall three-loop normalization is still represented by the explicit placeholder `C_3`. Coupling powers, loop-normalization factors, gauge-dependent longitudinal pieces and renormalization ownership are not silently inferred by this bridge.

## Q01 finite-q projected trace

`three_loop/projected_trace.py` now continues the chain to

`topology -> QEDExpr -> scalarized numerator/denominator -> finite-q magnetic projector trace`.

The electron and photon propagators are scalarized before the trace is built, so the scalar denominator is kept outside the Clifford word. The trace structure is

$$
\operatorname{Tr}\left[
(\rlap{/}p'+m)\,
K^{\mu}(D,z)\,
(\rlap{/}p+m)\,
N_{\mu}^{(3)}
\right],
$$

where the projector kernel is

$$
K^{\mu}(D,z)
=
a(D,z)\gamma^{\mu}
+
\frac{b(D,z)}{m}(p'+p)^{\mu}.
$$

The overall $1/m^2$ projector normalization is stored explicitly outside the trace. No $z=0$ substitution is performed at this point.

This is intentionally an unexpanded D-dimensional trace. QEDCalc already contains arbitrary-length D-dimensional Clifford-trace and fully contracted Lorentz-scalar machinery; the next computation step is to apply those engines to this Q01 trace, reduce the result to scalar products, and then organize the finite-$q$ expression for the $q\to0$ cancellation analysis.

## Stage 4 preview — divergent-subgraph candidates

`three_loop/divergence.py` was implemented early before the stage-number correction. It is retained as forward regression coverage for the next renormalization stage.

It currently:

- records explicitly declared VP and LBL closed kernels,
- scans contiguous open-electron-line intervals,
- counts crossing photon lines as external photon legs,
- applies QED superficial power counting,
- classifies electron subgraphs as self-energy or vertex candidates,
- excludes the whole graph from the subdivergence list.

This remains a candidate discovery/planning layer. It does not yet apply on-shell finite counterterms, Ward-identity cancellations, forest generation, or overlapping-subgraph subtraction.

## Validation

Run:

```text
run_three_loop_stage1_3_validation.bat
```

The validation checks stages 1–3, the Q01 QEDExpr bridge, the Q01 finite-q projected-trace structure, and the existing stage-4-preview checks. It remains separate from `run_v090_validation.bat`; before merging higher-loop work, both should remain green.

## Repository integration note

The previously missing `qedcalc/` source tree has now been restored. Stage 3 directly imports and reuses the restored QEDCalc projector machinery, and the Q01 bridge/projected-trace layers import the restored `qedcalc.core.expression` and propagator machinery directly.
