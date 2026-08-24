# QEDCalc v0.51.0

QEDCalc is an experimental toolkit for splitting long QED calculations into small processing functions while leaving the physical order of operations under user control.

The bundled one-loop vertex-correction workflow starts from LaTeX input and reaches

$$
F_2(0)=\frac{\alpha}{2\pi}.
$$

Since v0.10.0, QEDCalc has included reusable foundations for two-loop and higher-loop calculations. The v0.13.x line added subdiagram/forest bookkeeping and explicit counterterm-subtraction management, while v0.14.0 added contracted-graph/Taylor/forest machinery. v0.16.0 adds an explicit ordered topology-to-amplitude bridge and mixed multi-loop tensor reduction for structures such as $k^\mu l^\nu$.

## Documentation

- `README.md`: Japanese Quick Start
- `README_EN.md`: English Quick Start
- `REFERENCE.md`: Japanese Reference Manual
- `REFERENCE_EN.md`: English Reference Manual
- `CHANGELOG.md`: Change history
- `ROADMAP.md`: Development roadmap

## Requirements

- Windows 11
- Python 3.11 or later
- SymPy 1.13 or later

## First-time setup

Run `setup_env.bat` in the extracted project folder.

It creates `.venv` and installs the libraries listed in `requirements.txt` into that virtual environment.

If an older damaged `.venv` remains, delete the `.venv` folder and run the setup batch again.

## One-loop vertex demo

Run `run_qedcalc.bat`.

Input:

```text
input\vertex_1loop_integrand.tex
```

Output:

```text
output\vertex_1loop_session.md
```

## Multi-loop foundation demo

Run `run_multiloop_demo.bat`.

Output:

```text
output\multiloop_foundation.md
```

The demo covers two loop momenta, matrix square completion, simultaneous numerator shifts, general Feynman parameterization, general-$D$ scalar loop integrals, and explicit counterterm replacement.



## Calculation conventions: `conventions.txt`

QEDCalc does not stop during a calculation to ask interactive convention questions. It loads `conventions.txt` from the project root at startup.

The default file is:

```text
[Spacetime]
metric_signature = +---
dimreg_dimension = 4 - 2*epsilon

[Gauge]
gauge = feynman

[Renormalization]
renormalization_scheme = on_shell
dimreg_subtraction = MSbar
msbar_factor = true

[Subdiagram]
subdiagram_include_coupling = true
subdiagram_include_loop_measure = true
subdiagram_include_i = true

[Normalization]
coupling_symbol = e
loop_measure_denominator_latex = (2\pi)^4
loop_i_factor_latex = i
```

The `subdiagram_include_*` flags define normalization ownership when a one-loop subdiagram is contracted. With the defaults, contracting a one-loop self-energy subdiagram from a two-loop graph automatically leaves the outer prefactor

$$
\frac{e^2}{(2\pi)^4 i}
$$

Run `run_conventions_demo.bat` to inspect the loaded settings. Unknown keys, invalid values, or an unsupported gauge raise an error instead of falling back to an interactive prompt.

## Symbol definitions

Accepted input symbols are predeclared in `symbols.txt`. Greek symbols use LaTeX notation. Undefined symbols are errors and are not silently guessed.

## Markdown equation output

Display equations are always separated from surrounding text by blank lines:

```markdown
Text

$$
formula
$$

Text
```

## Tests

Run `run_tests.bat`.

v0.39.0 passes 173 regression tests including the full bounded degree-2 Cartesian master-candidate audit.

See `REFERENCE_EN.md` for the complete API, conventions, and current limitations.


## Main functionality as of v0.16.0

- `symmetric_even_rank()` for rank 2, 4, 6, 8, ... isotropic tensor reduction
- `dimreg_scale_factor()` for explicit MS / MS-bar dimensional scale factors
- `renormalized_dimreg_series()` for convention application, Laurent expansion, and minimal subtraction
- `bookkeep_uv_ir()` for UV, IR, and mixed UV/IR pole classification
- `qed_counterterm_library()` for the standard $\delta Z_1$, $\delta Z_2$, $\delta m$, and $\delta Z_3$ structures
- `contract_graph()` for contracted topology $G/F$
- `taylor_operator()` for multivariate total-degree Taylor subtraction
- `bphz_local_counterterm()` / `bphz_subtract()` for local BPHZ subtraction
- `forest_formula()` for signed compatible-forest sums

See `REFERENCE_EN.md` for details.


## v0.16.0 Zimmermann / BPHZ demo

On Windows run:

```text
run_forest_demo.bat
```

The generated report is written to `output/forest_subtraction_demo.md`.


## v0.16.0: first real two-loop trial

Run `run_vp_2loop_demo.bat` to execute the vacuum-polarization test. The workflow evaluates the closed electron-loop Dirac trace and the finite two-parameter kernel, then recognizes the final coefficient `119/36 - pi^2/3` from the numerical result.

## v0.17.0: second real two-loop trial — self-energy insertion

v0.17.0 adds the left/right electron self-energy-insertion pair as the second real two-loop trial. QEDCalc reduces the explicitly identified one-loop self-energy subdiagram, performs the loop shift and odd-term removal, evaluates on-shell counterterm formulas and UV-subdivergence cancellation, rationalizes the logarithm for the outer-loop coupling, and cross-checks the finite integral numerically and analytically.

The final checkpoint is

$$
A_{\mathrm S}
=
-\frac12\ln\rho^{-2}
+\frac{11}{24}
-\frac{\pi^2}{18}.
$$

The complete original aligned two-loop LaTeX expression is still not parsed as a single object; the self-energy subdiagram is supplied explicitly as topology metadata. Run `run_self_energy_2loop_demo.bat`.

## v0.18.0: two-loop ordinary-ladder trial

`run_ladder_2loop_demo.bat` adds D-dimensional projector utilities, denominator-basis reduction, validation of the 75-term integral-family coefficient table, and the one-loop subtraction. It reproduces the finite ordinary-ladder coefficient $11/48+\pi^2/18$. Regenerating the complete 75-term table directly from the raw D-dimensional Dirac trace remains future work.


## v0.19.0: crossed-ladder two-loop trial

`run_crossed_ladder_2loop_demo.bat` checks the independently derived projective/one-variable reduction: linearity of $\Delta$ and $W$ in $V$, the $h,t,q$ transformations, the canonical dilogarithmic kernel, the $q=1/2$ sector, endpoint-safe combination, and cancellation against the total-derivative boundary contribution. It reproduces

$$
F_{2,\mathrm X}^{(4)}(0)
=
\left(\frac{\alpha}{\pi}\right)^2
\left[
\frac16
+\frac{13\pi^2}{36}
+\frac54\zeta(3)
-\frac{5\pi^2}{6}\ln2
\right].
$$

The current version does not yet regenerate the several-hundred-term raw Dirac reduction and the five-parameter integrand $G_{\mathrm X}$ automatically; it validates the projective/one-variable stage onward.


## v0.21.0: corner (IIc) two-loop trial

`run_corner_2loop_demo.bat` verifies the independently derived UV-finite corner parameter representation. The trial checks the soft scaling and exact IR-log coefficient, the momentum-shift correction, the complete $K+\kappa^2$ hard sector, the $z$ sector, and the IR cancellation against the self-energy insertion pair.

The soft spatial integral gives the exact coefficient

$$
\int_0^1dv\int_0^\infty dR\int_0^\infty dS\,G(R,S,v)=1.
$$

The two finite sectors combine to

$$
A_{\mathrm C,fin}
=
-\frac{67}{24}+\frac{\pi^2}{18}-\frac12\zeta(3)+\frac{\pi^2}{3}\ln2.
$$

The corner IR coefficient is $+1$ and the self-energy insertion coefficient is $-1$, so the regulator logarithm cancels exactly.

The complete original six-denominator two-loop LaTeX expression is not yet transformed automatically all the way to the UV-finite projected parameter kernel. This trial starts from the independently derived parameter checkpoint and verifies the downstream calculation exactly.

## v0.21.0: first bare two-loop LaTeX input path

v0.21.0 can parse the bare two-loop vacuum-polarization RHS as one structured object rather than requiring the closed-loop numerator as a separate input.

`parse_loop_integral_latex()` separates and preserves the overall normalization, loop measures, and QED integrand. Explicit `DiracTrace` nodes are discovered automatically. Fermion propagators inside the trace can then be scalarized and separated into a trace numerator and a scalar denominator.

The overall normalization is intentionally preserved as LaTeX text so QEDCalc does not silently change user conventions. Full automatic reconstruction of the renormalized outer kernel from the entire bare diagram is still a future step.


## v0.22.1: raw self-energy-insertion discovery

v0.22.1 accepts each left/right self-energy-insertion bare two-loop RHS as one LaTeX input. QEDCalc discovers the ordered electron-line pattern

$$
S(r)\,\gamma^\alpha\,S(r-l)\,\gamma^\beta\,S(r)
$$

together with the separate $l$-photon factor. It identifies $r=p-k$ for the right insertion and $r'=p'-k$ for the left insertion, then contracts the block to $S(r)\Sigma^{(1)}(r)S(r)$. After the existing on-shell UV-cancellation check passes, the same compact topology can be rendered with $\Sigma_R^{(1)}$. The internal-photon numerator reduction currently selects the Feynman-gauge metric part.

## v0.25.0: ordinary-ladder raw-input bridge

The ordinary-ladder bare two-loop RHS can now be read directly from `input/ordinary_ladder_2loop_bare.tex`. QEDCalc derives the symbolic-$D$ loop measures, the ordered electron denominators $E_1$ through $E_4$, photon denominators $K,L$, auxiliary $H=-(k+l)^2$, the bare family index $J(1,1,0,1,1,1,1)$, and the direct $q=0$ Dirac numerator.

The scalar-product-to-denominator rules are independently regenerated by solving the denominator definitions. v0.26.0 also regenerates the historical general-$q^2$ 75-term audit table directly from the raw $D$-dimensional projector trace. v0.27.0 adds a generic IBP identity generator and a finite sparse Laporta elimination core. Automatic seed closure, sector/zero-sector handling, and complete master-integral reduction remain future work.

## Added in v0.25.0

- Arbitrary-length D-dimensional Clifford traces.
- Optimized fully-contracted SymPy trace path.
- Raw ordinary-ladder A0 projector-trace regeneration.
- Automatic generation of the 29 A0 scalar integrals from bare LaTeX.
- Added `run_ladder_a0_trace_demo.bat`.

## v0.26.0: general-$q^2$ ladder trace audit

`run_ladder_general_q_trace_demo.bat` evaluates the long general-$q^2$ $D$-dimensional trace directly from the raw ordinary-ladder LaTeX input. It regenerates the archived historical 75-term audit table with an exact **75/75 coefficient match**.

Important: the archived 75-term CSV belongs to the historical projector-first trace ordering,

$$
\operatorname{Tr}\left[(\rlap{/}p'+m)O_\mu(\rlap{/}p+m)\Gamma_{\mathrm L}^{\mu}\right].
$$

The later audited spin-sum ordering,

$$
\operatorname{Tr}\left[(\rlap{/}p'+m)\Gamma_{\mathrm L}^{\mu}(\rlap{/}p+m)O_\mu\right],
$$

is implemented as a separate route and is never forced to match the historical CSV. The current corrected route generates 72 scalar-integral monomials.

Outputs:

```text
output\ladder_general_q_raw_trace_trial.md
output\ladder_general_q_75_coefficients_generated.csv
output\ladder_general_q_corrected_spin_sum_generated.csv
```


## v0.27.0: IBP / finite Laporta core

`run_ibp_demo.bat` generates integration-by-parts identities for a generic multi-loop denominator family from

$$
0=\int d^{LD}k\,
rac{\partial}{\partial k_i^\mu}\left(v^\mu\prod_a D_a^{-n_a}
ight).
$$

For the ordinary-ladder seven-denominator family, QEDCalc generates the eight canonical identities for the bare seed $J(1,1,0,1,1,1,1)$ using derivatives with respect to $k,l$ contracted with $k,l,p,p'$. A finite sparse symbolic Laporta eliminator is included and is validated on a one-loop tadpole and on the eight-equation ladder seed system. First-neighbor seed generation produces 8 seeds, 64 IBPs, and 181 distinct integrals. Full seven-denominator closure still needs sector ordering, zero-sector detection, automatic seed expansion, and faster coefficient-field simplification.


## v0.29.0: family symmetry and generic-rank probes

The four-element ordinary-ladder symmetry group canonicalizes integral indices. The degree-2 domain drops from 36 seeds to 24 representatives and from 623 to 335 distinct integrals. An exact-rational generic-point probe yields 162 pivots for fast rank/closure diagnostics; it does not replace the arbitrary-kinematics symbolic reduction.


## Addition: exact rational reconstruction (v0.31.0)

QEDCalc can now reconstruct rational functions of $D,z$ from exact-rational generic-point Laporta reductions. Floating-point samples are rejected, and a candidate is accepted only after exact agreement on independent holdout points. The corrected ordinary-ladder route reconstructs representative coefficients for $J(-1,0,0,1,1,1,1)$ and $J(0,0,1,1,0,1,1)$. Full target-wide reconstruction still requires adaptive degree bounds, pole avoidance, and finite-field/modular acceleration.

## Added: corrected 40-target reconstruction audit (v0.32.0)

`run_full_target_reconstruction_demo.bat` applies exact-rational Laporta reduction and symbolic $D,z$ reconstruction to all 40 symmetry-canonical targets of the corrected ordinary-ladder projector route.

A target is no longer considered reduced merely because it appears as a Laporta pivot. QEDCalc recursively applies the generated rules and refuses interpolation whenever any integral outside the six stable candidates remains.

Current corrected-route classification:

- 6 candidate-basis targets,
- 6 additional targets fully closed on that basis and reconstructed with independent holdout validation,
- 28 targets containing non-candidate residues,
- 0 closed targets failing the degree-(3,3) rational ansatz.

This shows that the present bottleneck is residue-aware seed closure, not interpolation degree. Expanding every residue neighborhood at once scales too aggressively, so the next step is a sector- and residue-priority closure scheduler.


## v0.34.0 residue-aware closure scheduler

Adds target-impact and sector-priority residue scheduling for the corrected ordinary-ladder closure. A bounded direct-residue phase grows the baseline from 84 to 114 seeds, 666 to 906 IBP rows, and 598 to 823 pivots, reducing residue-bearing targets from 28 to 27 without the blow-up of all-at-once neighborhood expansion. Run `run_residue_scheduler_demo.bat`.

## v0.34.0: incremental phase-2 residue scheduling

The phase-2 scheduler now reuses the 823 phase-1 pivots and reduces only the IBP rows of each newly tested seed. Among 22 neighborhood candidates from sectors 96 and 80, 7 directly solve known terminal residues; a greedy marginal-coverage scheduler selects 2 seeds. Run `run_phase2_scheduler_demo.bat`.


## v0.35.0: phase-3 factorized lower subtopologies

Applying the two v0.34 phase-2 seeds for real raises the pivot count from 823 to 837, but full recursive reduction still leaves 27 residue-bearing targets: the high-power residues descend to simpler lower sectors instead of disappearing.

`factorized_one_denominator_per_loop()` analyzes the loop-space quadratic forms of active denominators and recognizes strict L-loop sectors that separate into L independent rank-one one-loop factors. Three ordinary-ladder terminal residues are thereby identified as products of one-loop massive tadpoles rather than new genuine two-loop masters. Treating them as known lower subtopologies reduces residue-bearing targets from **27 to 18**. `is_scaleless_zero_sector_extended()` also detects sectors with an unconstrained free loop direction. Run `run_phase3_factorized_demo.bat`.


### v0.37.0: directional depth-2 master-candidate audit

QEDCalc now tests the three remaining provisional ordinary-ladder master candidates beyond the first neighborhood using a bounded directional depth-2 seed domain. `directional_depth2_seeds()` moves one family index two steps in the same direction, while `diagnose_directional_depth2_irreducibility()` incrementally tests whether the residue becomes a new pivot.

All three candidates remain non-pivoting at three independent exact-rational probes. This is stronger bounded evidence, not a global master-integral proof, so they remain **depth-2-stable provisional master candidates**.

Demo: `run_phase5_depth2_master_demo.bat`

### v0.39.0: full degree-2 Cartesian audit

For the three remaining ordinary-ladder candidates, QEDCalc now exhausts the mixed two-direction degree-2 seeds in addition to the first-neighbor and directional depth-2 domains. At the primary exact-rational probe, all three remain non-pivoting in the complete bounded degree-2 Cartesian neighborhood. The 837-pivot rule set is stored as a portable JSON checkpoint for fast reproducible audits.

Run: `run_phase6_full_degree2_master_demo.bat`


## v0.39.0: Three-probe full degree-2 audit

The three provisional ordinary-ladder master candidates remain non-pivoting throughout the complete bounded degree-2 Cartesian neighborhood at all three independent exact-rational probes. Every baseline has 837 pivots. Incremental Laporta now shares a persistent reduction cache. This is a bounded audit, not a global master proof.


## v0.40.0: three-probe full bounded degree-3 audit

For the three provisional ordinary-ladder master candidates, QEDCalc now generates the new bounded degree-3 shell after removing the already-audited degree <= 2 domain, canonicalizes it by family symmetry, and appends it to the existing Laporta system sector by sector.

The new APIs are `degree3_shell_seeds()` and `diagnose_full_degree3_irreducibility()`. The three independent exact-rational probes all retain the same 837-pivot baseline. The new degree-3 shells contain 72/84/84 seeds for candidates 1/2/3, and the candidate itself remains non-pivot in all nine probe/candidate combinations.

This is strong bounded evidence for the three provisional master candidates, but it is not a global proof of the master count.


## v0.41.0: complete ordinary-ladder symbolic coefficient table

The corrected spin-sum route now closes all 40 symmetry-canonical targets on 12 terminal basis integrals.

Of the full $40\times12=480$ coefficient matrix entries, 151 are nonzero. Every nonzero $c_{ia}(D,z)$ is stored as an exact rational function and has been checked at 91 Cartesian-grid points plus three independent exact-rational probes outside that grid, for 94 exact validation points per coefficient.

The full table is `data\ladder_corrected_40target_12basis_symbolic_reduction.csv`; the nonzero-only table is `output\ladder_corrected_40target_symbolic_nonzero.csv`.

Run `run_phase9_full_symbolic_reduction_demo.bat` to audit the checkpoint.


## v0.42.0: ordinary-ladder 12-basis evaluation layer

v0.42.0 starts evaluating the 12 terminal basis integrals obtained in v0.41.0. `classify_ordinary_ladder_terminal_basis()` generates projective Feynman-parameter polynomials $U$, $F$, and $\Delta=F/U$ directly from the seven-denominator family for every basis integral.

At generic $z$, basis 0, 1, and 3 are factorized lower sectors. At the magnetic point $z=0$, the degeneracies $E_1=E_4$ and $E_2=E_3$ simplify additional sectors: basis 2 and 4 factor into massive tadpoles; basis 5 and 6 are one-massless/two-equal-mass vacuum sunsets; basis 7 and 9 are evaluated by a massless bubble followed by a generalized on-shell one-loop integral.

Therefore **9 of 12** basis integrals now have exact Gamma-function values at $z=0$. The remaining genuine two-loop evaluation problem is reduced to **basis 8, 10, and 11**. Values are stored as convention-free Euclidean scalar integrals; Minkowski $i$ factors, Wick-rotation signs, $(2\pi)^D$, and renormalization scales remain in the convention layer.

Run: `run_phase10_basis_evaluation_demo.bat`


## v0.43.0: complete analytic $z=0$ ordinary-ladder basis evaluation

The three basis integrals left unresolved in v0.42.0 (8, 10, 11) collapse at $z=0$ into one reduced family

$$
T_n=\int\frac{d^Dk\,d^Dl}{L\,H\,E_2\,E_4^n},\qquad n=1,2,3.
$$

A dedicated five-denominator family $(K,L,H,E_2,E_4)$ regenerates symbolic IBP relations that reduce $T_2$ and $T_3$ to $T_1$ plus lower sectors. The lower sectors are either scaleless or Gamma-function closed forms obtained from a massless two-point subloop followed by a generalized on-shell one-loop integral.

For $T_1$, a Cheng--Wu gauge $x_{E_2}+x_{E_4}=1$ reduces the projective integral to one variable. Euler--Beta integration gives ${}_3F_2(1)$ functions whose common upper/lower parameters cancel, leaving Gauss-summable ${}_2F_1(1)$ functions. Thus $T_1$ is also Gamma-only.

Therefore all 12 terminal basis integrals are analytic at $z=0$. Use `run_phase11_complete_basis_demo.bat` to regenerate the audit.


## v0.44.0: ordinary-ladder projector/reduction assembly

The corrected 72 raw projector monomials are canonicalized to 40 symmetry targets and composed with the exact 40 x 12 symbolic IBP matrix. No `1/z^2` pole survives, and the complete `1/z` coefficient cancels exactly after the exact z=0 basis relations are inserted. Only basis derivatives 0, 1, 3, 5, 6, 7, and 8 are required for the finite limit.


## v0.45.0: crossed-ladder raw bridge and symmetry-reduced IBP

- corrected raw crossed projector: 95 scalar-integral monomials
- graph reversal symmetry reduces 95 targets to 52 canonical targets
- primary exact probe: 416 IBP rows, 378 pivots, 40 target pivots
- the remaining 12 targets are non-pivoting at P1 in first-neighbor, directional depth-2, and mixed degree-2 bounded audits
- the same 12 baseline non-pivot targets occur at three independent exact-rational probes
- the raw six-denominator scalar core now generates Symanzik U/F automatically (degrees 2 and 3)

The main remaining crossed bridge is automatic conversion of the projected numerator into the detailed projective kernel used by the audited analytic route.

## v0.46.0: crossed-ladder q-linear magnetic-projector bridge

The raw crossed numerator can now be rewritten with `p'=p+q` and truncated at first order before projector assembly.  Full distribution gives exactly 144 `q^0` chains and 84 `q^1` chains, matching the independent 228-chain derivation.

At `q=0`, the two central electron denominators coincide.  QEDCalc therefore builds the five-denominator family `K,L,Dk,Dkl,Dl` with powers `(1,1,1,2,1)`.  The generic Symanzik generator independently reproduces the five-parameter denominator polynomials `Delta` and `W` and the expected measure factor `y`.

The Breit-frame magnetic projector is also checked with explicit 4x4 Dirac matrices and on-shell spinors: the projector kills `F1` exactly and returns unit coefficient for `F2`.  The denominator correction `2*x*k.q + y*(k+l).q` is exposed as a separate first-order object.

Run `run_phase20_crossed_qlinear_bridge_demo.bat`.
