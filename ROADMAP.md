# QEDCalc ROADMAP

## Current baseline: v0.90.0

QEDCalc v0.90.0 freezes the completed two-loop electron anomalous-magnetic-moment calculation as a protected regression baseline.

The current two-loop baseline includes:

- crossed ladder: 1 diagram,
- ordinary ladder: 1 diagram,
- corner: 2 diagrams,
- self-energy insertion: 2 diagrams,
- vacuum polarization: 1 diagram,
- exact corner/self-energy IR-log cancellation,
- exact seven-diagram basis sum,
- a standard-library regression that can run even when SymPy is unavailable.

Run

```text
run_v090_validation.bat
```

before and after major higher-loop changes.

---

## Completed milestone: two-loop semi-automatic processing

The seven two-loop diagrams now have validated graph-specific routes and release checkpoints.

| Diagram class | Status | Main checkpoint |
|---|---|---|
| crossed ladder | complete | Phase 78 |
| ordinary ladder | complete | Phase 81 |
| corner pair | complete | Phase 77 |
| self-energy-insertion pair | complete | Phase 80 |
| vacuum polarization | complete | Phase 79 |
| seven-diagram exact sum | complete | Phase 82 |
| protected two-loop regression | complete | Phase 83 |

The final two-loop coefficient is

$$
A_1^{(4)}
=
\frac{197}{144}
+\frac{\pi^2}{12}
+\frac34\zeta(3)
-\frac{\pi^2}{2}\ln2.
$$

The ordinary-ladder reduction baseline is

$$
72\longrightarrow40\longrightarrow12.
$$

The corner/self-energy infrared coefficient is exactly zero after assembly.

---

## Current development objective

The next objective is **not** to re-solve the completed two-loop diagrams. It is to generalize the successful two-loop machinery so that a larger fraction of higher-loop work can reuse common infrastructure instead of graph-specific one-off code.

The working direction is:

$$
\text{validated two-loop semi-automation}
\longrightarrow
\text{more general topology / renormalization / projector / reduction layers}
\longrightarrow
\text{three-loop support}.
$$

---

## Priority 1 — topology to ordered amplitude

### Goal

Reduce the amount of human work required to convert a Feynman graph into the correct noncommuting QED amplitude.

### Needed work

- represent electron/photon connectivity in a reusable topology object,
- generate ordered fermion chains without losing gamma/propagator order,
- attach momentum routing explicitly,
- carry symmetry/sign/closed-fermion-loop factors as inspectable metadata,
- reject ambiguous topology instead of guessing.

### Completion criterion

A supported graph topology should generate the same ordered raw amplitude that is currently supplied manually in the validated two-loop samples.

---

## Priority 2 — generalized divergent-subgraph and renormalization planning

### Goal

Extend the current specific self-energy / vacuum-polarization / corner machinery toward a reusable renormalization-planning layer.

### Needed work

- automatic candidate divergent-subgraph discovery for supported topologies,
- superficial-degree bookkeeping,
- nested/disjoint/overlapping relation construction,
- forest generation,
- explicit mapping from subgraph type to available counterterm structure,
- on-shell conditions kept distinct from MS/MS-bar pole subtraction,
- no silent inference of finite on-shell constants.

### Completion criterion

For a supported graph, QEDCalc should be able to report

$$
\text{graph}
\longrightarrow
\text{divergent subgraphs}
\longrightarrow
\text{required subtraction plan}
$$

before the user starts the detailed algebra.

---

## Priority 3 — unified magnetic-projector API

### Goal

Consolidate projector logic that is currently distributed across one-loop, crossed-ladder, ordinary-ladder, corner, and self-energy routes.

### Needed work

- common form-factor decomposition object,
- explicit support for finite-$q$ and $q\to0$ limits,
- support for $D$-dimensional projectors when evanescent terms matter,
- standardized normalization checks against the Schwinger one-loop result,
- common output format for projector residuals and coefficient tables.

### Completion criterion

A graph-specific module should supply its vertex expression while the projector layer handles the common $F_1/F_2$ extraction logic.

---

## Priority 4 — reusable parameter / sector strategy library

### Goal

Retain successful variable transformations and singular-region strategies as reusable named transformations rather than graph-local code.

Candidate strategies include:

- simplex parameter maps,
- Cheng--Wu gauges,
- projective variables,
- triangular-domain maps,
- soft/hard decompositions,
- overlap add-subtract constructions,
- logarithmic endpoint maps,
- cancellation-first denominator reductions.

### Completion criterion

Each strategy should expose its Jacobian, domain, inverse where practical, and exact measure audit.

---

## Priority 5 — IBP / master-integral automation

### Goal

Generalize the ordinary-ladder experience beyond its fixed 40-target / 12-master system.

### Needed work

- broader sector scheduling,
- scaleless-sector detection,
- better seed-closure diagnostics,
- modular/finite-field acceleration where useful,
- robust rational reconstruction,
- external reduction comparison hooks,
- master-integral boundary/value registry,
- explicit distinction between reduction and analytic master evaluation.

### Completion criterion

New denominator families should be reducible without embedding a precomputed graph-specific matrix as the primary route.

---

## Priority 6 — three-loop preparation

The known three-loop vertex problem contains many more diagrams and more complicated subgraph structure. Before large-scale three-loop derivations, establish a repeatable workflow for:

1. graph/topology registration,
2. raw ordered amplitude generation,
3. subgraph/forest audit,
4. magnetic projection,
5. parameter-family construction,
6. IBP/master reduction,
7. analytic or controlled numerical master evaluation,
8. release checkpoints and cross-diagram cancellation tests.

The v0.90 two-loop regression must remain green throughout this work.

---

## Historical-only open item

The precise algebraic origin of the Karplus--Kroll crossed-ladder discrepancy

$$
\Delta_{\mathrm X}=\frac1{32}
$$

has not been localized inside the 1950 calculation.

This is a provenance/history question only. The modern crossed-ladder coefficient and the complete two-loop coefficient are already independently validated.

---

## Documentation policy from v0.90 onward

- `README.md` and `README_JP.md` describe the current release.
- `REFERENCE.md` and `REFERENCE_JP.md` describe the current API/capabilities and current validated physics routes.
- `ROADMAP.md` contains current and future work only.
- `CHANGELOG.md` contains a concise newest-first release summary.
- Long cumulative pre-v0.90 versions are retained in `doc/archive/` rather than mixed into current-state documents.
- Detailed two-loop calculation/program manuals remain in `doc/QEDCalc_2loop_5sample_manuals_v2/`.

---

## Definition of success for the next major milestone

A future milestone should not be defined only by adding more formulas. It should measurably reduce the amount of graph-specific manual wiring required while preserving inspectability.

A good next milestone would demonstrate that several new higher-loop diagrams can share the same topology, renormalization, projector, and reduction infrastructure with only their physical graph data supplied explicitly.
