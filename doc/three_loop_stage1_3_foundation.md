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
b(D,z) &= \frac{Dz-2z+4}{z(D-2)(z-4)^2},
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

The validation checks stages 1–3 and also keeps the existing stage-4-preview checks. It remains separate from `run_v090_validation.bat`; before merging higher-loop work, both should remain green.

## Repository integration note

The previously missing `qedcalc/` source tree has now been restored. Stage 3 directly imports and reuses the restored QEDCalc projector machinery. Stage 2 remains structurally isolated for now; the next integration step is to convert its ordered amplitude representation into QEDCalc expression objects and then connect

`topology -> ordered amplitude -> QEDCalc expression -> magnetic projector -> F2`

for one or more reference three-loop diagrams before generalizing to all 72.
