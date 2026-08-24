# QEDCalc v0.90.0

<img src=https://github.com/Sanaxen/QEDCalc/blob/main/qed_diagrams_2loop.png>

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


## v0.55.0 progress note

Self-energy insertion is now closed from the raw two diagrams through on-shell renormalization to the final analytic result. Corner (IIc) now has a raw two-diagram parser/topology bridge, q=0 five-parameter denominator family, split-parameter q derivatives, and explicit q-linear magnetic projector generation. The next corner stage is the Gaussian/subtraction bridge to the existing UV-finite parameter representation.


## v0.56.0 progress note

Corner (IIc) now streams the v0.55 q-linear raw-projector polynomials through square completion, tensor reduction, and the two-loop Gaussian moments to regenerate the bare five-simplex kernels `G4` and `G5`. In the two vertex-subgraph UV charts the generated bare residues factorize exactly to one half of the one-loop magnetic density, and the corresponding local `B gamma_rho` subtraction removes the logarithmic UV residue exactly.

The local subtraction is retained as a UV-boundary audit representation, not as the final physical finite normalization. The next stage is direct generation of the renormalized inner-vertex `K`, `m^2/kappa^2`, and `z` sectors followed by the outer magnetic projection.


## v0.57.0 progress note

The physical on-shell-renormalized corner inner vertex is now represented as three explicit sectors rather than being conflated with the five-simplex local UV diagnostic subtraction. The z sector is closed analytically to log(Lambda_prime^2/Lambda0^2), while the corrected kappa-squared sector is rewritten as a denominator difference. Phase 36 verifies both identities and the on-shell subtraction point exactly.

### v0.63 corner progress

Phase 44 propagates the phase-43 D-dimensional evanescent local term through on-shell charge subtraction and the generated outer Breit projector. The local `-3/2 gamma_nu` term cancels exactly between the bare inner vertex and `B gamma_nu`, so it produces no physical corner finite shift.

### v0.64 corner Phase 45

Phase 45 separates the remaining corner discrepancy into inner-operator and outer-convention parts. The generated physical inner remainder is reconstructed exactly in three-sector form with `K_nu^gen = C_nu/2 - 2 f(u) gamma_nu`; all four operator residuals vanish. A local `gamma_nu` insertion independently calibrates the outer projector against the one-loop Schwinger kernel. The raw projector/Gaussian kernel has exact ratio `-4`; after the documented Eq.(42) factor `1/4`, the residual ratio is `-1`. No hand-tuned correction is applied.


## v0.66.0 / v0.67.0 corner update

v0.66.0 re-audits the log-sector denominator cancellation at finite photon mass. With outer photon scalar denominator $P=\rho^2-k^2$ and outer electron denominator $E=-D(k)$,

$$
\frac{A_Kk^2+A_DD}{PE^2L_z}
=
-\frac{A_K}{E^2L_z}
-\frac{A_D}{PEL_z}
+\frac{A_K\rho^2}{PE^2L_z}.
$$

The previous implementation had the opposite signs for the first two lower-denominator families and omitted the photon-mass residual. The corrected identity is verified with exact zero residual before assembly.

Phase 49 in v0.67.0 independently regenerates the preserved on-shell $K_\nu$ full-chain projector instead of loading a final parameter kernel. The transcribed operator is

$$
K_\nu
=
K_\nu^{\mathrm{pres}}
+(1-u)(1-uv)D(k)\gamma_\nu
+2k^2[1-u+u^2v(1-v)]\gamma_\nu.
$$

`corner_historical_K_projector_audit()` includes the $q$ derivative of the first outer electron denominator and regenerates

$$
P_K=D(k)Q_K+R_{\mathrm{odd}}.
$$

The remainder factorizes exactly as

$$
R_{\mathrm{odd}}=k_1k_2\,\mathcal R(k_0,k_1^2,k_2^2,k_3^2;u,v),
$$

so it vanishes under the shifted symmetric outer integration. Phase 49 gives `base/transverse/Q_K/remainder = 21/14/21/4` and exact `P_K-D Q_K-R_odd = 0`. Run `run_phase49_corner_historical_K_projector_audit.bat`.

The independently regenerated historical $Q_K$ is deliberately not aliased to the v0.61+ `C_nu`-derived `lp_quotient`. The remaining corner finite-part discrepancy is now localized to the correspondence between these two operator/family routes. v0.67.0 does not insert or fit the known final finite constant.


## v0.68.0 corner Phase 50 / 51

Phase 49 was a structural audit of the preserved historical $K_\nu$ route. The identity

$$
P_K=D(k)Q_K+R_{\mathrm{odd}}
$$

does not by itself fix the full Karplus--Kroll to current-notation map for explicit $i$ factors, $\sigma_{\mu\nu}$, and the sign convention of $\overline{\Lambda}$.

Phase 50 resolves the seven historical tensor-basis coefficients by solving directly against the independently generated raw-$C_\nu$ magnetic projector. The canonical solution is

$$
\boxed{(-1,\ 1,\ 0,\ -1,\ i,\ 1,\ -\tfrac12)}.
$$

The third basis vector is exactly projector-null. With this resolved map, the base, transverse, and common numerator agree identically with

$$
K_\nu^{\mathrm{current}}=\frac12 C_\nu-2f(u)\gamma_\nu.
$$

Thus the $+C_\nu/(2\Lambda'^2)$ rational sign used by the v0.61+ physical bridge is consistent with the convention-resolved historical $K_\nu$ route.

Phase 51 regroups the current rational remainder back into the historical $K+\kappa^2$ form and verifies exact equality at operator, common-quotient, odd-remainder, and Gaussian-template levels. The remaining finite-part discrepancy is therefore no longer attributed to the rational LP/$K$ sector.

The next corner target is the log sector: regenerate it directly from $\gamma_\nu\log(\Lambda'^2/\Lambda_0^2)$ before any denominator cancellation, then rerun finite-$\rho$ soft-importance QMC.


## v0.70.0 corner Phase 52: direct unsplit reconstruction of the log sector

After Phase 51 proved exact equivalence of the rational historical $K+\kappa^2$ regrouping and the current $LP+B_\gamma$ route, Phase 52 reconstructs the remaining logarithmic sector before denominator cancellation.

The starting identity is

$$
\ln\frac{\Lambda'^2}{\Lambda_0^2}=(\Lambda'^2-\Lambda_0^2)\int_0^1\frac{dz}{\Lambda_0^2+z(\Lambda'^2-\Lambda_0^2)}
$$

with

$$
\Lambda'^2-\Lambda_0^2=u^2v(1-v)k^2+uv(1-u)D(k).
$$

The implementation keeps the full numerator before photon/electron denominator cancellation, parameterizes the four-factor $P E^2L_z$ family directly, and applies the $n=4$ Gaussian master.

`corner_log_unsplit_audit()` returns the direct Gaussian template, the finite-$\rho$ direct parameter kernel, the generated delta coefficients, the exact pre-split scalar residual, and the Gaussian pole audit.

Phase 52 finds no $\Gamma(0)$ pole and an exact zero scalar split residual. Auxiliary uniform scrambled-Sobol checks at $\rho=0.05$ place both the direct and the three-family split log integrals near $0.32$. Those numerical values are diagnostic only because soft-endpoint variance is still too large for regression use.

The next step is to apply the same soft-importance map to both routes, establish numerical agreement within statistical uncertainty, and then re-evaluate the full corner finite part.


## v0.70.0 corner Phase 53 / 54

Phase 53 adds a projective importance map that resolves the soft region while covering the full integration domain.  The $u$ map is

$$
u=\rho[\exp(Lt)-1],\qquad L=\ln\frac{1+\rho}{\rho}
$$

and the outer simplex is parameterized by

$$
r=\frac{ux}{1-x},\qquad s=\frac{uy}{1-y}
$$

$$
a_d=\frac{r}{1+r+s},\qquad a_p=\frac{s}{1+r+s},\qquad a_l=\frac{1}{1+r+s}.
$$

Endpoint coverage, simplex sums, and Jacobians are audited exactly.  Numerical evaluation uses the compact Gaussian templates rather than the fully expanded kernels, which avoids catastrophic cancellation near the soft endpoint.  With this stable route, the direct unsplit and the three-family split log sectors agree within scrambled-Sobol uncertainty for $\rho=0.1,0.05,0.02$.

Phase 54 independently derives the finite normalization of the one-loop vertex subtraction coefficient $B$ from the $D=4-2\epsilon$ radial masters.  The finite integrand is

$$
u\left[-\ln L-\frac12-\frac{2f(u)}{L}\right],\qquad L=u^2+\rho^2(1-u).
$$

Its small-$\rho$ expansion gives

$$
B_{\rm fin}(\rho)=2\ln\rho+\frac{11}{4}+o(1).
$$

Using $A^{(1)}(0)=1/2$, the local finite counterterm constant is

$$
A_{\rm CT,fin}\supset-\frac{11}{8}.
$$

This is an independently generated one-loop normalization checkpoint, not a fit to the final corner constant.  It is not inserted by hand into the current corner kernel.  The next audit determines whether the current Eq. (32) route already contains this local finite normalization.


### v0.70.0 corner update

Phase 55 proves that the finite local $B\gamma_\nu$ normalization cancels completely in the on-shell-renormalized inner remainder, so the phase-54 $-11/8$ counterterm constant is not an additional corner correction.

Phase 56 independently rederives the Eq. (42) normalization: one sequential side gives $\alpha^2/(8\pi^4)$, the mirror pair gives $\alpha^2/(4\pi^4)$, and the common outer-loop $\pi^2$ leaves exactly $\frac14(\alpha/\pi)^2$. It also makes the external $u\,du$ measure ownership explicit for every physical kernel.

The remaining corner task is a controlled treatment of the non-uniform soft overlap and full-corner QMC convergence.

## v0.71.0 corner Phases 57--58: large-r soft overlap

Phase 57 regenerates the non-uniform `a_d=u*r` corner and proves exactly

$$
\boxed{\lim_{r\to\infty} r\left(\mathcal K_K+\mathcal K_{\kappa^2}\right) = \frac{8v}{(1-a_l)^2}}.
$$

A smooth add-subtract profile with the same $1/r$ tail is provided only for numerical variance reduction; its finite part is not an independent physical correction.

Phase 58 fixes the actual simplex cutoff,

$$
R_{\max} = \frac{1-a_l}{u},
$$

and verifies that the overlap add-back owns the corresponding $\ln(1/u)$ coefficient exactly.  Next, use the same cutoff ownership in compact finite-rho full-corner QMC.

### v0.72.0 corner update

Phase 59 attaches the overlap subtraction and analytic add-back to the identical simplex cutoff, with exact recombination and removal of the $1/r$ tail. Phase 60 analytically normalizes the measure-included joint soft density, proving that the universal IR logarithm belongs to the combined soft density rather than to a single sequential family. The next step is to build the finite-rho joint compact density and apply the same subtraction there.


### v0.73.0 corner update

Phase 61 integrates the Phase-60 measure-included joint soft density over the actual finite simplex,

$$
R+S\leq \frac{1}{\rho U}.
$$

With $R=qx$ and $S=q(1-x)$ the finite-triangle normalization $N(T,v)$ closes analytically and satisfies $N(0,v)=0$ and $N(\infty,v)=1$. Its tail is

$$
1-N(T,v)=\frac{2v\ln T+v(1-2\ln v)}{T}+o(T^{-1}).
$$

After $T=1/(\rho U)$ this is only $O(\rho\ln(1/\rho))$, so the primary finite soft triangle cannot generate an order-one corner finite mismatch.

Phase 62 audits ownership of the printed Karplus--Kroll Eq. (28) versus the raw shift-consistent routing. QEDCalc generates the coefficient $-u(1-v)$ of $p''$, while the printed expression uses $-v(1-u)$; shift-consistent minus printed is exactly $v-u$. The stored hard-primary checkpoint is the printed route and `corner_shift_correction_result()` converts it to the shift-consistent hard result. The finite-$\rho$ raw kernel is already shift-consistent, so that correction must not be added again.


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



## v0.75.0: Phase 64 reproducible finite-rho corner evaluator

Phase 64 turns the current SymPy-generated corner parameter kernels into a reproducible optional numerical diagnostic. The evaluator owns the physical measure, parameter domains, soft-importance Jacobians, and the Eq. (42) normalization in one place.

The generated kernels do not contain the outer factor or the inner parameter measure. The evaluator therefore applies

$$
\mathcal N_{\mathrm C}=\frac14
$$

and

$$
d\mu_u=u\,du
$$

exactly once.

The family domains are different and are kept explicit: LP and the two full log families use a two-simplex; $B_\gamma$ and the photon-cancel log family use a one-simplex. The local $B_\gamma$ sector is independent of $v$, so its omitted $v$ integration equals one rather than an additional numerical dimension.

`corner_finite_rho_qmc()` uses only the current generated kernels. Archived corrected QMC values are not inputs to the integrand. At $\rho=0.05$, a small diagnostic run reproduces the known current-route mismatch rather than hiding it, which makes the discrepancy a package-level reproducible regression target.

The active corner question is now narrower: the largest discrepancy sits in the rational remainder. The raw inner-radial bridge and the physical on-shell bridge display opposite signs for the nonlocal $C_\nu/(2\Lambda'^2)$ term. Phase 50 compared against a current-route target and therefore does not by itself provide a non-circular proof of that sign. The next audit must fix the raw-radial to physical-remainder sign using the complete Feynman prefactor/Wick convention, not by fitting the final corner constant.

### Two-loop seven-diagram status

| sector | diagrams | SymPy status |
| --- | ---: | --- |
| corner pair | 2 | raw diagrams through renormalized parameter kernels complete; final finite-rho reconciliation still open |
| self-energy insertions | 2 | raw-to-final analytic result complete |
| vacuum polarization | 1 | raw-to-final analytic result complete |
| ordinary ladder | 1 | raw-to-final analytic result complete |
| crossed ladder | 1 | raw-to-final analytic result complete |

Thus five of the seven diagrams are closed raw-to-final. The remaining two are the corner pair, where the symbolic derivation is deep into the final parameter representation and the unresolved issue is a finite normalization/sign ownership inside the rational remainder rather than missing raw-diagram machinery.


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

## v0.79.0: Phase 72 full stabilized corner audit

Phase 72 combines the Phase-71 stabilized cancellation-first rational route with the independently generated Phase-52 unsplit direct-log kernel using the same physical quarter normalization.  The direct log is integrated through the exact Phase-53 soft bijection and uncertainties are estimated from independent Sobol scrambles.

Both numerical pieces are stable at small rho, but their combined finite estimate approaches roughly +0.29 instead of the analytic checkpoint -0.5640209413... .  The checkpoint is used only after integration as regression metadata and never as a fit, correction, or normalization input.  The remaining discrepancy is therefore classified as a kernel/sector finite-term ownership problem rather than a QMC endpoint-instability problem.

## v0.80.0: Phase 73 finite-rho cancellation / Wick ownership

Phase 73 separates Minkowski denominator cancellation from Wick/Gaussian sign ownership. It proves the leading Phase-70 D- and k2-cancel signs are consistent after the normalized Minkowski scalar-master parity `(-1)^n` is restored. The finite-rho k2 sector also contains a separate photon-mass residual proportional to `-rho^2/(2P)`, which vanishes as rho^2 and therefore cannot by itself explain the observed O(1) finite mismatch.

Run: `run_phase73_corner_cancellation_wick_audit.bat`.

## v0.81.0: Phase 74 non-uniform finite-rho residual

The Phase-73 remainder `-rho^2/(2P)` vanishes at fixed nonzero `k^2`, but remains O(1) in the soft scaling `k^2=rho^2 chi`. It therefore cannot be dropped before integration. Phase 74 freezes this non-commuting limit exactly and adds a checkpoint-free comparison of the Phase-64 and Phase-71 rational routes.

Run: `run_phase74_corner_k2_mass_nonuniform.bat`

## v0.82.0: Phase 75 retained-photon residual and cancellation-sign correction

Phase 75 reconstructs the finite-rho retained-photon residual on the original `P D^2 Lp` family from the Phase-69 `k2_cancel_quotient`. Direct pre-cancellation n=4 versus reduced n=3 sector comparisons show that the extra Wick-parity ratio introduced in Phase 73 double-counted denominator continuation already owned by the Gaussian helper. The reduced coefficients are therefore `D_cancel=-1` and leading `k2_cancel=+1/2`; the retained n=4 residual remains `-rho^2/(2P)`. No analytic corner constant is used to select these signs.

## v0.83.0: Phase 76 soft-finite ownership restoration

The stabilized log-subtracted numerical route evaluates the hard remainder, not the complete finite corner constant. The independently derived soft finite constant

$$
C_{\rm soft}=\frac{\pi^2}{6}+\ln^2 2-3\ln2-\frac74
$$

must be restored exactly once. Phase 76 verifies symbolically that

$$
A_{\rm C,fin}=H_{\rm fin}+C_{\rm soft}
$$

with zero residual and without using the closed-form checkpoint as a fit or numerical input.

## v0.84.0: Phase 77 end-to-end corner closure checkpoint

Phase 77 consolidates the two-loop corner result into one exact regression checkpoint. It independently assembles the historical sector route (hard-primary + shift + z) and the soft/hard matching route (H_fin + C_soft), verifies that both equal the same closed-form finite coefficient with exact symbolic residual zero, and checks the +1 corner infrared logarithm against the -1 self-energy insertion-pair logarithm. `corner_phase77_numerical_checkpoint()` attaches the stabilized finite-rho QMC as an independent numerical diagnostic; the analytic checkpoint is not fed into the kernel, fit, or normalization.

Validation: `run_v084_validation.bat`


## v0.85.0: Phase 78 crossed-ladder end-to-end closure

Phase 78 adds a fast exact release checkpoint for the modern crossed-ladder route. It verifies the Breit magnetic projector normalization (F1 coefficient 0, F2 coefficient 1), exact endpoint cutoff-log cancellation, and equality of the independently assembled half-sector plus endpoint-sector result to the final closed form. The expensive raw-q-kernel to automatic Hermite/canonical regeneration remains in the existing dedicated crossed-ladder phases and is intentionally not rerun by release validation. The historical Karplus--Kroll 1/32 discrepancy remains a separate provenance audit; v0.85 does not claim to locate the lost term in the 1950 algebra.

## v0.86.0: vacuum-polarization end-to-end checkpoint

Phase 79 combines dimensional transversality, on-shell subtraction, the finite D->4 VP kernel, outer magnetic insertion, z integration, generated primitive/endpoints, and the final coefficient in one exact release checkpoint. The result is $A_{VP}=119/36-\pi^2/3$ with zero closure residual. Run `run_v086_validation.bat`.

## v0.88.0: Phase 81 ordinary-ladder end-to-end closure

Phase 81 assembles the corrected 72-term spin-sum projector through 40 symmetry-canonical IBP targets into the 12 analytic master integrals. The leading magnetic-projector z-pole cancels exactly in the physical master sum. The independently reconstructed bare finite coefficient is `107/48 + pi^2/18`; applying the one-loop on-shell subtraction `-3/(4 delta) + 2` gives the renormalized ordinary-ladder coefficient `11/48 + pi^2/18`. The final coefficient is not an input to the master reconstruction and is used only as an output-side checkpoint.

Run `run_phase81_ordinary_ladder_end_to_end_checkpoint.bat`; validate with `run_v088_validation.bat`.


## v0.90.0: complete two-loop regression

`run_v090_validation.bat` is the single release regression for the complete seven-diagram two-loop result. The mandatory path uses only the Python standard library and verifies the five diagram classes, seven-diagram multiplicity, exact corner/self-energy IR cancellation, the ordinary-ladder `72 -> 40 -> 12` reduction invariants, and the final exact basis coefficients `(197/144, 1/12, 3/4, -1/2, 0)`.

When SymPy is available, the same batch additionally reruns the Phase 77–80 scientific analytic checkpoints. The historical crossed-ladder Karplus--Kroll `1/32` gap remains a separate provenance question; its precise location in the 1950 algebra is not claimed to be resolved.
