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

This first implementation deliberately returns a structural amplitude rather than immediately constructing the existing symbolic expression type. That keeps the new layer inspectable and prevents accidental graph-specific simplification.

For Q01 the generated open-line sequence is checked against the reference topology `(2;(1,4),(3,6),(5,7))`.

## Stage 3 — divergent-subgraph candidates

`three_loop/divergence.py` performs a first topology-level UV audit.

It:

- records explicitly declared VP and LBL closed kernels,
- scans contiguous open-electron-line intervals,
- counts crossing photon lines as external photon legs,
- applies QED superficial power counting,
- classifies electron subgraphs as self-energy or vertex candidates,
- excludes the whole graph from the subdivergence list.

This is a **candidate discovery/planning layer**. It does not yet apply on-shell finite counterterms, Ward-identity cancellations, forest generation, or overlapping-subgraph subtraction.

## Validation

Run:

```text
run_three_loop_stage1_3_validation.bat
```

The validation is intentionally separate from `run_v090_validation.bat`. Before merging higher-loop work, both should remain green.

## Current repository note

At the branch point, `README_JP.md`, `pyproject.toml`, and the tests describe a `qedcalc` Python package, but the `main` Git tree does not contain that package directory. For that reason stages 1–3 are added as an isolated `three_loop` package. Once the missing existing source tree is restored or its intended location is confirmed, this layer can be connected to QEDCalc's existing expression/projector/renormalization APIs without rewriting the topology data.
