# QEDCalc v0.90.0 Reference Manual

## 1. Purpose

QEDCalc is a symbolic QED calculation toolkit designed to divide long perturbative calculations into small, inspectable mathematical and physical operations. The user controls the physical order of operations; QEDCalc performs the mechanical algebra and exposes intermediate results for audit.

The current v0.90.0 milestone establishes a durable two-loop baseline for the electron anomalous magnetic moment.

Core principles:

- The user determines the physical calculation route.
- Noncommuting factor order is explicit and never reconstructed by guesswork.
- Dirac algebra, traces, projectors, parameterization, loop shifts, tensor reduction, renormalization bookkeeping, IBP reduction, and regression checks are separated into inspectable stages.
- Intermediate expressions can be rendered as LaTeX/Markdown.
- Undefined symbols, incomplete bases, or unsupported topology operations are rejected rather than guessed.
- Exact symbolic residuals are preferred whenever possible.

The bundled one-loop vertex workflow reproduces

$$
F_2(0)=\frac{\alpha}{2\pi}.
$$

The completed two-loop release baseline reproduces

$$
A_1^{(4)}
=
\frac{197}{144}
+\frac{\pi^2}{12}
+\frac34\zeta(3)
-\frac{\pi^2}{2}\ln2.
$$

---

## 2. Current version and environment

Current release baseline: **QEDCalc v0.90.0**.

`pyproject.toml` is the authoritative package-version source.

Requirements for the scientific calculation layer:

- Windows 11
- Python 3.11+
- SymPy 1.13+

Run `setup_env.bat` to create `.venv` and install the project requirements.

The v0.90 standard-library two-loop ZIP regression can run without SymPy. Scientific symbolic checkpoints are then skipped explicitly rather than treated as failures.

---

## 3. Main repository structure

```text
QEDCalc/
├─ data/
├─ doc/
├─ examples/
├─ input/
├─ output/
├─ qedcalc/
│  ├─ config/
│  ├─ core/
│  ├─ history/
│  ├─ latex/
│  ├─ operations/
│  ├─ parser/
│  └─ validation/
├─ tests/
├─ conventions.txt
├─ pyproject.toml
├─ README.md
├─ README_JP.md
├─ REFERENCE.md
├─ REFERENCE_JP.md
├─ ROADMAP.md
└─ CHANGELOG.md
```

Historical cumulative versions of the former top-level reference, roadmap, and changelog are preserved under `doc/archive/`.

---

## 4. QED-LaTeX input model

QEDCalc parses a restricted QED-oriented LaTeX language rather than arbitrary mathematical LaTeX.

Typical objects include:

- scalar symbols,
- Lorentz vectors and indices,
- gamma matrices,
- Feynman slashes,
- metric tensors,
- scalar products,
- fermion and photon propagator structures,
- commutative products,
- noncommutative products,
- loop-integral expressions.

The important rule is that fermion-chain order is preserved explicitly. QEDCalc does not infer a lost noncommuting order from a scalarized expression.

Main entry point:

```python
from qedcalc import parse_latex
expr = parse_latex(source)
```

---

## 5. Calculation conventions

`conventions.txt` centralizes convention-dependent settings such as:

- metric signature,
- gauge,
- renormalization scheme,
- dimensional-regularization dimension,
- MS/MS-bar subtraction settings,
- coupling and loop-measure ownership for subdiagrams.

Load with:

```python
from qedcalc.config import load_conventions
conv = load_conventions()
```

QEDCalc does not silently convert an unsupported convention into another one. For example, a bridge implemented only for the Feynman-gauge numerator should reject an unsupported covariant-gauge path rather than drop longitudinal terms.

---

## 6. Main algebraic capabilities

### 6.1 Dirac and Lorentz algebra

The operations layer supports the Dirac/Lorentz manipulations needed by the validated one- and two-loop routes, including fully contracted trace paths optimized to avoid materializing unnecessarily large metric tensors.

### 6.2 Feynman parameterization

Unit and positive-integer propagator powers can be parameterized explicitly. Multi-loop quadratic forms can be square-completed and loop shifts can be applied simultaneously to the numerator.

### 6.3 Tensor reduction

Even-rank isotropic tensor reductions are available in general dimension. Mixed multi-loop reductions use the inverse quadratic matrix after square completion.

### 6.4 Dimensional regularization and poles

QEDCalc can keep UV and IR regulators conceptually distinct, extract Laurent poles, and apply explicit dimensional-regularization convention factors.

### 6.5 Counterterms and subdiagrams

Counterterm definitions, explicit insertions/replacements, declared subdiagram relations, compatible forests, contracted graphs, Taylor subtraction, and BPHZ local-counterterm machinery are available as separate layers.

Finite on-shell counterterms are not guessed from pole parts alone; physical renormalization conditions remain explicit inputs.

### 6.6 IBP / Laporta infrastructure

The operations layer includes denominator-family representations, generic IBP-equation generation, finite sparse Laporta elimination, sector signatures, symmetry canonicalization, exact-rational probes, and rational reconstruction tools used during the ordinary-ladder development.

---

## 7. Magnetic form factor

For an on-shell electromagnetic vertex,

$$
\Gamma_\mu^{\mathrm R}(p',p)
=
\gamma_\mu F_1(q^2)
+\frac{i\sigma_{\mu\nu}q^\nu}{2m}F_2(q^2).
$$

The anomalous magnetic moment is

$$
a_e=F_2(0).
$$

QEDCalc contains validated projector routes that remove the Dirac form-factor contribution and isolate the Pauli form factor. The exact projector representation differs by calculation route, especially when a finite-$q$ or $D$-dimensional treatment is required.

---

## 8. Two-loop diagram classes completed at v0.90.0

The seven two-loop diagrams are grouped as follows:

| Class | Number of diagrams | Release checkpoint |
|---|---:|---|
| crossed ladder | 1 | Phase 78 |
| ordinary ladder | 1 | Phase 81 |
| corner | 2 | Phase 77 |
| self-energy insertion | 2 | Phase 80 |
| vacuum polarization | 1 | Phase 79 |
| integrated seven-diagram audit | 7 total | Phase 82 |
| complete two-loop regression | 7 total | Phase 83 |

### 8.1 Crossed ladder

Validated route:

$$
\text{raw graph}
\longrightarrow
\text{magnetic projector}
\longrightarrow
\text{projective representation}
\longrightarrow
\text{one-variable kernel}
\longrightarrow
\text{endpoint assembly}.
$$

Final coefficient:

$$
A_{\mathrm X}
=
\frac16
+\frac{13\pi^2}{36}
+\frac54\zeta(3)
-\frac{5\pi^2}{6}\ln2.
$$

The historical Karplus--Kroll `1/32` discrepancy is retained as an unresolved provenance question only; it does not alter the validated modern coefficient.

### 8.2 Ordinary ladder

The corrected physical spin-sum route closes through

$$
72\text{ projector terms}
\longrightarrow
40\text{ canonical IBP targets}
\longrightarrow
12\text{ analytic masters}.
$$

Bare result:

$$
A_{\mathrm L,bare}
=
-\frac{3}{4(D-4)}
+\frac{107}{48}
+\frac{\pi^2}{18}
+O(D-4).
$$

After on-shell subtraction:

$$
A_{\mathrm L}
=
\frac{11}{48}
+\frac{\pi^2}{18}.
$$

### 8.3 Corner pair

The corner route includes raw-pair parsing, magnetic projection, the inner-vertex UV subtraction, renormalized sectors, soft/hard ownership, and IR asymptotics.

$$
A_{\mathrm C}
=
\ln\frac1\rho
-\frac{67}{24}
+\frac{\pi^2}{18}
-\frac12\zeta(3)
+\frac{\pi^2}{3}\ln2
+o(1).
$$

### 8.4 Self-energy-insertion pair

The raw left/right insertion diagrams are audited through self-energy-subdiagram detection, on-shell renormalization, reinsertion, finite integration, and IR asymptotics.

$$
A_{\mathrm S}
=
\ln\rho
+\frac{11}{24}
-\frac{\pi^2}{18}
+o(1).
$$

Thus the corner/self-energy IR logarithms cancel exactly:

$$
\ln\frac1\rho+\ln\rho=0.
$$

### 8.5 Vacuum polarization

The route covers complete raw input, closed electron-loop trace detection, Dirac trace, tensor reduction, transversality, on-shell subtraction, outer magnetic insertion, and endpoint evaluation.

$$
A_{\mathrm{VP}}
=
\frac{119}{36}
-\frac{\pi^2}{3}.
$$

---

## 9. Complete two-loop regression

Run:

```text
run_v090_validation.bat
```

The standard-library Phase-83 regression checks:

```text
Phase-83 complete two-loop regression PASS
diagram count = 7
IR log residual = 0
ordinary ladder reduction = 72 -> 40 -> 12
total basis coefficients = ('197/144', '1/12', '3/4', '-1/2', '0')
historical 1/32 origin resolved = False
QEDCalc 0.90.0
v0.90 validation PASS
```

The coefficient vector is expressed in the basis

$$
\left\{
1,
\pi^2,
\zeta(3),
\pi^2\ln2,
\ln\frac1\rho
\right\}.
$$

The final zero is the exact IR-log cancellation.

The durable baseline is stored in:

```text
data/two_loop_v090_baseline.json
```

---

## 10. Automation boundary at v0.90.0

QEDCalc should currently be described as a **semi-automatic higher-order QED calculation framework**, not as a fully automatic Feynman-diagram solver.

### Automated or strongly assisted

- QED-oriented LaTeX parsing,
- ordered algebraic representation,
- selected topology/subdiagram detection,
- Dirac algebra and traces,
- magnetic projection,
- Feynman parameterization,
- multi-loop square completion and shifts,
- tensor reduction,
- selected UV/IR and counterterm audits,
- IBP/Laporta infrastructure,
- graph-specific analytic checkpoints,
- full two-loop release regression.

### Still requires human physical judgment

- constructing or validating the original ordered Feynman-rule expression,
- choosing momentum routing when several equivalent routes exist,
- deciding which subgraph is to be renormalized and under which physical condition,
- choosing useful variable transformations, sector splits, and endpoint strategies,
- deciding how graph-specific outputs are connected to the next specialized stage,
- identifying suitable analytic master-integral representations for new topologies.

QEDCalc intentionally favors an inspectable calculation route over silent guessing.

---

## 11. Documentation

- `README.md` — English Quick Start
- `README_JP.md` — Japanese Quick Start
- `REFERENCE.md` — English current reference
- `REFERENCE_JP.md` — Japanese current reference
- `ROADMAP.md` — current development roadmap
- `CHANGELOG.md` — current release history summary
- `doc/QEDCalc_2loop_5sample_manuals_v2/` — detailed two-loop sample calculation/program manuals
- `doc/QEDCalc_2loop_Milestone_Automation_Scope_and_Remaining_Manual_Work_EN.md` — two-loop automation milestone report
- `doc/QEDCalc_2loop_Milestone_Automation_Scope_and_Remaining_Manual_Work_JP.md` — Japanese milestone report
- `doc/archive/` — cumulative historical versions preserved during the v0.90 documentation cleanup

---

## 12. Current limitations and next direction

The v0.90 milestone freezes the completed two-loop result. The next major development direction is to generalize the successful two-loop machinery before and during three-loop work.

Priority areas include:

1. topology-to-ordered-amplitude generation,
2. more general automatic divergent-subgraph and renormalization planning,
3. unified magnetic-projector APIs,
4. reusable parameter/sector strategy libraries,
5. broader master-integral and IBP automation,
6. three-loop diagram support while retaining the v0.90 two-loop regression as a protected baseline.

For detailed priorities, see `ROADMAP.md`.
