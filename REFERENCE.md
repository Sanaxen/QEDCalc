# QEDCalc v0.52.0 Reference Manual

## 1. Purpose

QEDCalc is designed to process QED calculations as a sequence of small, inspectable mathematical and physical operations rather than as a black-box diagram evaluator.

Core principles:

- The user controls the physical order of operations.
- Dirac algebra, denominator manipulation, Feynman parameterization, loop shifts, and projectors are separate functions.
- Intermediate expressions can be checked as LaTeX/Markdown.
- Undefined symbols or incomplete bases are not silently guessed.
- One-loop functionality is generalized gradually toward two-, three-, and four-loop calculations.

The bundled one-loop vertex example reaches

$$
F_2(0)=\frac{\alpha}{2\pi}.
$$

## 2. Environment and setup

Requirements:

- Windows 11
- Python 3.11+
- SymPy 1.13+

Run `setup_env.bat` once. It creates `.venv` and installs `requirements.txt`.

Batch files:

- `run_qedcalc.bat`: one-loop vertex workflow
- `run_multiloop_demo.bat`: reusable multi-loop foundation demo
- `run_tests.bat`: pytest

## 3. Symbol table

`symbols.txt` predefines accepted scalars, constants, vectors, and Lorentz indices. Greek symbols are written in LaTeX notation. Undefined symbols are errors.

## 4. QED-LaTeX parser

Main API:

```python
from qedcalc import parse_latex
expr = parse_latex(source)
```

Major supported constructs include gamma matrices, Feynman slashes, metric tensors, fractions, scalar products, powers, parentheses, sums, and products. Dirac products preserve factor order through `NCProduct`.

QEDCalc is not a general-purpose LaTeX parser.


## 4A. `conventions.txt` — calculation conventions

v0.26.0 continues to centralize convention-dependent settings in `conventions.txt`. No interactive convention prompt is used during a calculation.

```python
from qedcalc.config import load_conventions

conv = load_conventions()
```

The main keys are:

- `metric_signature`: `+---` or `-+++`
- `gauge`: `feynman` or `covariant`
- `renormalization_scheme`: `on_shell`, `MS`, `MSbar`, or `BPHZ`
- `dimreg_dimension`: default `4 - 2*epsilon`
- `dimreg_subtraction`: `MS`, `MSbar`, or `none`
- `msbar_factor`: whether to include $S_\epsilon=(4\pi e^{-\gamma_E})^\epsilon$
- `subdiagram_include_coupling`
- `subdiagram_include_loop_measure`
- `subdiagram_include_i`
- `coupling_symbol`
- `loop_measure_denominator_latex`
- `loop_i_factor_latex`

`QEDConventions.compact_outer_one_loop_prefactor_latex()` constructs the normalization left after contracting one one-loop subdiagram from a two-loop graph. With the default settings it returns

$$
\frac{e^2}{(2\pi)^4 i}
$$

`contract_self_energy_to_outer_loop()` now accepts `conventions=...`. If `outer_prefactor_latex` is omitted, the prefactor is generated from the convention file. The explicit prefactor argument remains available as an override.

The raw self-energy bridge currently performs full automatic internal-photon numerator reduction only for `gauge=feynman`. Selecting `gauge=covariant` raises `NotImplementedError` rather than silently dropping the longitudinal term.

`dimreg_scale_factor()` and `renormalized_dimreg_series()` also accept `conventions=...`, using `dimreg_subtraction` and `msbar_factor`.

Use `run_conventions_demo.bat` to inspect the loaded settings. The generated report is `output/conventions.md`.

---

## 5. Core expression types

Important classes include `Symbol`, `Vector`, `Index`, `Gamma`, `Slash`, `Metric`, `ScalarProduct`, `VectorComponent`, `Product`, `NCProduct`, `Fraction`, `FeynmanParamIntegral`, `GeneralFeynmanParamIntegral`, `CompletedSquare`, `MultiLoopCompletedSquare`, `SpinorSandwich`, `FormFactorDecomposition`, `PoleTerm`, `LaurentResult`, `Counterterm`, and `CountertermInsertion`.

## 6. Multi-loop quadratic forms

`complete_multiloop_square()` interprets a scalar quadratic form as

$$
K^T M K+2K\cdot B+C
$$

and returns

$$
\left(K+M^{-1}B\right)^T
M
\left(K+M^{-1}B\right)
+C-B^TM^{-1}B.
$$

`shifted_multiloop_denominator()` produces the denominator after introducing new shifted loop momenta.

### `shift_multiloop_momenta_in_numerator()`

Added in v0.11.0. It applies all loop shifts simultaneously to numerator structures such as `Slash(k)`, vector components, and scalar products. Simultaneous substitution prevents mixed structures such as $k\cdot l$ from being corrupted by sequential replacements.

## 7. Feynman parameterization

### Unit powers

`feynman_parameterize_n()` implements

$$
\frac{1}{D_1\cdots D_N}
=
(N-1)!\int_{\Delta_{N-1}}
\frac{d^{N-1}x}{(\sum_i x_iD_i)^N}.
$$

### Arbitrary positive integer powers

`feynman_parameterize_powers()` was added in v0.11.0. For positive integer $a_i$,

$$
\frac{1}{D_1^{a_1}\cdots D_N^{a_N}}
=
\frac{\Gamma(A)}{\prod_i\Gamma(a_i)}
\int_{\Delta_{N-1}}
\frac{\prod_i x_i^{a_i-1}}
{(\sum_i x_iD_i)^A}
d^{N-1}x,
\qquad A=\sum_i a_i.
$$

Powers can be inferred from positive `Power(...)` denominator factors or supplied explicitly.

## 8. General-D scalar loop integrals

### `euclidean_scalar_loop_integral()`

Added in v0.11.0. It returns the SymPy expression for

$$
\int d^Dl\,
\frac{(l^2)^r}{(l^2+\Delta)^n}
$$

using

$$
\pi^{D/2}\Delta^{D/2+r-n}
\frac{\Gamma(r+D/2)\Gamma(n-r-D/2)}
{\Gamma(D/2)\Gamma(n)}.
$$

It intentionally does **not** insert Wick-rotation $i$ factors, signs, $(2\pi)^{-D}$ normalization, renormalization scales, or MS-bar factors. Those belong to an explicit convention layer.

### `dimensional_regularized_loop_series()`

Substitutes $D=4-2\epsilon$ and returns a SymPy Laurent series in $\epsilon$.

## 9. Symmetric tensor reduction

`symmetric_rank2()` contains selected rank-2 rules used by the one-loop workflow.

`symmetric_rank4()` implements

$$
l^\mu l^\nu l^\rho l^\sigma
\to
\frac{l^4}{D(D+2)}
\left(
g^{\mu\nu}g^{\rho\sigma}
+g^{\mu\rho}g^{\nu\sigma}
+g^{\mu\sigma}g^{\nu\rho}
\right).
$$

## 10. UV/IR Laurent poles

`extract_laurent_poles()` separates negative regulator powers and the finite term. Separate symbols such as `epsilon_UV` and `epsilon_IR` can be used to keep UV and IR poles distinct.

## 11. Counterterms

`make_counterterm()` stores a name, coefficient, structure, and loop order.

`counterterm_contribution()` converts it to an algebraic contribution.

`add_counterterms()` adds explicit counterterm contributions.

### `replace_factor_with_counterterm()`

Added in v0.11.0. Replaces one explicitly selected top-level `Product`/`NCProduct` factor with a counterterm contribution.

### `insert_counterterm_factor()`

Inserts a counterterm contribution immediately before or after a selected factor.

QEDCalc does not guess where a counterterm belongs. The caller explicitly chooses the factor and whether replacement or insertion is appropriate for the chosen diagram and convention.

## 12. One-loop magnetic form factor

The bundled one-loop workflow reduces the current, projects the magnetic form factor, and obtains

$$
F_{2,\mathrm{num}}=4m^2(x+y)(1-x-y),
$$

$$
\Delta=m^2(x+y)^2,
$$

followed by

$$
\int_0^1dx\int_0^{1-x}dy\,
\frac{4(1-x-y)}{x+y}=2,
$$

and finally

$$
F_2(0)=\frac{\alpha}{2\pi}.
$$

## 13. Markdown sessions

`MarkdownSession` writes calculation history to Markdown. Display equations always have a blank line before the opening `$$` and after the closing `$$`.

## 14. Internal identifiers and LaTeX display names

QEDCalc may use ASCII-friendly identifiers internally, but `render_latex()` converts them to conventional QED notation for mathematical output.

| Internal identifier | LaTeX output |
|---|---|
| `deltaZ1` | `\delta Z_{1}` |
| `deltaZ2` | `\delta Z_{2}` |
| `deltaZ3` | `\delta Z_{3}` |
| `delta_m` | `\delta m` |
| `zeta` | `\zeta` |
| `eta` | `\eta` |
| `omega` | `\omega` |
| `epsilon_UV` | `\epsilon_{\mathrm{UV}}` |
| `epsilon_IR` | `\epsilon_{\mathrm{IR}}` |

For example, a vertex counterterm is rendered as

$$
\delta Z_1\gamma_\mu
$$

rather than exposing the internal identifier `deltaZ1`.

---

## 15. v0.12.0 additions

### 14.1 General even-rank tensor reduction

`symmetric_even_rank()` implements the isotropic rank-$2n$ rule

$$
l^{\mu_1}\cdots l^{\mu_{2n}}
\longrightarrow
\frac{(l^2)^n}
{D(D+2)\cdots(D+2n-2)}
\sum_{\mathrm{pairings}}
g^{\mu_i\mu_j}\cdots .
$$

Rank six automatically generates all 15 complete pairings. `dimension` may be an integer or a SymPy expression such as $4-2\epsilon$.

### 14.2 MS / MS-bar convention layer

`qedcalc.operations.renormalization` makes dimensional-regularization conventions explicit.

QEDCalc defines

$$
S_\epsilon
=
\left(4\pi e^{-\gamma_E}\right)^\epsilon
$$

and uses, at $L$ loops,

$$
\mu^{2L\epsilon}S_\epsilon^L
$$

for `scheme="MSbar"`. For `scheme="MS"`, only $\mu^{2L\epsilon}$ is included.

Main APIs:

```python
dimreg_scale_factor(...)
apply_dimreg_convention(...)
pole_part(...)
minimal_subtract(...)
renormalized_dimreg_series(...)
```

`renormalized_dimreg_series()` returns the scale factor, Laurent series, pole part, and minimally subtracted result separately.

### 14.3 UV / IR bookkeeping

`bookkeep_uv_ir()` treats `epsilon_UV` and `epsilon_IR` as independent regulators and separates UV-only poles, IR-only poles, mixed UV/IR poles, the finite part, and positive-power regular remainder.

### 14.4 Standard QED counterterm library

The library now provides builders for

$$
\delta Z_1\gamma_\mu,
$$

$$
\delta Z_2\rlap{/}p,
$$

$$
\delta m,
$$

and

$$
\delta Z_3
\left(k^2g_{\mu\nu}-k_\mu k_\nu\right).
$$

APIs:

```python
qed_vertex_counterterm(...)
qed_electron_wavefunction_counterterm(...)
qed_mass_counterterm(...)
qed_photon_wavefunction_counterterm(...)
qed_counterterm_library(...)
```

The numerical coefficients are intentionally not guessed; they remain explicit inputs tied to the chosen renormalization scheme and loop order.

## 16. v0.13.x subdiagram / counterterm management

The v0.13.x line keeps graph-topology metadata explicit instead of trying to infer divergent subgraphs from a bare algebraic formula alone.

Main APIs include:

```python
Subdiagram(...)
relation(...)
forest_compatible(...)
enumerate_forests(...)
CountertermAssignment(...)
assemble_renormalized_amplitude(...)
renormalization_plan(...)
minimal_r_operation(...)
```

Declared subdiagrams can be classified as nested, disjoint, or overlapping, and topology-compatible forests can be enumerated. For MS/MS-bar workflows, evaluated subdiagram poles may be converted to subtraction counterterms through

$$
C(\gamma)
=
-\operatorname{Pole}[\gamma].
$$

Finite on-shell counterterms are not inferred from poles alone because they depend on renormalization conditions.

---

## 17. Current limitations

v0.16.0 completes the bundled one-loop vertex workflow and provides reusable multi-loop topology, renormalization, and tensor foundations. It is not yet a fully automatic evaluator for arbitrary two-loop graphs.

Main limitations:

- richer topology templates for branching graphs and non-contiguous contractions
- complete Minkowski $i$ / Wick-rotation / $(2\pi)^{-D}$ convention management
- arbitrary complex denominator powers in Feynman parameterization
- IBP reduction
- master-integral database/interface
- sector decomposition
- general end-to-end two-loop diagram automation

---

## 18. Tests

v0.19.0: 100 tests passed.

Run `run_tests.bat`.

---

## 19. Contracted graph / Taylor subtraction / forest formula

Main APIs:

```python
ContractedGraph
TaylorSubtractionSpec
contract_graph(...)
taylor_operator(...)
apply_taylor_spec(...)
bphz_local_counterterm(...)
bphz_subtract(...)
forest_formula(...)
```

### 19.1 Contracted graph

`contract_graph()` contracts declared subdiagrams into local `CT[...]` topology vertices and stores the topology of $G/F$. Nested forests are contracted from inner to outer subgraphs.

### 19.2 Taylor subtraction

`taylor_operator()` returns the multivariate Taylor polynomial of total degree $\leq\omega$ in explicitly supplied commuting variables.

$$
t^{\omega}f(p) = \sum_{|a|\leq\omega}\frac{(p-p_0)^a}{a!}\left.\partial^a f\right|_{p=p_0}
$$

### 19.3 BPHZ local counterterm

$$
C_{\mathrm{BPHZ}}(\gamma) = -t_{\gamma}^{\omega(\gamma)}\Gamma_{\gamma}
$$

`bphz_subtract()` returns $(1-t^\omega)\Gamma$ and is distinct from MS / $\overline{\mathrm{MS}}$ pole subtraction.

### 19.4 Zimmermann forest sum

`forest_formula()` enumerates compatible forests, constructs contracted topologies, applies the forest sign $(-1)^{|F|}$, and sums explicit amplitudes supplied by an `amplitude_provider`.

---

## 20. Topology-to-amplitude layer

### 19.1 `TopologyFactor`

Associates one topology identifier with its QED expression.

```python
TopologyFactor(factor_id, expression, commutative=False)
```

Non-commuting factors preserve their declared order. Only explicitly commuting factors should use `commutative=True`.

### 19.2 `QEDAmplitudeTemplate`

Stores the **explicit factor order** associated with a Feynman graph. QEDCalc does not reconstruct graph ordering from a bare algebraic expression after that information has been lost.

### 19.3 `build_bare_amplitude()`

Builds the bare algebraic amplitude from the explicit topology template.

### 19.4 `build_contracted_amplitude()`

Combines a `ContractedGraph` with declared local vertices to build the algebraic amplitude for $G/F$.

For safety, automatic replacement currently requires the subdiagram to form a contiguous block in the ordered template. Non-contiguous replacements are rejected rather than guessed.

---

## 21. Mixed multi-loop tensor reduction

### 19.1 `symmetric_multiloop_tensor()`

After square completion, assume the remaining loop dependence is only through

$$
Q = L^TML.
$$

For $n$ loop vectors in Lorentz dimension $D$, define

$$
N = nD.
$$

An even tensor of rank $2r$ is reduced as

$$
L_{i_1}^{\mu_1}\cdots L_{i_{2r}}^{\mu_{2r}} \longrightarrow \frac{Q^r}{N(N+2)\cdots(N+2r-2)}\sum_{\mathrm{pairings}}\prod\left[(M^{-1})_{ij}g^{\mu\nu}\right].
$$

For rank 2,

$$
L_i^\mu L_j^\nu \longrightarrow \frac{Q}{nD}(M^{-1})_{ij}g^{\mu\nu}.
$$

Use this only after square completion when the loop-momentum dependence is isotropic in the quadratic form $Q$.

---

## 22. Automation boundary in v0.16.0

Automated:

- bare amplitude construction from an explicit factor template
- contracted-topology bookkeeping for declared subdiagrams
- contracted-amplitude construction when local vertices are supplied
- multi-loop square completion
- mixed-loop tensor reduction
- forest/Taylor/counterterm bookkeeping

Not inferred automatically:

- Feynman-graph topology from a bare algebraic expression alone
- non-contiguous topology rewiring
- complete Feynman-rule generation for arbitrary branching contracted graphs

These are intentional safety boundaries to avoid silently generating the wrong graph topology.


---

## Two-loop vacuum-polarization trial

v0.16.0 uses the vacuum-polarization graph as the first real two-loop test case. The closed electron-loop numerator is read from QED-LaTeX, evaluated with `dirac_trace_4d()`, shifted, odd terms are removed, and the rank-2 symmetric tensor reduction is applied. The finite on-shell-renormalized scalar kernel is then combined with the one-loop magnetic kernel.

The final finite coefficient is evaluated from

$$
A_{\mathrm{VP}}
=
2\int_0^1dx\,(1-x)
\int_0^1dz\,z(1-z)
\ln\left[
1+\frac{x^2}{1-x}z(1-z)
\right].
$$

Numerically,

$$
A_{\mathrm{VP}}
=
0.0156874218591026826107252222635\ldots
$$

and independent analytic recognition in the {1, $\pi^2$} basis gives

$$
\boxed{
A_{\mathrm{VP}}
=
\frac{119}{36}-\frac{\pi^2}{3}
}.
$$

The complete original two-loop LaTeX diagram is not yet parsed as one expression. The topology and the closed electron-loop subdiagram are supplied explicitly. This is an intentional safety boundary: QEDCalc does not reconstruct missing Feynman topology by guessing from algebra alone.


## 25. v0.17.0 self-energy-insertion two-loop trial

The left/right electron self-energy insertion pair is treated as an explicit one-loop self-energy subdiagram inserted into the outer magnetic vertex. The new `qedcalc.operations.self_energy` module provides denominator helpers, generic on-shell counterterm formulas, UV-cancellation checks, logarithm rationalization, and finite-integral cross checks.

For

$$
\Sigma(r)=mA(r^2)+\rlap{/}r B(r^2),
$$

QEDCalc implements

$$
\delta m=m[A(m^2)+B(m^2)]
$$

and

$$
\delta Z_2=B(m^2)+2m^2[A'(m^2)+B'(m^2)].
$$

The UV numerator after on-shell subtraction reduces to zero. The finite and IR checkpoints are

$$
A_A(0)=-\frac1{24}-\frac{\pi^2}{18},
$$

$$
A_B(\rho)=\ln\rho+\frac12+o(1),
$$

and therefore

$$
A_{\mathrm S}=-\frac12\ln\rho^{-2}+\frac{11}{24}-\frac{\pi^2}{18}.
$$

The complete original aligned two-loop LaTeX expression is not yet parsed as a single object; the self-energy subdiagram is supplied explicitly.

## 27. v0.19.0 crossed-ladder two-loop trial

The crossed-ladder trial starts from the independently derived projective/one-variable checkpoint. It does not yet regenerate the several-hundred-term raw Dirac reduction and the five-parameter integrand $G_{\mathrm X}$ automatically.

`crossed_projective_forms()` returns the projective polynomials $\Delta$ and $W$ and verifies that both are linear in $V$. `crossed_tq_transform()` implements $h=(1-t)/t$, $R=q/t$ with Jacobian $1/t^3$, and `crossed_tq_log_argument()` returns the reduced logarithm argument.

`crossed_canonical_kernel()` implements the canonical one-variable kernel using $L=\ln q$, $M=\ln(1-q)$ and $D(q)=\operatorname{Li}_2(q)-\operatorname{Li}_2(2-1/q)$. `crossed_half_sector_result()` evaluates the $q=1/2$ sector, while `crossed_endpoint_combined_kernel()` combines endpoint-singular pieces before integration. `crossed_endpoint_asymptotics()` verifies cancellation of cubic, quadratic and linear cutoff logarithms against the total-derivative boundary contribution.

The final analytic checkpoint is

$$
I_{\mathrm X}
=
\frac16+\frac{13\pi^2}{36}+\frac54\zeta(3)-\frac{5\pi^2}{6}\ln2.
$$

Run `run_crossed_ladder_2loop_demo.bat`; output is written to `output/crossed_ladder_2loop_trial.md`.



## 28. v0.21.0 corner (IIc) two-loop trial

### 28.1 Scope

`qedcalc.operations.corner` verifies the downstream calculation beginning from the independently derived UV-finite corner parameter representation. It does not yet regenerate the complete projected finite kernel directly from the original six-denominator two-loop LaTeX expression.

### 28.2 Soft kernel and IR logarithm

`corner_soft_kernel()` returns

$$
\mathcal S
=
\frac{2RSUv(4R+S+4v)}{(R+v)^2(1+U^2)(R+S+v)^4}.
$$

The spatial soft kernel integrates first over $S$ to $2Rv/(R+v)^3$ and then over $R$ to 1. Therefore `corner_soft_ir_coefficient()` returns the exact coefficient 1 of $\ln(1/\rho)$.

### 28.3 Momentum shift

`corner_shifted_p_minus_k()` implements

$$
p'-k\longrightarrow(1-uv)p'-u(1-v)p''-k,
$$

explicitly retaining the $-u(1-v)$ coefficient of $p''$.

### 28.4 Diagnostic soft/hard split

`corner_soft_finite_constant()` returns

$$
C_{\mathrm{soft}}
=
\frac{\pi^2}{6}+\ln^22-3\ln2-\frac74.
$$

Together with `corner_hard_remainder_from_soft_split()` it reproduces the finite corner result. This split is diagnostic only; the soft constant must not be added again to the final sector bookkeeping.

### 28.5 Hard and z sectors

`corner_hard_primary_result()` returns

$$
H_{K\kappa}^{(1)}
=
-\frac{19}{3}-\frac{15}{8}\zeta(3)+\frac{11\pi^2}{36}+\frac34\pi^2\ln2.
$$

`corner_shift_correction_result()` returns

$$
\Delta A_{\mathrm{shift}}
=
\frac83-\frac{\pi^2}{4}-\frac{\pi^2}{6}\ln2+\frac34\zeta(3).
$$

Their sum is

$$
H_{K\kappa}
=
-\frac{11}{3}-\frac98\zeta(3)+\frac{\pi^2}{18}+\frac{7\pi^2}{12}\ln2.
$$

`corner_z_sector_result()` returns

$$
A_z
=
\frac78+\frac58\zeta(3)-\frac{\pi^2}{4}\ln2.
$$

### 28.6 Final finite part

`corner_finite_result()` returns

$$
A_{\mathrm C,fin}
=
-\frac{67}{24}+\frac{\pi^2}{18}-\frac12\zeta(3)+\frac{\pi^2}{3}\ln2.
$$

`corner_result_difference()` simplifies the difference from the independent checkpoint exactly to zero.

### 28.7 IR cancellation

`corner_self_energy_ir_cancellation()` stores the corner IR-log coefficient $+1$ and the self-energy insertion coefficient $-1$ and verifies exact cancellation.

### 28.8 Execution

Run `run_corner_2loop_demo.bat`. Output is written to `output/corner_2loop_trial.md`.

## 29. v0.21.0 bare two-loop input and automatic closed-loop extraction

### 29.1 `LoopIntegralExpression`

Represents a bare loop-integral RHS as

$$
\mathcal N
\int d^Dk\,d^Dl\,
\mathcal I(k,l).
$$

It stores the original normalization LaTeX, loop momenta, integration dimension, and structurally parsed QED integrand.

### 29.2 `parse_loop_integral_latex()`

The supported base form is

```latex
<prefactor> \int d^4k\,d^4l <integrand>
```

v0.21.0 also structurally parses `\operatorname{tr}[...]`, `k_\rho`, and `k^\rho`.

### 29.3 `DiracTrace`

An explicit trace is stored as `DiracTrace(argument)` rather than opaque text. `find_dirac_traces()` discovers trace nodes and `require_single_dirac_trace()` validates a unique closed trace.

### 29.4 `reduce_trace_subdiagram_4d()`

This helper performs propagator recognition, fermion-propagator scalarization, numerator/denominator separation, and the four-dimensional Dirac trace of the numerator.

### 29.5 Current automation boundary

The automated path now reaches

$$
\text{bare 2-loop RHS}
\rightarrow
\text{DiracTrace detection}
\rightarrow
\text{propagator scalarization}
\rightarrow
\text{trace numerator}
\rightarrow
l=r-zk
\rightarrow
\text{rank-2 reduction}.
$$

Complete reconstruction of the transverse renormalized tensor and automatic connection to the outer magnetic kernel remain separate layers for now.


# 33. v0.22.0 — bare self-energy-insertion bridge

## 33.1 Supported raw input

The left and right self-energy-insertion diagrams can be supplied as complete bare two-loop RHS expressions to `parse_loop_integral_latex()`.

`find_self_energy_subdiagrams(diagram)` searches the ordered electron chain for

$$
S(r)\,\gamma^\alpha\,S(r-l)\,\gamma^\beta\,S(r).
$$

It requires equal repeated outer fermion propagators, a middle propagator differing by exactly one loop momentum, and a separate photon factor depending on that loop momentum and carrying the two gamma indices.

## 33.2 API

- `find_self_energy_subdiagrams(diagram)`
- `require_single_self_energy_subdiagram(diagram)`
- `contract_self_energy_subdiagram(diagram, renormalized=False)`
- `contract_self_energy_to_outer_loop(diagram, outer_prefactor_latex=None, conventions=None, renormalized=False)`

`SelfEnergySubdiagramMatch` records the insertion side, subloop momentum, external electron momentum, factor indices, gamma indices, and photon factor.

## 33.3 Numerator reduction

For the Feynman-gauge metric part, QEDCalc constructs

$$
\gamma^\alpha\left(m+\rlap{/}r-\rlap{/}l
ight)\gamma_\alpha
=4m-2\rlap{/}r+2\rlap{/}l.
$$

The right insertion automatically gives $r=p-k$; the left insertion gives $r=p'-k$.

## 33.4 Compact outer diagram

`contract_self_energy_to_outer_loop()` removes the subloop measure from the outer representation and returns a one-loop outer diagram containing

$$
S(r)\Sigma^{(1)}(r)S(r).
$$

Starting with v0.25.0, normalization ownership is declared in `conventions.txt`. When `outer_prefactor_latex` is omitted, QEDCalc constructs the compact outer prefactor from those settings. The explicit argument remains an override for special conventions. After the existing on-shell UV-cancellation check succeeds, `renormalized=True` renders the compact structure with $\Sigma_R^{(1)}$.

## 33.5 Current limits

- QEDCalc detects the declared ordered topology but does not invent rewiring when the pattern is absent.
- Raw internal-photon numerator reduction currently selects the Feynman-gauge metric part; full automatic longitudinal general-covariant-gauge processing is not yet implemented.
- Finite on-shell counterterms are still determined by the existing $A(r^2),B(r^2)$ layer rather than reconstructed completely from the raw general-gauge subloop.

All 118 tests pass in this release.


---

## 30. v0.25.0 ordinary-ladder raw-input bridge

### 30.1 Symbolic-$D$ loop measure

`parse_loop_integral_latex()` now preserves `\\int d^Dk\\,d^Dl` in addition to numeric loop dimensions.

### 30.2 `analyze_raw_ordinary_ladder()`

This function consumes the complete bare ordinary-ladder RHS, validates the ordered electron propagator momenta as $E_1:p'-k$, $E_2:p'-k-l$, $E_3:p-k-l$, and $E_4:p-k$, and identifies the two photon denominators $K=-k^2$ and $L=-l^2$. The auxiliary denominator $H=-(k+l)^2$ is introduced with exponent zero, giving the bare family index $J(1,1,0,1,1,1,1)$.

### 30.3 `derive_ladder_scalar_product_rules_from_family()`

The scalar-product basis is regenerated by solving the denominator definitions rather than by returning a hard-coded replacement table. The derived rules are regression-tested against the established ladder basis.

### 30.4 `raw_ladder_q0_numerator()`

This function structurally sets $p'=p$ in the scalarized raw numerator and generates the direct $A_0$-branch Dirac numerator from the original graph.

### 30.5 Current automation boundary

Raw graph parsing, family detection, scalar-product basis derivation, and $q=0$ numerator generation are automatic. Generation of the complete 75-term coefficient table from the raw $D$-dimensional projector trace and a general IBP/Laporta reduction are still not implemented; the supplied CSV remains independently derived validation data.


---

## 31. v0.25.0: arbitrary-length D-dimensional Clifford traces and full A0 regeneration

### 31.1 `dirac_trace_ddim()`

v0.25.0 adds recursive evaluation of arbitrary even-length Clifford words,

$$
\operatorname{Tr}
\left(
\gamma^{\mu_1}\cdots\gamma^{\mu_{2n}}
\right),
$$

with trace normalization

$$
\operatorname{Tr}(1)=4.
$$

Gamma5 is intentionally unsupported.

### 31.2 `contract_fully_scalar_lorentz()`

For fully contracted scalar results, the Lorentz-index network is reduced to scalar products and powers of $D$. For example,

$$
g^{\mu\nu}p_\mu q_\nu
\longrightarrow
p\cdot q,
$$

and a closed metric loop gives

$$
g^\mu{}_{\mu}
\longrightarrow
D.
$$

Free or multiply-used indices are rejected rather than guessed.

### 31.3 `dirac_trace_fully_contracted_sympy()`

Long projector traces can become impractical if every intermediate metric tensor is materialized. The optimized fully-contracted path therefore:

1. expands the numerator into scalar coefficients and Clifford words;
2. combines identical words;
3. caches perfect-pairing patterns;
4. contracts pairings directly to scalar products without creating the full metric expression;
5. returns a SymPy scalar polynomial.

### 31.4 `ladder_a0_projector_trace_sympy()`

Starting from the raw ordinary-ladder input, QEDCalc now evaluates

$$
A_0
=
\operatorname{Tr}
\left[
(\rlap{/}P+m)
N_\mu^{(0)}
(\rlap{/}P+m)
\gamma^\mu
\right]
$$

directly from the bare graph.

### 31.5 `ladder_a0_denominator_polynomial()`

The trace result is converted to the $K,L,H,A,B$ denominator polynomial using the on-shell scalar-product identities.

### 31.6 `ladder_a0_integral_table()`

With bare denominator

$$
KLA^2B^2,
$$

each numerator monomial is converted to the family

$$
J(n_K,n_L,n_H,n_A,n_B).
$$

The raw bare ladder now regenerates exactly

$$
\boxed{
29\text{ distinct scalar integrals}
}
$$

for the $A_0$ branch, matching the independent derivation checkpoint.

The generated coefficient table can be written to

`output/ladder_A0_29_coefficients_generated.csv`.

### 31.7 Demo

Run

`run_ladder_a0_trace_demo.bat`

to generate

`output/ladder_A0_raw_trace_trial.md`.

### 31.8 Current boundary

The $A_0$ 29-integral branch is now regenerated from raw bare LaTeX. The remaining ordinary-ladder gap is the general-$q^2$ Pauli-projector branch that generates the 75-term audit table, followed by a general IBP/Laporta reducer.


## 32. v0.26.0: full regeneration of the general-$q^2$ ordinary-ladder audit table

### 32.1 Faster fully-contracted trace engine

For finite $q$, the number of distinct scalar products grows substantially. v0.26.0 therefore aggregates each Clifford pairing by a canonical key consisting of the power of $D$ and the sorted scalar-product monomial before constructing a SymPy expression. Pairing patterns and word traces are cached.

### 32.2 `ladder_general_q_projector_result()`

```python
ladder_general_q_projector_result(raw, trace_order="archived")
ladder_general_q_projector_result(raw, trace_order="spin_sum")
```

`archived` reproduces the historical projector-first ordering

$$
\operatorname{Tr}\left[(\rlap{/}p'+m)O_\mu(\rlap{/}p+m)\Gamma_{\mathrm L}^{\mu}\right],
$$

which generated the stored 75-term audit CSV. Starting from the raw bare ladder expression, QEDCalc regenerates all 75 integral-family monomials and matches all 75 archived coefficients exactly.

`spin_sum` uses the later audited ordering

$$
\operatorname{Tr}\left[(\rlap{/}p'+m)\Gamma_{\mathrm L}^{\mu}(\rlap{/}p+m)O_\mu\right]
$$

and the corrected finite-$q$ projector coefficients. It is deliberately kept separate from the historical CSV; the current route generates 72 monomials.

### 32.3 Corrected projector coefficients

$$
a(z)=-\frac{2}{z(D-2)(z-4)}
$$

$$
b(z)=-\frac{Dz-2z+4}{z(D-2)(z-4)^2}
$$

### 32.4 Table audit helpers

```python
compare_ladder_integral_tables(generated, reference)
write_ladder_general_q_integral_table_csv(table, path)
```

### 32.5 Demo

```text
run_ladder_general_q_trace_demo.bat
```

Outputs:

```text
output/ladder_general_q_raw_trace_trial.md
output/ladder_general_q_75_coefficients_generated.csv
output/ladder_general_q_corrected_spin_sum_generated.csv
```

### 32.6 Interpretation

Exact regeneration of the 75-term table is a reproducibility/audit result for the historical calculation. Because the later trace-order audit corrected the physical spin-sum ordering, QEDCalc never silently treats that archived 75-term table as the final physical projector. The audited finite-limit $A_0$ and $C_1=B_1-2A_1$ route remains the physical $F_2(0)$ path. v0.27.0 adds the general IBP equation generator and finite sparse Laporta elimination core. Complete seed closure and master-integral reduction remain the next major automation gap.
\n\n## 33. v0.27.0: generic IBP equations and finite Laporta elimination\n\n`qedcalc.operations.ibp` introduces a generic denominator-family representation for integration-by-parts relations. For\n\n$$\nJ(n_1,\ldots,n_N)=\int d^{LD}k\,\prod_aD_a^{-n_a},\n$$\n\nQEDCalc generates\n\n$$\n0=\int d^{LD}k\,\frac{\partial}{\partial k_i^\mu}\left[v^\mu\prod_aD_a^{-n_a}\right].\n$$\n\nScalar products produced by differentiating denominators are reduced back to denominator symbols and external invariants. The ordinary-ladder adapter uses $(K,L,H,E_1,E_2,E_3,E_4)$ and generates the eight canonical IBPs for the bare seed $J(1,1,0,1,1,1,1)$.\n\n`laporta_eliminate()` performs sparse symbolic elimination on a finite equation set. The one-loop tadpole test generates $(D-2)J(1)-2m^2J(2)=0$ and reduces $J(2)=(D-2)J(1)/(2m^2)$ when $J(1)$ is protected. The bare ladder seed produces 31 distinct integrals in eight equations and eight finite pivots.\n\nSector signatures, binary sector IDs, and first-neighbor seed generation are also included. The first ordinary-ladder neighborhood contains 8 seeds and generates 64 IBPs involving 181 distinct integrals. Full closure is not yet attempted automatically; sector ordering, scaleless/zero-sector detection, iterative seed expansion, rational-function coefficient optimization, and master-integral boundary data remain future work.\n\n\n## 31. v0.29.0: ordinary-ladder family symmetry and generic-rank probes\n\nThe seven-denominator ordinary-ladder family now has a four-element symmetry group generated by external exchange and a unit-Jacobian loop reparametrization. Integral indices are canonicalized to the lexicographically smallest member of their symmetry orbit.\n\nThe degree-2 bounded domain drops from 36 seeds to 24 symmetry representatives, while the distinct integrals appearing in the IBP system drop from 623 to 335.\n\nQEDCalc also supports an exact-rational generic-point coefficient specialization for fast rank diagnostics. At $D=37/10$, $z=2/5$, $m^2=1$, the symmetry-reduced degree-2 system yields 162 forward-sparse pivots. This probe is not an arbitrary-kinematics symbolic reduction; it is a fast diagnostic for rank and seed closure.\n

## Addition: exact rational reconstruction (v0.31.0)

QEDCalc can now reconstruct rational functions of $D,z$ from exact-rational generic-point Laporta reductions. Floating-point samples are rejected, and a candidate is accepted only after exact agreement on independent holdout points. The corrected ordinary-ladder route reconstructs representative coefficients for $J(-1,0,0,1,1,1,1)$ and $J(0,0,1,1,0,1,1)$. Full target-wide reconstruction still requires adaptive degree bounds, pole avoidance, and finite-field/modular acceleration.


## v0.34.0: residue-aware closure scheduler

v0.34.0 adds a bounded residue-aware scheduler for the corrected ordinary-ladder Laporta system. Instead of expanding every terminal-residue neighborhood at once, QEDCalc measures which targets each residue blocks, aggregates residues by sector, and ranks sectors by blocked-target impact per new direct seed.

New APIs:

- `residue_impact_profile()`
- `residue_sector_profile()`
- `schedule_residue_sectors()`

For the corrected 84-seed baseline, the highest-impact sectors are sector 96 (22 blocked targets, one new residue seed), sector 82 (18 blocked targets but no new direct seed because its residue is already seeded), and sector 80 (17 blocked targets, one new residue seed).

The phase-1 scheduler inserts terminal residues themselves without inserting their full neighborhoods. Adding 30 new direct residue seeds changes the system from 84 to 114 seeds, 666 to 906 IBP rows, and 598 to 823 pivots, while residue-bearing corrected targets decrease from 28 to 27.

The scheduling score is a priority heuristic, not a claim that every blocked target will immediately close. The next phase will recompute residues on the 114-seed system and expand only the best remaining sector neighborhoods under a strict seed budget.

## v0.34.0 — incremental Laporta and phase-2 scheduler

`reduce_ibp_equation_with_rules()` and `extend_laporta_rules_incrementally()` reuse an existing triangular Laporta reduction and process only the new seed rows. `evaluate_neighborhood_seed_candidates()` checks whether new pivots directly solve known terminal residues; `schedule_neighborhood_seeds()` greedily maximizes marginal blocked-target coverage. In the ordinary-ladder phase-1 system, 7 of 22 tested neighborhood seeds have positive direct impact, and 2 seeds cover a union of 26 blocked targets. This is a scheduler metric, not a claim of full closure.


## v0.35.0 — factorized lower-subtopology classifier

New APIs `denominator_loop_direction()`, `loop_denominator_rank()`, `has_free_scaleless_loop_direction()`, `factorized_one_denominator_per_loop()`, and `factorized_euclidean_scalar_value()` analyze propagator quadratic forms in loop-momentum space. If an L-loop sector contains exactly L independent rank-one positive denominators and no numerator slots, an invertible linear loop transformation separates the sector into one one-loop factor per loop. In the ordinary ladder, `(0,0,0,0,0,1,1)`, `(0,0,0,0,1,0,1)`, and `(0,0,0,0,2,0,3)` satisfy this test with determinant -1 and are therefore one-loop massive-tadpole products, not new genuine two-loop masters.

After actually adding the two phase-2 seeds, full recursion still leaves 27 blocked targets. Once these three descended lower sectors are classified as known factorized subtopologies, only 18 targets remain residue-bearing and only three terminal residue kinds remain. The extended zero-sector diagnostic additionally detects a denominator-free loop direction, e.g. `(0,0,0,0,0,0,2)`. The main Laporta pruning path intentionally keeps the older conservative criterion for performance/backward reproducibility; the extended test is opt-in for scheduler/lower-sector diagnostics.

## 36. v0.36.0: Local master-candidate diagnostics for the final three residues

After factorized lower subtopologies are removed, three terminal residue types remain. `diagnose_first_neighbor_irreducibility()` generates every new canonical first-neighbor seed, reduces its IBP rows incrementally through the existing triangular system, and checks whether the terminal residue itself becomes a new pivot.

For the ordinary ladder each of the three residues has seven new canonical first-neighbor seeds and zero pivoting seeds. They may therefore be carried as **provisional local master candidates**, expanding the corrected non-factorized candidate basis from six to nine. Together with the known factorized lower sectors, this exhausts the terminal non-basis residues of the 40 corrected canonical targets.

This is a bounded local IBP diagnostic, not a proof of global master-integral status. A wider seed domain or an independent reduction/master-count argument is still required for a definitive statement.
\n\n## 37. v0.37.0: Directional depth-2 and multi-probe master-candidate audit\n\n### 37.1 `directional_depth2_seeds()`\n\nInstead of opening the full Cartesian degree-2 Laporta domain, this bounded audit moves one admissible family index two steps in the same direction. Positive denominator powers receive $+2$ and non-positive numerator slots receive $-2$, followed by symmetry canonicalization and existing-seed removal.\n\n### 37.2 `diagnose_directional_depth2_irreducibility()`\n\nEach directional depth-2 seed contributes only its own IBP rows. Those rows are reduced incrementally through an existing triangular rule set and QEDCalc records whether the terminal residue itself becomes a new pivot. This remains a bounded diagnostic, not a proof of global irreducibility.\n\n### 37.3 `build_specialized_laporta_rules()`\n\nRebuilds the same canonical seed domain independently at an exact-rational probe. This is used to audit accidental rank loss at a special kinematic point.\n\n### 37.4 Ordinary-ladder result\n\nAll three remaining candidates have zero pivoting first-neighbor seeds. Their directional depth-2 audits also yield zero pivoting seeds at three independent exact-rational probes, and each rebuilt baseline has 837 pivots. QEDCalc therefore labels them **depth-2-stable provisional master candidates**. The full Cartesian degree-2 domain and an independent external reduction remain future validation work.\n\nDemo: `run_phase5_depth2_master_demo.bat`\n

## 38. v0.38.0: Full degree-2 Cartesian master-candidate audit

### 38.1 `mixed_degree2_seeds()`

Returns only the mixed two-direction part of `bounded_seed_domain(..., max_extra_degree=2)` after removing the center, first neighbors, same-direction depth-2 seeds, existing seeds, and applying symmetry canonicalization.

### 38.2 `diagnose_mixed_degree2_irreducibility()`

Each mixed seed contributes only its own IBP rows, which are reduced incrementally through the existing triangular Laporta rules. At the ordinary-ladder primary probe, all three candidates have zero mixed pivoting seeds.

Relative to the 116-seed phase-2 baseline, the three candidates have 32, 19, and 33 new full degree-2 seeds, including 18, 10, and 21 mixed seeds. Combined with the already-audited first-neighbor and directional depth-2 classes, this exhausts the complete bounded degree-2 Cartesian neighborhood at the primary probe.

### 38.3 Portable Laporta checkpoints

`write_laporta_rule_checkpoint()` and `read_laporta_rule_checkpoint()` store ReductionRule sets in JSON. The 837-pivot exact-rational primary-probe system can therefore be reused without rebuilding or depending on Python pickle files.

This remains a bounded audit, not a global proof of master-integral status.

Run: `run_phase6_full_degree2_master_demo.bat`


## 39. v0.39.0: Three-probe full degree-2 audit

The complete bounded degree-2 Cartesian audit is repeated at three independent exact-rational probes. All three independently rebuilt phase-2 baselines contain 837 pivots. For the three provisional ordinary-ladder candidates, the mixed degree-2 domains contain 18, 10, and 21 canonical seeds respectively; none makes its candidate a pivot at probe 2 or probe 3. Combined with the already completed three-probe first-neighbor and directional depth-2 audits, all three candidates are non-pivoting throughout the complete bounded degree-2 Cartesian domain at all three probes. This is strong bounded evidence but not a global master-integral proof.

`build_integral_reducer()` now supplies a persistent recursive reduction cache shared across all rows in one incremental Laporta extension, avoiding repeated expansion through the same 837-rule baseline.

Run: `run_phase7_three_probe_full_degree2_demo.bat`


## v0.40.0: three-probe full bounded degree-3 audit

For the three provisional ordinary-ladder master candidates, QEDCalc now generates the new bounded degree-3 shell after removing the already-audited degree <= 2 domain, canonicalizes it by family symmetry, and appends it to the existing Laporta system sector by sector.

The new APIs are `degree3_shell_seeds()` and `diagnose_full_degree3_irreducibility()`. The three independent exact-rational probes all retain the same 837-pivot baseline. The new degree-3 shells contain 72/84/84 seeds for candidates 1/2/3, and the candidate itself remains non-pivot in all nine probe/candidate combinations.

This is strong bounded evidence for the three provisional master candidates, but it is not a global proof of the master count.


## 41. v0.41.0: complete corrected ordinary-ladder symbolic reduction

### 41.1 Closure from 40 targets to 12 basis integrals

The 40 symmetry-canonical targets from the corrected general-$q^2$ spin-sum route terminate on the same 12 integrals at all three independent exact-rational 837-pivot checkpoints. The terminal set consists of nine non-factorized provisional basis candidates plus three factorized lower subtopologies.

### 41.2 Analytic reconstruction of all 151 nonzero coefficients

Of the $40\times12=480$ matrix entries, 151 are nonzero. Each coefficient $c_{ia}(D,z)$ is reconstructed as an exact rational function from a 91-point Cartesian grid and then checked at three independent probes outside that grid:

$$
(D,z)=\left(\frac{37}{10},\frac25\right),\quad\left(\frac{41}{11},\frac37\right),\quad\left(\frac{29}{8},-\frac13\right).
$$

Thus every nonzero coefficient has 94 exact validation points. Grid-only fits that fail an independent probe are rejected.

The complete matrix is stored in `data/ladder_corrected_40target_12basis_symbolic_reduction.csv`; the 151 nonzero entries are also written to `output/ladder_corrected_40target_symbolic_nonzero.csv`.

### 41.3 Denominator-guided reconstruction

`infer_allowed_univariate_denominator()` infers an exact denominator from one-dimensional slices while allowing only known IBP singular factors. `reconstruct_bivariate_with_known_denominator()` fixes the denominator $Q(D,z)$ and reconstructs only the numerator polynomial on a Cartesian tensor grid, followed by exact grid and holdout validation.

For the hardest coefficient in the reduction of $J(-2,1,1,1,0,1,1)$, the structured denominator contains

$$
4(D-4)(D-3)(D-2)(2D-7)(3D-8)(z-4),
$$

and the reconstructed expression passes all 91 grid points and all three independent probes.

Run `run_phase9_full_symbolic_reduction_demo.bat`.

This completes the ordinary-ladder IBP coefficient reduction. Analytic evaluation of the 12 basis integrals themselves, and reuse of the same raw-to-IBP path for crossed ladder and corner graphs, remain subsequent tasks.


## 42. v0.42.0: Ordinary-ladder 12-basis evaluation layer

### 42.1 Projective representations for all 12 basis integrals

`scalar_feynman_parametric_representation()` constructs the convention-free Euclidean projective representation

$$
I=\pi^{LD/2}\frac{\Gamma(\nu-LD/2)}{\prod_i\Gamma(n_i)}\int_{\sum x_i=1}\!\left(\prod_i x_i^{n_i-1}\right)\frac{U^{\nu-(L+1)D/2}}{F^{\nu-LD/2}}
$$

directly from the quadratic denominator family. For the ordinary ladder it derives $U=\det A$, $\Delta=B^T A^{-1}B$, and $F=U\Delta$. Regression tests verify degree-2 homogeneity of $U$ and degree-3 homogeneity of $F$ for all 12 basis integrals.

### 42.2 Generic-z factorized lower sectors

Basis 0, 1, and 3 are already products of one-loop massive tadpoles at generic $z$. Their exact Gamma-function values are produced through the lower-subtopology classifier and `massive_tadpole_euclidean()`.

### 42.3 Nine exact z=0 basis values

At $z=0$, $p'=p$, so $E_1=E_4$ and $E_2=E_3$. Basis 2 reduces to $T_2T_1$ and basis 4 to $T_2^2$. Basis 5 and 6 become one-massless/two-equal-mass vacuum sunsets and are evaluated in Gamma functions by `one_massless_two_massive_vacuum_euclidean()`. Basis 7 and 9 are evaluated by integrating a massless bubble first and then a generalized on-shell one-loop electron integral with `massless_bubble_on_shell_electron_euclidean()`.

The exact analytic basis indices are

$$
0,1,2,3,4,5,6,7,9,
$$

leaving only basis 8, 10, and 11 as genuine unresolved two-loop $z=0$ masters.

### 42.4 Convention boundary

The returned values are convention-free Euclidean scalar integrals. Minkowski $i$ factors, Wick-rotation signs, $(2\pi)^D$ measures, $\mu^{2\epsilon}$, and $S_\epsilon$ remain the responsibility of the convention/dimreg layer.

Run: `run_phase10_basis_evaluation_demo.bat`


## 43. v0.45.0: complete analytic evaluation of all 12 $z=0$ terminal basis integrals

At $z=0$, $E_1=E_4$ and $E_3=E_2$. The former basis integrals 8, 10, and 11 therefore form

$$
T_n=\int\frac{d^Dk\,d^Dl}{L\,H\,E_2\,E_4^n},\qquad n=1,2,3.
$$

`ordinary_ladder_z0_reduced_ibp_family()` builds the reduced five-denominator family and `ordinary_ladder_z0_T_ibp_reductions()` regenerates symbolic reductions of $T_2,T_3$ to $T_1$ plus lower sectors. The remaining lower sectors are either scaleless or Gamma-function products.

`ordinary_ladder_T1_z0_euclidean()` evaluates $T_1$ by Cheng--Wu gauge fixing, one-variable hypergeometric reduction, and Gauss summation. Consequently `ordinary_ladder_basis_z0_evaluations()` returns exact analytic values for all twelve basis integrals.


## 44. v0.44.0: projector/reduction assembly and z-pole audit

`qedcalc.operations.ladder_assembly` canonicalizes the corrected 72 terms to 40 symmetry targets and composes them with the v0.41 40 x 12 symbolic reduction. `ladder_basis_z_pole_residues()` and `ladder_basis_z_double_pole_coefficients()` audit the z -> 0 poles, while `ladder_projector_leading_z_pole_cancellation()` verifies cancellation of the complete `1/z` coefficient using the exact v0.43 z=0 basis values. The v0.41 reduction matrix uses the normalization `m^2=1`. Only basis 0,1,3,5,6,7,8 need first z derivatives for the finite term.

## 44. v0.45.0: crossed-ladder symmetry and raw-to-parametric bridge

The crossed seven-slot family uses `(K,L,H,E1,E2,E3,E4)`, with `H=-(k+l)^2` auxiliary. Simultaneous external exchange `p<->p'` and loop exchange `k<->l` gives the exact denominator permutation `K<->L`, `E1<->E4`, `E2<->E3`, with `H` fixed. Canonicalization reduces the 95 corrected projector targets to 52 representatives.

At the exact probe `(D,z,m2)=(37/10,2/5,1)`, the symmetry-reduced target seed system contains 416 IBP rows and 378 pivots; 40 of 52 canonical projector targets pivot. The remaining 12 do not pivot from any canonical first-neighbor seed in the bounded audit, so the next step is a degree-2 or z=0-specialized reduction rather than uncontrolled seed expansion.

`crossed_bare_scalar_parametric_representation()` independently generates the standard six-denominator crossed scalar Symanzik representation from `K,L,E1,E2,E3,E4`. The generated `U` and `F` are homogeneous of degrees 2 and 3. This closes the denominator-level bridge from the raw crossed family to projective integration. The projected numerator-to-projective-kernel bridge remains a separate unfinished layer.

## 45. v0.47.0: crossed-ladder q-linear projector bridge

`crossed_raw_numerator_q_expansion()` introduces `p'=p+q` into the complete parsed crossed-ladder numerator and truncates the distributed noncommutative expression at first order.  The result contains 144 zeroth-order and 84 first-order chains.

`crossed_q0_five_denominator_family()` and `crossed_q0_parametric_bridge()` implement the q=0 scalar family with denominator powers `(1,1,1,2,1)`.  With parameters `(u,v,x,y,z)` for `(K,L,Dk,Dkl,Dl)`, the generic Symanzik construction returns the independent checks

$$
U=(x+y+u)(y+z+v)-y^2=\Delta,
$$

$$
F=(y+z+v)(x+y)^2-2y(x+y)(y+z)+(x+y+u)(y+z)^2=W,
$$

and the parameter numerator monomial is `y`.

`crossed_denominator_q1_correction()` returns

$$
\delta\mathcal D=2x\,k\cdot q+y(k+l)\cdot q.
$$

`crossed_breit_projector_check()` uses explicit 4x4 Dirac matrices and Breit-frame spinors to verify the projector normalization: the F1 coefficient is zero and the F2 coefficient is one.

## 46. v0.50.0: crossed-ladder U/tq/raw-kernel/Hermite bridge

After the generated V partial fractions, QEDCalc now uses `h=S(R+U)-1`. The original domain `S>=1` gives `0<=U<=h-R+1`. With `Y=R+U`, every remaining U integrand is polynomial in Y divided by a monomial power of Y, so the U integral is done by exact monomial primitives rather than a generic CAS integral.

The subsequent map `h=(1-t)/t`, `R=q/t` has Jacobian `1/t^3` and gives the triangle `0<t<q<1`. The logarithm becomes `(q^2+(1-2q)t)/(q^2(1-t))`.

The t integral is then regenerated with a lower cutoff kept until the rational and logarithmic sectors are combined. The coefficient of `log(epsilon)` cancels exactly. The raw one-variable kernel closes on `1,L,M,L^2,LM,D(q)`.

`crossed_automatic_hermite_reduction()` applies rational Horowitz-Ostrogradsky reduction hierarchically while accounting for derivatives of `L`, `M`, and `D(q)`. It reconstructs the complete `R,T,U,V,P,Q,Z` total-derivative primitive and the simple-pole canonical kernel without loading those coefficients from a stored table. Both agree exactly with the independently audited crossed-ladder derivation.

Run `run_phase23_crossed_u_tq_bridge_demo.bat`, `run_phase24_crossed_raw_q_kernel_demo.bat`, and `run_phase25_crossed_automatic_hermite_demo.bat`.

## 51. v0.51.0: independent analytic evaluation of the crossed canonical kernel

The crossed-ladder final analytic evaluation no longer inserts the three `q=1/2` standard-integral values or the endpoint finite constant as final data. `crossed_standard_integrals_derived()` constructs the half-sector values from odd-part zeta sums and alternating Euler sums. `crossed_endpoint_canonical_integral_derived()` extracts the coefficients of the endpoint-safe canonical kernel automatically and integrates the basis `L^2/q`, `LM/q`, `M^2/q`, `L/q`, `M/q`, and `1/q` with a symbolic cutoff.

`crossed_endpoint_asymptotics_derived()` starts from the automatically reconstructed Hermite primitive. The `q->1` expansion of `D(q)` is generated by integrating the exact derivative relation with `D(1)=0`; the `q->0` side uses the dilogarithm inversion asymptotic. The canonical cutoff logarithms and boundary cutoff logarithms cancel exactly, leaving the finite boundary term.

The final coefficient is assembled by `crossed_final_result()` from these regenerated pieces. `crossed_expected_result()` is retained only as a regression checkpoint after the independent assembly.

Run `run_phase26_crossed_independent_analytic_demo.bat`.

## 52. v0.52.0: vacuum-polarization raw-to-final and self-energy analytic downstream

### 52.1 Vacuum polarization

The raw closed electron trace is shifted and D-dimensionally tensor-reduced. A scalar loop IBP identity converts the metric coefficient to the exact transverse form proportional to `(k^2 g^{alpha beta}-k^alpha k^beta)`. On-shell subtraction is performed before taking `D->4`, producing the finite logarithmic scalar vacuum-polarization integrand directly from a dimensional difference.

The outer magnetic kernel then generates the finite two-parameter g-2 representation. The z integral is derived from the elementary beta substitution, the x primitive is assembled from rational and logarithmic Laurent monomials, and both endpoints are generated analytically. The final coefficient is `119/36-pi^2/3`; the stored checkpoint is used only for regression comparison.

Run `run_phase27_vacuum_polarization_raw_to_final.bat`.

### 52.2 Self-energy insertion

Starting from the already generated finite four-parameter kernel `G_A`, v0.52 regenerates the b integral by the linear denominator variable `Y=ab+q^2 z(1-a)`. The z stage uses the two elementary integrals `I0(c)` and `I1(c)`, and the q stage reconstructs the audited one-variable kernel without reading it as an input.

The final a integration is assembled from general power-log identities, zeta(2) sums and the endpoint-safe telescoping pair. The finite sector is `-1/24-pi^2/18`. Independently, the factorized IR branch gives `A^(1)->1/2`, `J(rho)=-log(rho)-1/2+o(1)`, hence `A_B=log(rho)+1/2+o(1)` and the total pair coefficient `log(rho)+11/24-pi^2/18+o(1)`.

Run `run_phase28_self_energy_analytic_downstream.bat`.

The remaining self-energy raw-to-final gap is the mechanical magnetic-projector/tensor-reduction bridge from the two raw diagrams to `G_A`.


## v0.55.0 progress note

Self-energy insertion is now closed from the raw two diagrams through on-shell renormalization to the final analytic result. Corner (IIc) now has a raw two-diagram parser/topology bridge, q=0 five-parameter denominator family, split-parameter q derivatives, and explicit q-linear magnetic projector generation. The next corner stage is the Gaussian/subtraction bridge to the existing UV-finite parameter representation.


## v0.56.0 corner raw Gaussian / UV bridge

`corner_gaussian_bare_templates()` streams the v0.55 raw magnetic-projector monomials through square completion, odd-moment removal, rank-2/rank-4 tensor reduction, and the two-loop radial master integrals to generate compact `G4` and `G5` templates. `corner_uv_residue_sample()` audits the bare UV residue at exact-rational chart points, while `corner_local_uv_subtractions()` and `corner_uv_subtracted_residue_sample()` verify exact cancellation of the logarithmic UV residue by a local `B gamma_rho` representative. The local subtraction is a boundary audit device, not a replacement for the physical UV-finite representation.


## v0.57.0 corner renormalized-inner-vertex sector bridge

The Eq. (32)-type on-shell-renormalized inner vertex is now a distinct three-sector object. The z sector is integrated exactly to a logarithm and the corrected kappa-squared sector is reduced to a simple denominator difference. This layer is intentionally distinct from the local five-simplex UV subtraction.

### Phase 44: evanescent local term and on-shell subtraction

The D-dimensional local finite term generated in Phase 43 is proportional to `gamma_nu`. Because the on-shell constant `B` is defined from that same local gamma channel, the identical contribution occurs in both the bare vertex and `B gamma_nu`. QEDCalc verifies exact cancellation before outer integration and again after the outer Breit projector.


## v0.67.0: independent regeneration of the historical corner $K_\nu$ full-chain projector

Phase 49 rebuilds the independently preserved on-shell $K_\nu$ operator in the current explicit 4x4 gamma convention. It does not load a stored $Q_K$ or a final finite parameter kernel. The transcribed full operator after the right external Dirac equation is

$$
K_\nu
=
K_\nu^{\mathrm{pres}}
+(1-u)(1-uv)D(k)\gamma_\nu
+2k^2[1-u+u^2v(1-v)]\gamma_\nu.
$$

The audit uses the already documented convention map $i\gamma_{KK}\cdot a\leftrightarrow-\rlap{/}a$ and current $\sigma_{\mu\nu}=i[\gamma_\mu,\gamma_\nu]/2$.

`corner_historical_K_projector_audit()` regenerates the full magnetic projector including the $q$ derivative of the first outer electron denominator. Polynomial division then gives the exact identity

$$
P_K=D(k)Q_K+R_{\mathrm{odd}}.
$$

The remainder factorizes as

$$
R_{\mathrm{odd}}=k_1k_2\,\mathcal R(k_0,k_1^2,k_2^2,k_3^2;u,v),
$$

which vanishes under the shifted symmetric outer integration because the spatial transverse components are unshifted. Generated term counts are `21/14/21/4` for base/transverse/$Q_K$/remainder.

The Phase-49 historical `Q_K` remains deliberately distinct from `corner_physical_common_quotients().lp_quotient`, which is generated from the raw $C_\nu$ representation. No denominator-power or sign patch is applied merely to force these objects to agree. The next audit must establish their operator-level correspondence sector by sector.

Run `run_phase49_corner_historical_K_projector_audit.bat`.


## 68. v0.68.0 Phase 50: convention-resolved historical $K_\nu$

Phase 49 is retained as a structural audit of $P_K=DQ_K+R_{\rm odd}$. Phase 50 resolves the full Karplus--Kroll/current convention by decomposing the preserved historical operator into seven tensor structures and solving their coefficients against the independently generated raw-$C_\nu$ magnetic projector.

The canonical coefficient tuple is

$$
\boxed{(-1,\ 1,\ 0,\ -1,\ i,\ 1,\ -\tfrac12)}.
$$

The third basis vector is exactly projector-null. The resolved projector agrees identically with

$$
K_\nu^{\rm current}=\frac12C_\nu-2f(u)\gamma_\nu
$$

at base, transverse, and common-numerator levels.

APIs:

- `corner_K_convention_resolved_audit()`
- `corner_phase50_K_convention_resolved_audit()`

## 69. v0.68.0 Phase 51: rational-remainder regrouping

Phase 51 verifies

$$
\frac{C_\nu}{2\Lambda'^2}-\frac{2f\gamma_\nu}{\Lambda_0^2}=\frac{K_\nu^{\rm current}}{\Lambda'^2}+2f\gamma_\nu\left(\frac1{\Lambda'^2}-\frac1{\Lambda_0^2}\right)
$$

for all four inner Lorentz components, then checks the same regrouping after common-denominator division and the linear Gaussian map. All residuals vanish exactly. Therefore the remaining corner finite-part discrepancy is no longer assigned to the rational LP/$K$ operator or Gaussian regrouping.

APIs:

- `corner_rational_regrouping_audit()`
- `corner_phase51_rational_regrouping_audit()`


## 70. v0.69.0 Phase 52: direct unsplit reconstruction of the log sector

### 70.1 Starting identity

The logarithmic sector is regenerated directly from

$$
\ln\frac{\Lambda'^2}{\Lambda_0^2}=(\Lambda'^2-\Lambda_0^2)\int_0^1\frac{dz}{\Lambda_0^2+z(\Lambda'^2-\Lambda_0^2)}
$$

rather than from already split rational families.  The raw inner bridge generates

$$
\Lambda'^2-\Lambda_0^2=u^2v(1-v)k^2+uv(1-u)D(k).
$$

### 70.2 Family before denominator cancellation

Writing the outer photon denominator as $P$, the outer electron denominator as $E$, and the interpolated inner denominator as $L_z$, the unsplit scalar family is

$$
\frac{[A_Kk^2+A_DD(k)]Q_{\log}(k)}{P E^2L_z}.
$$

Phase 52 Feynman-parameterizes this four-factor family directly and sends it to the $n=4$ Gaussian master.

APIs:

```python
corner_log_unsplit_audit()
corner_phase52_log_unsplit_audit()
```

### 70.3 Exact audit

The generated coefficients are

$$
A_K=u^2v(1-v)
$$

and

$$
A_D=uv(1-u).
$$

The original scalar identity relating the unsplit family to the three v0.66 split families has exact zero residual, and the direct Gaussian template is free of $\Gamma(0)$ poles.

### 70.4 Numerical cross-check status

Auxiliary uniform scrambled-Sobol runs at $\rho=0.05$ place both direct and split log-sector integrals near $0.32$.  Because the soft-endpoint variance is still significant, those values are diagnostic rather than regression targets.  Phase 53 will apply the same soft-importance map to both routes and test their numerical equality within statistical uncertainty.


## 71. v0.69.0 Phase 53: soft-importance map and compact numerical route

Phase 53 implements a bijection adapted to $u=O(\rho)$ and $a_d,a_p=O(u)$ while retaining complete domain coverage:

$$
u=\rho[\exp(Lt)-1],\qquad L=\ln\frac{1+\rho}{\rho}
$$

$$
r=\frac{ux}{1-x},\qquad s=\frac{uy}{1-y}
$$

$$
a_d=\frac{r}{1+r+s},\qquad a_p=\frac{s}{1+r+s},\qquad a_l=\frac{1}{1+r+s}.
$$

APIs:

```python
corner_soft_importance_audit()
corner_phase53_soft_importance_audit()
```

The endpoint values, simplex and line-map sums, and Jacobians are checked exactly.  Numerical diagnostics evaluate the compact Gaussian templates directly instead of the expanded rational kernels.  This removes catastrophic endpoint cancellation.  Scrambled-Sobol checks for $\rho=0.1,0.05,0.02$ show agreement of the direct and split log routes within estimated statistical uncertainty.

## 72. v0.69.0 Phase 54: independent finite normalization of $B$

Expanding the normalized $k^2$ radial master in $D=4-2\epsilon$ produces the finite term

$$
J_{k^2,\mathrm{fin}}=-\ln L-\frac12.
$$

Together with the scalar master, the finite $B$ integrand is

$$
u\left[-\ln L-\frac12-\frac{2f(u)}{L}\right]
$$

with

$$
L=u^2+\rho^2(1-u),\qquad f(u)=1-u-\frac12u^2.
$$

Polynomial division of $u f(u)/L$ gives the hard constant $-5/4$.  Combining it with

$$
I_{\log}=-\int_0^1u\ln(u^2)\,du=\frac12
$$

and the explicit $-1/2$ term gives

$$
\boxed{B_{\rm fin}(\rho)=2\ln\rho+\frac{11}{4}+o(1)}.
$$

Since $A^{(1)}(0)=1/2$,

$$
\boxed{-B_{\rm fin}A^{(1)}\supset-\frac{11}{8}}.
$$

APIs:

```python
corner_B_finite_normalization_audit()
corner_phase54_B_finite_normalization_audit()
```

The $-11/8$ constant is generated from the one-loop subtraction and is not fitted to the final corner result.  It must not be inserted by hand; the next step audits whether the current Eq. (32) route already owns this finite normalization.


## Phase 55: local finite-normalization ownership

The finite local pieces of the one-loop $B$ coefficient are tracked separately in the bare on-shell charge channel and the $B\gamma_\nu$ subtraction channel.  At fixed $u$ the local coefficient is

$$
C_{\rm local}(u,\rho)= -\ln L_0-\frac12-\frac{2f(u)}{L_0}
$$

with

$$
L_0=u^2+\rho^2(1-u).
$$

The logarithmic, radial $-1/2$, and rational pieces cancel independently between the bare and subtraction channels. Hence

$$
\boxed{C_{\rm local}^{\rm ren}=0}.
$$

The phase-54 counterterm-side constant $-11/8$ therefore is not an extra term to append to the already on-shell-renormalized inner remainder. The current temporal charge matrix element and the outer base/transverse projector residuals are also exactly zero.

API:

```python
corner_local_finite_ownership_audit()
corner_phase55_local_finite_ownership_audit()
```

## Phase 56: sequential normalization and measure ownership

The Eq. (42) quarter factor is rederived from the current Feynman-rule factors. One sequential side carries

$$
C_{\rm one}=\frac{e^2}{(2\pi)^4}\frac{\alpha}{2\pi}
$$

and therefore

$$
\boxed{C_{\rm one}=\frac{\alpha^2}{8\pi^4}}.
$$

Including the mirror side gives

$$
\boxed{C_{\rm pair}=\frac{\alpha^2}{4\pi^4}},
$$

which matches the amputated Eq. (42) prefactor exactly. Removing the common outer-loop $\pi^2$ leaves

$$
C_{\rm phys}=\frac14\left(\frac{\alpha}{\pi}\right)^2.
$$

The inner and outer Feynman-gauge photon numerator signs are both $-1$, so the complete corner pair carries their product $+1$.

The physical parameter kernels do not include the external $u\,du$ measure. The required measures are now exposed explicitly by the audit API.

```python
corner_sequential_normalization_ownership_audit()
corner_phase56_sequential_normalization_ownership_audit()
```

After phases 55--56, local finite normalization, mirror ownership, and the overall quarter normalization are excluded as sources of the finite-part discrepancy. The next target is the non-uniform soft-region overlap and full-corner QMC convergence.

## Phase 57: exact large-r overlap audit

QEDCalc regenerates the stored `a_d=u*r` joint soft sector and proves

$$
\boxed{\lim_{r\to\infty} r\left(\mathcal K_K+\mathcal K_{\kappa^2}\right) = \frac{8v}{(1-a_l)^2}}.
$$

The smooth profile

$$
\mathcal O(r) = \frac{8v}{(1-a_l)^2}\frac{r}{1+r^2}
$$

is an add-subtract numerical device only.  The subtracted kernel has zero $1/r$ coefficient.

## Phase 58: simplex cutoff ownership

The exact simplex endpoint is

$$
r_{\max} = \frac{1-a_l}{u}.
$$

Integrating the same overlap profile to this endpoint reproduces the exact $\ln(1/u)$ coefficient $8v/(1-a_l)^2$.  Any profile-dependent finite remainder is matching bookkeeping, not a standalone physical contribution.

## Phase 59: overlap add-subtract on the identical simplex cutoff

Use the exact Phase-58 domain with

$$
a_d=ur,
\qquad
a_p=1-a_l-ur,
\qquad
r_{\max}=\frac{1-a_l}{u}.
$$

QEDCalc keeps the identity

$$
\mathcal K_{\rm joint}=\left(\mathcal K_{\rm joint}-\mathcal O\right)+\mathcal O
$$

on the same domain.  The pointwise recombination residual, analytic add-back residual, and the subtracted $1/r$ coefficient are all exactly zero.  The add-back is a numerical stabilization identity, not an extra physical correction.

## Phase 60: normalized measure-included joint soft density

Under

$$
u=\rho U,
\qquad
a_d=uR,
\qquad
a_p=uS,
\qquad
a_l=1-u(R+S),
$$

the leading measure-included soft density factorizes as

$$
\mathcal S(U,R,S,v)=\frac{U}{1+U^2}G(R,S,v),
$$

with

$$
G(R,S,v)=\frac{2RSv(4R+S+4v)}{(R+v)^2(R+S+v)^4}.
$$

QEDCalc derives

$$
\int_0^\infty dS\,G=\frac{2Rv}{(R+v)^3},
$$

and

$$
\boxed{
\int_0^\infty dR
\int_0^\infty dS\,G=1
}.
$$

Therefore the universal IR logarithm belongs to the joint measure-included soft density, not to any single sequential family.


## 79. Phase 61: finite-triangle joint-soft ownership

The Phase-60 spatial density is integrated on the actual triangle $R+S\leq T$. QEDCalc closes the $R=qx$, $S=q(1-x)$ angular integral and the subsequent $q$ integral analytically. The omitted tail obeys

$$
1-N(T,v)=\frac{2v\ln T+v(1-2\ln v)}{T}+o(T^{-1}),
$$

so the physical cutoff $T=1/(\rho U)$ produces only an $O(\rho\ln(1/\rho))$ correction.

## 80. Phase 62: Eq. (28) shift ownership

The raw QEDCalc routing produces the $p''$ coefficient $-u(1-v)$, whereas the printed historical Eq. (28) uses $-v(1-u)$. Their difference is exactly $v-u$. The stored hard-primary checkpoint belongs to the printed route and the stored shift correction converts it to the shift-consistent hard result. No such correction is appended to a finite-$\rho$ raw kernel that already uses the shift-consistent routing.


## v0.74.0: Phase 63 pure finite-rho matching ownership

Phase 63 separates the exact analytic matching condition from archived numerical checkpoints.  The shift-consistent hard sector and the analytic z sector obey

$$
M_{\mathrm{match}}^{\mathrm{analytic}} = A_{\mathrm C,fin}-H_{K\kappa}^{\mathrm{shift}}-A_z =0.
$$

Hence no additional finite matching constant is allowed.  `corner_pure_matching_audit()` keeps the historical corrected finite-rho QMC values only as regression checkpoints and never feeds them into symbolic construction.  At the smallest archived point,

$$
\rho=0.002,
\qquad
M_{\mathrm{match}}(\rho)=-0.0034390586\ldots,
$$

with archived uncertainty $0.00638$, consistent with the exact zero-matching condition.  The next target is independent regeneration of $I_K$, $I_{\kappa^2}$ and $I_z$ followed by pointwise comparison with the current raw-generated kernels.



## v0.75.0: Phase 64 finite-rho numerical ownership API

Phase 64 adds a reproducible numerical layer without changing the symbolic corner derivation.

APIs:

```python
corner_finite_rho_numerical_measure_audit()
corner_phase64_finite_rho_measure_audit()
corner_finite_rho_qmc(rho_value, power=12, seed=1)
```

The measure audit derives its maps from the Phase-53 symbolic bijection. The physical $u$ measure is

$$
d\mu_u=u\frac{du}{dt}\,dt.
$$

For a two-simplex family the numerical weight is

$$
d\mu_{\Delta_2}=u\frac{du}{dt}J_{\Delta_2}\,dt\,dx\,dy,
$$

while a one-simplex family uses

$$
d\mu_{\Delta_1}=u\frac{du}{dt}J_{\Delta_1}\,dt\,dx.
$$

The assembled coefficient is obtained with

$$
A_{\mathrm C}(\rho)=\frac14\sum_f I_f(\rho).
$$

The optional QMC path requires NumPy and SciPy at runtime but they are not mandatory package dependencies. It reports each family before the quarter normalization, a standard-error estimate, the finite-sample fraction, the assembled $A_{\mathrm C}$, and $A_{\mathrm C}-\ln(1/\rho)$.

This API deliberately contains no Petermann value and no archived corrected QMC number in the integrand construction. Its purpose is to make the current generated-kernel mismatch reproducible before changing any symbolic sign or finite term.

### Phase-64 diagnostic consequence

At $\rho=0.05$ the formal evaluator again places the dominant positive contribution in the rational LP and $B_\gamma$ families; the log families are much smaller. Therefore the remaining reconciliation work should start at the transition

$$
\text{raw radial inner vertex}\longrightarrow\text{physical on-shell rational remainder},
$$

where the code currently contains a sign change of the nonlocal $C_\nu/(2\Lambda'^2)$ term. No sign flip is applied in v0.75.0; the discrepancy is only isolated and made reproducible.


## v0.76.0: corner rational sign resolution and secondary-overlap QMC

Phase 65 independently fixes the relative sign of the raw inner radial master. In the raw-chain convention used by QEDCalc,

$$
\frac{1}{i\pi^2}\int\frac{d^4r}{(r^2-L+i0)^3}=-\frac{1}{2L}.
$$

Hence the raw radial bridge generates $+\gamma_\nu\log(\Lambda'^2/\Lambda_0^2)$ together with $-C_\nu/(2\Lambda'^2)$.

Phase 66 resolves the physical on-shell sign of $C_\nu$ from the charge condition. At $k=0$,

$$
\frac{C_0(0)}{2\Lambda_0^2}=\frac{2f(u)}{\Lambda_0^2}\gamma_0,
$$

while the on-shell $B\gamma_0$ subtraction contributes $-2f(u)\gamma_0/\Lambda_0^2$. Only the $+C_\nu/(2\Lambda'^2)$ physical candidate cancels exactly. Therefore the raw-radial minus sign must not be copied directly into the physical kernel.

Phase 67 embeds the $B_\gamma$ line family exactly into the LP two-simplex and samples the secondary $a_d=ur$ overlap logarithmically in $r$. The measure and Jacobian identities are exact, but the overlap-aware QMC still does not approach the corrected rational hard value. The remaining order-one mismatch is therefore algebraic rather than a numerical tail-sampling problem.

The next audit compares the historical full-$K_\nu$ projector polynomial $Q_K$ from Phase 49 directly against the current `lp_quotient` and factorizes their difference.


## v0.77.0: corner historical-K denominator-cancellation audit

Phase 68 separates the historical $K_\nu$ operator into $K_\nu^{\mathrm{pres}}$, the explicit $D(k)\gamma_\nu$ sector, and the explicit $k^2\gamma_\nu$ sector, and projects each sector independently through the full magnetic chain. Exact SymPy polynomial division proves that both the base and transverse pieces of the $D(k)\gamma_\nu$ sector retain a factor $D(k)$, while both pieces of the $k^2\gamma_\nu$ sector retain a factor $k^2$.

Phase 69 therefore performs the denominator cancellations before the final Gaussian family assignment. The preserving sector remains $(K^1D^2\Lambda'^1)$ with total power $n=4$, the $D$-cancel sector becomes $(K^1D^1\Lambda'^1)$ with $n=3$, and the $k^2$-cancel sector becomes $(D^2\Lambda'^1)$ with $n=3$. All three post-combination remainders are transverse odd and integrate to zero. The next audit keeps the two $n=3$ families in $D=4-2\epsilon$ until their poles are combined with the remaining rational sectors.


### Phase 70: convention-resolved cancellation-first rational kernels

The Phase-50 current convention is applied to the Phase-68/69 sector decomposition. Five separate kernels are generated and Gaussian-reduced: $K_{\mathrm{pres}}$, the $D$-cancel sector, the $k^2$-cancel sector, $\kappa^2/\Lambda'$, and $\kappa^2/\Lambda_0$. All five kernels are pole-free.

A diagnostic QMC at $\rho=0.05$ shows an order-one finite shift relative to the current all-in-one rational routing. At smaller $\rho$, however, the generic soft map has large variance for the newly separated sectors, so those values are not used for a physical conclusion. The next step is a sector-specific soft/secondary-overlap map for the cancellation-first representation.

## v0.78.0: Phase 71 cancellation-first secondary-overlap QMC

`corner_phase71_cancellation_first_overlap_measure_audit()` exactly audits the Jacobian and upper boundaries of the `a_d=u*r` maps for both triangle and line domains.

`corner_cancellation_first_overlap_qmc(rho_value, power=..., seed=..., replicates=...)` evaluates all five Phase-70 sectors with dedicated overlap maps.  Triangle sectors retain `a_l=y` and sample `r` logarithmically up to `(1-y)/u`; line sectors sample up to `1/u`.  The physical `u du` measure and `da_d=u dr` Jacobian are each applied exactly once.

Uncertainty is estimated from independently scrambled Sobol replicate scatter.  This is a finite-rho numerical diagnostic and does not use an archived corrected coefficient as an input.

Run `run_phase71_corner_cancellation_overlap_qmc.bat` and validate with `run_v078_validation.bat`.

## v0.82.0: Phase 75 retained-photon route closure

`corner_retained_photon_residual_kernel()` reconstructs the finite-rho n=4 residual directly from the Phase-69 k2 quotient. Phase 75 fixes the reduced cancellation coefficients by direct pre/post-cancellation family equality rather than by the archived analytic corner result.

## v0.83.0: Phase 76 soft-finite ownership

`corner_phase76_soft_finite_ownership_audit()` identifies the stabilized log-subtracted numerical limit as the hard remainder

$$
H_{\rm fin}=A_{\rm C,fin}-C_{\rm soft}.
$$

`corner_phase76_full_finite_qmc()` restores the independently derived soft finite constant exactly once after assembling the corrected Phase-75 rational route, retained-photon residual, and Phase-52 direct-log route.

## v0.84.0: Phase 77 corner end-to-end checkpoint

`corner_phase77_end_to_end_checkpoint()` audits the sector assembly, the independent soft/hard matching assembly, the closed-form corner finite coefficient, and the infrared-log cancellation with the self-energy insertion pair. All analytic residuals are exactly zero. `corner_phase77_numerical_checkpoint(rho, ...)` compares the stabilized finite-rho QMC with this analytic closure without using the analytic value as numerical input.


## 78. v0.85.0: crossed-ladder end-to-end closure checkpoint

`crossed_phase78_end_to_end_checkpoint()` is the fast crossed-ladder release checkpoint. It verifies exact Breit-projector F1/F2 normalization, endpoint cutoff-log cancellation, and the half-sector plus endpoint-sector analytic assembly with zero residual against the closed form. The expensive raw q-kernel through automatic Hermite/canonical regeneration remains in the dedicated crossed-ladder phases. The historical Karplus--Kroll 1/32 discrepancy is kept separate as an unresolved provenance question.

## v0.86.0 / Phase 79: vacuum-polarization end-to-end closure

`vp_phase79_end_to_end_checkpoint()` joins the physical invariants downstream of the existing raw-subloop bridge: dimensional transversality, $\Pi_R(0)=0$, the finite D->4 kernel, outer magnetic insertion, z-kernel, primitive derivative, endpoints, and final analytic coefficient. The raw LaTeX/topology parse remains independently covered by Phase 21.

## Phase 81: ordinary-ladder end-to-end checkpoint

`examples/phase81_ordinary_ladder_end_to_end_checkpoint.py` combines the corrected 72-term spin-sum projector into 40 symmetry-canonical targets and applies `ladder_corrected_40target_12basis_symbolic_reduction.csv` to reach the 12-master basis.

Audited invariants:

- 40 canonical targets
- 12 terminal masters
- exact cancellation of the leading physical 1/z projector pole
- bare Laurent pole `-3/(4 delta)`
- bare finite part `107/48 + pi^2/18`
- finite one-loop subtraction `2`
- renormalized result `11/48 + pi^2/18`

The expensive 12-master evaluation runs once in the example; pytest keeps a lighter release-invariant check.


## Phase 83 — complete two-loop regression checkpoint

`examples/phase83_two_loop_completion_regression_stdlib.py` audits the Phase 77–82 release artifacts and reduction data without importing scientific packages. The exact seven-diagram coefficient vector in the basis `{1, pi^2, zeta(3), pi^2 ln 2, ln(1/rho)}` is `(197/144, 1/12, 3/4, -1/2, 0)`. The final zero is the exact corner/self-energy IR-log cancellation.

The durable baseline is stored in `data/two_loop_v090_baseline.json`. Future higher-loop changes can run `run_v090_validation.bat` as a single two-loop regression. If SymPy is available, the batch also reruns the fast scientific analytic checkpoints; the heavy ordinary-ladder full master reconstruction remains in its dedicated Phase 81 path.
