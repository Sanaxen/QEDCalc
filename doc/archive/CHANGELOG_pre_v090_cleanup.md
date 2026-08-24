# v0.88.1

- Windows validation hotfix for Phase 81.
- `mpmath` is now an optional extended-audit dependency instead of a required import.
- When `mpmath` is unavailable, validation still checks the exact symbolic release invariants: 40 canonical targets, 12 master bases, leading $1/z$ cancellation, on-shell subtraction, and the renormalized closed-form residual.
- No physics formula or ladder reduction data changed.

# v0.47.0

- Added streaming crossed-ladder generation of the 244-term homogeneous degree-8 projective numerator `P_X` directly from the raw Dirac numerator and O(q) magnetic projector.
- Added exact cancellation of the apparent rank-4 `Gamma(0)` sector before the Gaussian result is accepted.
- Added graph-reversal check `x <-> z`, `u <-> v`.
- Added algebraic six-term V partial-fraction bridge without a general `apart()` call.
- Verified the simple-pole logarithmic cancellation and the detailed-derivation h-logarithm argument exactly.
- Added Phase 21/22 demos and v0.47 regression tests.

## v0.44.0

- Added `qedcalc.operations.ladder_assembly` for corrected ordinary-ladder projector/reduction composition.
- Canonicalizes the 72 corrected raw projector monomials to the 40 symmetry targets and composes them with the exact 40 x 12 symbolic IBP matrix.
- Added exact simple- and double-pole diagnostics for the magnetic-projector `z -> 0` limit.
- Verified that no `1/z^2` pole survives the 72 -> 40 -> 12 composition.
- Verified that the complete `1/z` coefficient cancels exactly after inserting the v0.43 exact z=0 basis relations (with the v0.41 matrix normalization `m^2=1`).
- Identified the only basis derivatives required for the finite limit: basis 0, 1, 3, 5, 6, 7, and 8.
- Added `run_phase12_ladder_assembly_demo.bat`, `phase12_ladder_assembly_trial.md`, and regression tests.

# Changelog

## v0.43.0

- Completed the ordinary-ladder $z=0$ terminal-basis evaluation: 12/12 exact.
- Added the reduced $(K,L,H,E2,E4)$ IBP family and symbolic $T_2,T_3$ reductions.
- Added a generalized massless-two-point -> on-shell-electron Gamma evaluator.
- Added the Cheng--Wu / hypergeometric / Gauss Gamma-only closed form for $T_1$.
- Added `run_phase11_complete_basis_demo.bat` and complete 12-basis evaluation output.

## v0.42.0
- Added the ordinary-ladder terminal-basis evaluation layer.
- Added convention-free projective Feynman-parameter generation `(U,F,Delta)` for all 12 v0.41 terminal basis integrals.
- Classified the generic-z basis into 3 factorized lower sectors and 9 genuine two-loop candidates.
- At z=0, derived exact Gamma-function values for 9 of the 12 basis integrals.
- Added exact helpers for massive tadpoles, the one-massless/two-equal-mass vacuum sunset, and a massless bubble followed by a generalized on-shell electron integral.
- Reduced the remaining z=0 master-evaluation problem to basis 8, 10, and 11.
- Added `run_phase10_basis_evaluation_demo.bat`, classification/evaluation CSV outputs, and regression tests.

## v0.41.0
- Completed the corrected ordinary-ladder symbolic reduction from 40 symmetry-canonical targets to 12 terminal basis integrals.
- Reconstructed all 151 nonzero coefficient functions as exact rational functions of `D` and `z`.
- Validated every nonzero coefficient on a 91-point Cartesian grid plus three independent exact-rational probes (94 exact checks per coefficient).
- Added denominator-guided reconstruction helpers `infer_allowed_univariate_denominator()` and `reconstruct_bivariate_with_known_denominator()`.
- Added the full 40 x 12 symbolic reduction checkpoint and the phase-9 demo.
- Rejected earlier grid-only overfits unless they also pass the three independent 837-pivot checkpoints.

## v0.40.0
- Added bounded degree-3 shell generation and sector-batched incremental Laporta auditing.
- Audited all three provisional ordinary-ladder master candidates at three independent exact-rational probes.
- Degree-3 shell sizes are 72/84/84; none of the nine probe/candidate cases pivoted the candidate.
- Added `run_phase8_full_degree3_demo.bat`.


## v0.39.0

- Added persistent shared recursive reduction caches with `build_integral_reducer()` and reused them across incremental Laporta rows.
- Added portable 837-pivot checkpoints for exact-rational probes 2 and 3.
- Repeated the complete bounded degree-2 Cartesian audit at all three independent exact-rational probes.
- For all three provisional ordinary-ladder candidates, mixed degree-2 batch extensions leave the candidate non-pivoting at probes 1, 2, and 3.
- All three independently rebuilt phase-2 baseline systems contain 837 pivots.
- Added the phase-7 three-probe audit report and CSV checkpoint.
- This remains bounded evidence, not a global proof of master-integral status.

## v0.38.0

- Added the mixed part of the full bounded Cartesian degree-2 seed audit.
- Added `mixed_degree2_seeds()` and `diagnose_mixed_degree2_irreducibility()`.
- Added portable JSON Laporta-rule checkpoints with `write_laporta_rule_checkpoint()` / `read_laporta_rule_checkpoint()`.
- Ordinary-ladder primary probe: all three provisional candidates remain non-pivoting in the complete bounded degree-2 Cartesian neighborhood.
- Added `run_phase6_full_degree2_master_demo.bat`.

## v0.35.0

- Added rank-one loop-direction analysis for propagator denominators.
- Added an extended free-loop zero-sector diagnostic for sectors with an unconstrained loop integration direction.
- Added strict recognition of factorized lower subtopologies with one independent rank-one denominator per loop.
- Added convention-free Euclidean evaluation of such factorized sectors as products of one-loop scalar tadpoles.
- Performed the actual recursive check of the v0.34 phase-2 pair: 823 -> 837 pivots, but residue-bearing targets remain 27 because the high-power residues descend rather than disappear.
- Recognizing three descended lower-sector residues as factorized one-loop products reduces residue-bearing corrected targets from 27 to 18 and leaves only three terminal residue kinds.
- Added `run_phase3_factorized_demo.bat` and CSV diagnostics.

## v0.34.0

- Added incremental Laporta extension that reuses an existing triangular reduction instead of recomputing the full IBP system for every new seed.
- Added cheap phase-2 neighborhood seed scoring based on direct terminal-residue pivots.
- Added greedy marginal target-coverage scheduling for neighborhood seeds.
- On the corrected ordinary-ladder phase-1 system, 22 neighborhood candidates from sectors 96 and 80 are screened; 7 have positive direct impact and 2 seeds cover the terminal residues blocking a union of 26 targets.
- Added `run_phase2_scheduler_demo.bat`.


## v0.29.0

- Added generic denominator-permutation integral symmetries and orbit canonicalization.
- Added the four-element ordinary-ladder symmetry group generated by external exchange and a unit-Jacobian loop reparametrization.
- Degree-2 ladder seeds reduce from 36 to 24 symmetry representatives; distinct integrals reduce from 623 to 335.
- Added exact-rational coefficient specialization for fast generic-rank probes.
- The symmetry-reduced degree-2 probe produces 162 forward-sparse pivots at a generic rational point.
- Symbolic arbitrary-kinematics reconstruction remains separate from the probe.


## v0.28.0

- Added conservative scaleless zero-sector detection.
- Added sector-aware Laporta ranking and bounded seed domains.
- Added forward sparse elimination; the 64-equation first ordinary-ladder neighborhood yields 63 pivots.
- Degree-2 bounded generation produces 36 seeds, 288 IBPs, and 623 distinct integrals.
- 148 tests passed.

## v0.27.0

- Added generic multi-loop `IntegralFamily`, `IntegralIndex`, and sparse `IBPEquation` representations.
- Added automatic IBP generation from total derivatives with loop/external contraction vectors.
- Added scalar-product reduction of denominator derivatives back to the family basis.
- Added the ordinary-ladder seven-denominator IBP adapter.
- Added a finite sparse symbolic Laporta elimination core and recursive rule application.
- Validated the reducer on a one-loop tadpole: `J(2)=(D-2)J(1)/(2 m^2)`.
- Generated the eight canonical IBPs for the ordinary-ladder bare seed.
- Added sector signatures/IDs and first-neighbor seed generation.
- First ordinary-ladder neighborhood: 8 seeds, 64 IBPs, 181 distinct integrals.
- Added `run_ibp_demo.bat` and `output/ibp_laporta_trial.md`.
- 143 tests passed.

## v0.26.0

- Optimized arbitrary-length fully-contracted D-dimensional Clifford traces by aggregating pairing monomials before SymPy materialization.
- Added global caching for pairing patterns and fully-contracted Clifford words.
- Added general-q ordinary-ladder raw projector traces.
- Regenerated the archived historical 75-term ladder coefficient table from the raw bare LaTeX expression with an exact 75/75 coefficient match.
- Added a separate corrected spin-sum trace route; it is intentionally not forced to match the historical audit CSV.
- Added `ladder_corrected_projector_coefficients`, table comparison helpers, CSV export, and `run_ladder_general_q_trace_demo.bat`.
- Added regression tests that preserve the distinction between the historical audit table and the corrected physical trace ordering.
- 136 tests passed.

## v0.25.0

- Added arbitrary-length D-dimensional Clifford traces.
- Added fully-contracted Lorentz-network reduction.
- Added an optimized scalar SymPy trace engine for long closed projector traces.
- Regenerated the ordinary-ladder A0 projector trace directly from raw bare LaTeX.
- Automatically generated the complete 29-integral A0 table.
- Added `run_ladder_a0_trace_demo.bat` and generated CSV/Markdown audit output.
- The general-q^2 75-term audit-table generation remains the next ordinary-ladder milestone.

# QEDCalc Changelog

## v0.24.0

- Added symbolic `D` loop-measure parsing for raw multi-loop LaTeX.
- Fixed scalar photon fractions such as `1/(-k^2-i epsilon)` so they are not misclassified as fermion propagators.
- Added the raw ordinary-ladder bare input file.
- Added automatic E1..E4 electron-propagator momentum detection and K/L photon-denominator detection.
- Added the seven-denominator ladder family bridge with auxiliary H and bare index J(1,1,0,1,1,1,1).
- Added denominator-equation-based derivation of the ladder scalar-product basis.
- Added direct q=0 Dirac-numerator generation from the raw graph.
- Updated the ordinary-ladder demo and Japanese/English documentation.
- 127 tests passed.

## v0.23.0

- Added project-level `conventions.txt` and typed `QEDConventions` loading/validation.
- Added metric, gauge, renormalization, dimensional-regularization, subdiagram-normalization, and loop-normalization settings.
- Removed the need to pass the self-energy outer prefactor in normal use; it is generated from convention ownership rules.
- Kept `outer_prefactor_latex` as an explicit override for special conventions.
- Connected dimensional-regularization helpers to `dimreg_subtraction` and `msbar_factor`.
- Raw self-energy reduction now rejects unsupported non-Feynman-gauge automatic reduction instead of silently discarding longitudinal terms.
- Added `run_conventions_demo.bat` and `output/conventions.md`.
- Updated Japanese/English README and reference manuals.
- 124 tests passed.

# QEDCalc v0.22.1

- Fixed all Windows demo batch files to launch examples with `python -m examples.<module>` so the project root remains on Python's import path.
- Prevents `ModuleNotFoundError: No module named 'qedcalc'` when running demo batches.

# QEDCalc Change Log

## v0.22.1

- Added raw bare two-loop LaTeX inputs for both left/right self-energy-insertion diagrams.
- Added ordered open self-energy-subdiagram discovery from repeated fermion-propagator structure.
- Added automatic left/right insertion classification and subloop-momentum identification.
- Added canonical Feynman-gauge numerator reduction to $4m-2\rlap{/}r+2\rlap{/}l$.
- Added `SelfEnergySubdiagram` structural marker and LaTeX rendering for $\Sigma^{(1)}$ / $\Sigma_R^{(1)}$.
- Added compact outer-loop contraction from the raw two-loop chain to $S\Sigma S$.
- Connected the raw bridge to the existing on-shell UV-cancellation check before promoting to $\Sigma_R$.
- Updated the self-energy two-loop demo, Japanese/English README, and Japanese/English reference manuals.
- 118 tests passed.

## v0.20.0

- Added the first corner (IIc) two-loop trial.
- Added exact soft-scaling kernel and IR-log coefficient checks.
- Added explicit momentum-shift coefficient bookkeeping for $p'-k$.
- Added diagnostic soft/hard split helpers with double-counting safeguards.
- Added hard-primary, shift-correction, complete $K+\kappa^2$ hard-sector, and $z$-sector analytic checkpoints.
- Reproduced $A_{\mathrm C,fin}=-67/24+\pi^2/18-\zeta(3)/2+(\pi^2/3)\ln2$ exactly.
- Added explicit IR-log cancellation check against the self-energy insertion pair.
- Added `corner_2loop_trial.py` and `run_corner_2loop_demo.bat`.
- Updated Japanese/English README and reference manuals.
- 108 tests passed.

## v0.19.0

- Added the crossed-ladder two-loop trial.
- Added projective crossed-ladder denominator helpers and the h/t/q transformation checks.
- Added the canonical one-variable dilogarithmic kernel.
- Added endpoint-safe sector combination and explicit cutoff-log cancellation checks.
- Added analytic q=1/2 and endpoint-sector composition through the final coefficient.
- Added `run_crossed_ladder_2loop_demo.bat`.
- Updated Japanese and English reference manuals.
- 100 tests passed.

## v0.18.0

- Added the first ordinary-ladder two-loop trial.
- Added D-dimensional Pauli-projector coefficient utilities.
- Added D-dimensional outer-gamma identities that preserve evanescent `(D-4)` terms.
- Added ordinary-ladder scalar-product to denominator-basis substitutions.
- Added `LadderIntegralIndex` and a loader/validator for the reproducible 75-term coefficient table.
- Added D-dimensional one-loop `F2` and `Z1` subtraction utilities.
- Verified the ordinary-ladder UV pole cancellation and final coefficient `11/48 + pi^2/18`.
- Added `run_ladder_2loop_demo.bat`.
- Updated Japanese and English reference manuals.

# CHANGELOG

## v0.17.0

- Added the second real two-loop trial: the left/right electron self-energy insertion pair.
- Added reusable one-loop self-energy denominator and on-shell denominator helpers.
- Added generic on-shell counterterm formulas for Sigma = m A(r^2) + /r B(r^2).
- Added explicit UV-subdivergence cancellation check.
- Added logarithm-to-rational-parameter helpers used before coupling the self-energy block to the outer loop.
- Added finite four-parameter and reduced one-variable cross-check kernels.
- Added `run_self_energy_2loop_demo.bat`.
- Extended 4D gamma contraction with gamma^a gamma_a = 4 and improved numeric-sign simplification.
- Two-loop checkpoint reproduced: A_S = -1/2 log(rho^-2) + 11/24 - pi^2/18.
- 87 tests passed.


## v0.16.0

- Added explicit ordered topology-to-amplitude templates.
- Added safe contracted-amplitude construction using declared local vertices.
- Non-contiguous subdiagram replacement is rejected instead of guessed.
- Added mixed multi-loop tensor reduction using the inverse quadratic matrix.
- Added rank-2 and rank-4 mixed-loop tensor support for forms depending on $Q=L^TML$.
- Added `topology_amplitude_demo.py` and `run_topology_demo.bat`.
- Rechecked the bundled one-loop workflow through $F_2(0)=\alpha/(2\pi)$.
- Updated Japanese/English README and reference manuals.
- 78 tests passed.

## v0.14.0

- Added topology-only `ContractedGraph` representation for $G/F$.
- Added nested/disjoint forest contraction with local `CT[...]` topology vertices.
- Added multivariate total-degree Taylor subtraction operator.
- Added `TaylorSubtractionSpec` linked to declared subdiagrams.
- Added local BPHZ counterterm and $(1-t)$ subtraction helpers.
- Added topology-driven Zimmermann forest-sum assembly with explicit amplitude providers.
- Added `forest_subtraction_demo.py` and `run_forest_demo.bat`.
- Updated Japanese/English README and reference manuals.
- Regression: bundled one-loop result remains $F_2(0)=\\alpha/(2\\pi)$.
- 71 tests passed.

## v0.13.1

- Fixed LaTeX rendering of QED renormalization constants: `deltaZ1`, `deltaZ2`, `deltaZ3`, and `delta_m` now render as $\delta Z_1$, $\delta Z_2$, $\delta Z_3$, and $\delta m$.
- Ensured plain internal Greek identifiers such as `zeta`, `eta`, and `omega` render with their LaTeX command backslashes.
- Added explicit rendering for `epsilon_UV` and `epsilon_IR`.
- Grouped additive photon-counterterm structures so $\delta Z_3$ visibly multiplies the complete structure.
- Added renderer regression tests.
- Updated Japanese/English README and reference manuals to v0.13.1.
- 64 tests passed.

## v0.13.0

- Added explicit `Subdiagram` topology metadata.
- Added nested/disjoint/overlapping relation checks and compatible-forest enumeration.
- Added counterterm assignments, coverage checks, and explicit renormalized-amplitude assembly.
- Added MS/MS-bar pole-counterterm generation and minimal R-operation helpers.
- Added the renormalization-process demo.
- Regression: bundled one-loop result remains $F_2(0)=\alpha/(2\pi)$.
- 61 tests passed.

## v0.12.0

- Added `symmetric_even_rank()` for general even-rank isotropic tensor reduction.
- Rank 6 and higher are generated from all complete metric pairings.
- Added an explicit dimensional-regularization convention layer.
- Added MS and MS-bar scale factors with the documented QEDCalc convention $S_\epsilon=(4\pi e^{-\gamma_E})^\epsilon$.
- Added minimal pole subtraction helpers.
- Added independent UV / IR / mixed-pole bookkeeping.
- Added the standard QED counterterm library for $\delta Z_1$, $\delta Z_2$, $\delta m$, and $\delta Z_3$.
- Extended the multi-loop foundation demo and Markdown output.
- Removed the stale `QEDCalc v0.7.0` stage banner.
- Updated Japanese and English README/reference manuals to v0.12.0.
- Regression: bundled one-loop result remains $F_2(0)=\alpha/(2\pi)$.
- 54 tests passed.


## v0.11.0

- Added `feynman_parameterize_powers()` for arbitrary positive integer denominator powers.
- Added `GeneralFeynmanParamIntegral` internal representation and LaTeX rendering.
- Added `euclidean_scalar_loop_integral()` for general $D$, numerator power $r$, and denominator power $n$.
- Added `dimensional_regularized_loop_series()` for expansion around $D=4-2\epsilon$.
- Added simultaneous multi-loop numerator shifts with `shift_multiloop_momenta_in_numerator()`.
- Added explicit counterterm factor replacement and insertion operations.
- Added `CountertermInsertion` internal representation.
- Extended the multi-loop foundation demo and Markdown output.
- Fully refreshed Japanese and English reference manuals for current functionality.
- Regression: bundled one-loop result remains $F_2(0)=\alpha/(2\pi)$.
- 47 tests passed.

## v0.10.0

- Added reusable multi-loop quadratic-form square completion.
- Added multiple loop-momentum declarations.
- Added rank-4 symmetric tensor averaging.
- Added unit-power N-denominator Feynman parameterization.
- Added UV/IR Laurent pole representation and extraction.
- Added explicit counterterm objects.
- Preserved the complete one-loop vertex-correction workflow.

## v0.9.0

- Completed the bundled one-loop vertex-correction workflow through $F_2(0)=\alpha/(2\pi)$.

## v0.21.0

- Added `DiracTrace` and `LoopIntegralExpression` core objects.
- Added `parse_loop_integral_latex()` for bare multi-loop RHS input.
- Added vector-component parsing such as `k_\rho` and `k^\rho`.
- Added explicit `\operatorname{tr}[...]` parsing and rendering.
- Added generic closed-trace discovery/reduction helpers in `bare_diagram.py`.
- Upgraded the two-loop vacuum-polarization demo to parse the full bare two-loop RHS as one structural object.
- The overall scalar normalization is preserved verbatim in LaTeX while loop measures and the QED integrand are structurally parsed.


## v0.31.0

- Added exact multivariate rational-function reconstruction from exact-rational samples.
- Added independent holdout validation; floating-point samples are rejected.
- Added reconstruction of sampled Laporta reduction coefficients onto a protected candidate basis.
- Ordinary-ladder corrected route now reconstructs representative analytic coefficients in symbolic $D,z$.
- Added `run_rational_reconstruction_demo.bat`.

## v0.32.0

- Added batch symbolic reconstruction for all corrected ordinary-ladder canonical targets.
- Added `TargetReconstructionStatus`, `BatchReconstructionResult`, `reduction_residuals()`, `sampled_target_reductions()`, and `batch_reconstruct_targets()`.
- Reconstruction is now refused whenever recursive Laporta reduction leaves a non-candidate residue at any exact-rational probe.
- Added early residue screening so obviously non-closed targets are not needlessly expanded at every probe point.
- Added `run_full_target_reconstruction_demo.bat`.
- Corrected ordinary-ladder 40-target audit result: 6 candidate-basis targets, 6 additional holdout-validated reconstructed targets, 28 residue-bearing targets, 0 closed-but-unreconstructable targets within degree (3,3).
- Added the 84-seed corrected closure checkpoint to `data/ladder_corrected_closure_84_seeds.csv`.
- A naive residue-neighborhood expansion was tested and found to scale too aggressively; the next step is a sector/residue-priority closure scheduler rather than all-at-once expansion.


## v0.33.0

- Added residue impact profiling and sector aggregation for terminal Laporta residues.
- Added bounded sector scheduling via `schedule_residue_sectors()`.
- Added direct-residue phase before neighborhood expansion.
- Corrected ordinary-ladder phase-1 result: 84→114 seeds, 666→906 IBPs, 598→823 pivots, residue-bearing targets 28→27.
- Added `run_residue_scheduler_demo.bat` and scheduler CSV diagnostics.

## v0.36.0

- Added bounded first-neighborhood local-irreducibility diagnostics for terminal IBP residues.
- Added `LocalIrreducibilityDiagnostic`, `diagnose_first_neighbor_irreducibility()`, and `promote_local_master_candidates()`.
- Ordinary-ladder phase-4 audit: the three genuine residues remaining after factorized lower-sector recognition each have zero pivoting seeds in their seven new canonical first-neighbor trials.
- Treating those three strictly as provisional local master candidates expands the corrected non-factorized basis from 6 to 9 and closes the 40 corrected canonical targets relative to that provisional basis plus known factorized lower sectors.
- This is explicitly not presented as a proof that the three integrals are globally irreducible masters.


## v0.37.0

- Added `DirectionalDepth2Diagnostic`, `directional_depth2_seeds()`, and `diagnose_directional_depth2_irreducibility()`.
- Added `build_specialized_laporta_rules()` for independent exact-rational multi-probe Laporta audits.
- Ordinary-ladder phase-5 audit: the three remaining provisional candidates remain non-pivoting in bounded directional depth-2 tests at three independent exact-rational probes.
- All three rebuilt baseline probe systems contain 837 pivots.
- The candidates are promoted only to **depth-2-stable provisional master candidates**; this remains explicitly weaker than a global master-integral proof.
- Added `run_phase5_depth2_master_demo.bat` and checkpoint/CSV diagnostics.
- Regression status: 170 tests passed (166 regular + 4 heavy general-q raw-trace).

## v0.45.0 - crossed-ladder symmetry and raw-to-parametric bridge

- Added crossed-ladder graph-reversal integral symmetry: simultaneous `p <-> p'` and `k <-> l` maps `K <-> L`, `E1 <-> E4`, `E2 <-> E3`.
- Added `crossed_bare_scalar_parametric_representation()` and structural U/F checks, connecting the raw crossed denominator family to the generic Symanzik generator.
- Added Phase 18 raw scalar-family -> projective bridge demo.
- Added Phase 19 symmetry-reduced crossed IBP baseline and first-neighbor audit.
- Crossed corrected projector targets reduce from 95 raw monomials to 52 symmetry representatives; the bounded IBP system reduces from 760 to 416 rows at the primary probe.
- 40/52 canonical targets pivot in the bounded baseline. The remaining 12 have no pivoting first-neighbor seed at the primary exact-rational probe and are treated only as bounded local master candidates, not globally proven masters.

## v0.46.0 - crossed-ladder q-linear magnetic-projector bridge

- Added a raw crossed-ladder `p'=p+q` numerator expansion through first order in `q`.
- The automatically distributed Dirac-chain count is 144 at `q^0` and 84 at `q^1`, reproducing the independent `144+48+36=228` audit.
- Added the dedicated `q=0` five-denominator crossed family `K,L,Dk,Dkl,Dl` with powers `(1,1,1,2,1)`.
- The generic Symanzik generator now independently reproduces the hand-derived `Delta=ab-c^2`, `W=br^2-2crs+as^2`, and Feynman-parameter measure monomial `y`.
- Added the explicit denominator first-order correction `delta D = 2 x k.q + y (k+l).q`.
- Added an explicit Breit-frame Dirac-matrix/spinor check of the magnetic projector; the `F1` coefficient is exactly zero and the `F2` coefficient exactly one.
- Added `run_phase20_crossed_qlinear_bridge_demo.bat` and regression tests.
- The remaining raw-to-`P_X` gap is now isolated to loop-shifted q-linear matrix elements, streaming tensor reduction, and Gaussian recombination.

# v0.50.0

- Added exact analytic crossed-ladder U integration after the generated V partial fractions.
- Derived the U domain `0 <= U <= h-R+1` from `S>=1` and introduced the exact `Y=R+U` monomial integrator.
- Added the `(h,R) -> (t,q)` triangular bridge and regenerated `0<t<q<1` and the logarithm argument.
- Added exact t integration with an explicit lower cutoff; the `log(epsilon)` coefficient cancels identically after all sectors are combined.
- Regenerated the raw one-variable kernel in the basis `1,L,M,L^2,LM,D(q)` directly from the automatically generated `P_X` route.
- Added an automatic Horowitz-Ostrogradsky/Hermite rational reduction. The coefficients `R,T,U,V,P,Q,Z` and the simple-pole canonical remainder are now regenerated from the raw kernel rather than read from a stored table.
- Exact checks reproduce the audited total-derivative primitive and canonical crossed-ladder kernel.

## v0.51.0 - independent crossed-ladder analytic evaluation

- Replaced the crossed `q=1/2` sector's directly stored three standard-integral values by an exact derivation layer based on odd-part zeta sums and alternating Euler sums.
- Added automatic coefficient extraction from the endpoint-safe canonical kernel in the basis `L^2, L M, M^2, L, M, 1`, followed by exact cutoff integration. The finite endpoint canonical value is now regenerated rather than inserted.
- Regenerated the total-derivative endpoint boundary term directly from the automatically reconstructed Hermite primitive `G(q)`.
- The `q->1` dilogarithm series is generated by integrating the exact `D'(q)` identity with `D(1)=0`; the `q->0` asymptotic uses the real-branch dilogarithm inversion identity.
- The cubic, quadratic, and linear cutoff logarithms cancel exactly between canonical and boundary pieces.
- The crossed-ladder final coefficient is now assembled without using the stored final closed-form checkpoint; that checkpoint is used only for the final regression comparison.
- Added Phase 26 demo and five focused regression tests.

## v0.52.0 - vacuum-polarization raw-to-final and self-energy analytic closure

- Connected the parsed two-loop vacuum-polarization graph to an explicit D-dimensional transverse-tensor reduction using the scalar loop IBP identity.
- Added on-shell subtraction before the `D->4` limit; the finite logarithmic `hat(Pi)_R(k^2)` integrand is regenerated from the dimensionally regulated difference rather than inserted as a stored formula.
- Regenerated the vacuum-polarization g-2 double kernel, the elementary z-integrated kernel `H(x)`, a real-branch antiderivative, both endpoint values, and the final coefficient `119/36-pi^2/3` without using the final checkpoint as an input.
- Added Phase 27 and seven focused vacuum-polarization regression tests.
- Added an exact downstream regeneration route for the self-energy-insertion finite sector: `G_A -> b -> z -> q -> F(a) -> A_A(0)`.
- The b integration is regenerated directly from the four-parameter `G_A` through `Y=ab+q^2 z(1-a)` and monomial integration; the z stage uses derived `I0(c), I1(c)` and the q stage reproduces the audited one-variable kernel exactly.
- Added an analytic standard-integral/Euler-sum assembly of `A_A(0)=-1/24-pi^2/18` and an independent IR factorization yielding `A_B(rho)=log(rho)+1/2+o(1)`.
- The self-energy pair therefore regenerates `A_S(rho)=log(rho)+11/24-pi^2/18+o(1)` downstream of `G_A`.
- Added Phase 28 and six focused self-energy regression tests.
- The remaining self-energy automation gap is explicitly isolated to the raw left/right diagrams plus magnetic projector through generation of `G_A`; downstream analytic evaluation no longer depends on stored final kernels.

## 0.53.0

- Added a raw left/right self-energy-insertion magnetic projector bridge.
- Reconstructs the q=0 denominator family D_k^3 D_kl K L and the three distinct q-linear denominator-derivative streams.
- Performs streaming two-loop Wick/Gaussian reduction without loading the archived bare polynomial.
- Regenerates the bare Feynman-parameter integrand normalized to (alpha/pi)^2 and matches independent exact-rational checkpoints.
- Regenerates the self-energy UV sub-sector with y=tY, v=t(1-Y), x=(1-t)X, u=(1-t)(1-X), including the Y-integrated C_UV(X,rho) and rho=0 limit.
- The remaining self-energy automation gap is the renormalized finite H_A outer-loop projector bridge to G_A; the downstream G_A -> final analytic result is already automated from v0.52.

## v0.54.0 - complete self-energy raw-to-final bridge

- Added the on-shell-renormalized `Sigma_R -> H_A` outer magnetic-projector bridge.
- Regenerates the finite four-parameter kernel `G_A(a,z,b,q)` from the renormalized self-energy block rather than using the stored kernel as input.
- Uses a streaming one-loop Gaussian reducer after the effective self-energy subloop has been renormalized.
- The intermediate apparent `Gamma(0)` pieces cancel in the complete left/right pair.
- The detailed `(t,e)->(q,b)` map regenerates `G_A` exactly after the convention factor `-1/16`; the stored `G_A` is used only as a regression checkpoint.
- Added an end-to-end self-energy audit: raw pair -> UV subdivergence -> on-shell `Sigma_R` -> `H_A+H_B` -> final `A_S(rho)`.

## v0.55.0 - corner raw pair and q-linear projector foundation

- Added explicit Feynman-gauge raw LaTeX inputs for corner diagrams 4 and 5.
- Added structural recognition of the four electron propagators, the common `l`-loop inner vertex, and left/right insertion side.
- Regenerates the q=0 denominator multiplicities `D_k^2 D_kl D_l K L` and `D_k D_kl D_l^2 K L`.
- Added the common five-parameter quadratic family with `a,b,c,r,s`, `Delta`, `W`, and `Omega=W+rho^2(u+v)Delta`.
- Preserves the split parameter through q differentiation and regenerates the two diagram-specific denominator variations.
- Added explicit Breit-frame magnetic-projector numerator generation for both raw corner diagrams.
- The remaining corner gap is the two-loop Gaussian reduction plus local cancellation against the inner-vertex `B gamma_rho` subtraction before the already implemented finite sector analysis.

## v0.56.0 - corner streaming Gaussian and local UV-subtraction bridge

- Added a streaming two-loop Gaussian reduction for the corner pair using the q-linear raw projector polynomials generated in v0.55.
- Regenerates compact bare parameter kernels `G4` and `G5` without the historical monolithic Dirac/P/Q expansion.
- Includes the split-parameter denominator derivative and the common `1/(16 Delta^2)` convention/Jacobian normalization.
- Added exact-rational UV-chart audits showing both bare diagrams factorize to one half of the one-loop magnetic density.
- Added local five-simplex representatives of the `B gamma_rho` subtraction and verifies that the logarithmic UV residue of `G_bare-G_UV` is exactly zero for both diagrams.
- This local subtraction remains a UV-boundary diagnostic; it is not substituted for the physical renormalized-inner-vertex representation used by the downstream finite corner analysis.


## v0.57.0 - corner renormalized inner-vertex sector bridge
- Added an explicit three-sector representation of the on-shell-renormalized corner inner vertex.
- Closed the z-sector Feynman-parameter integral exactly to `log(Lambda_prime_sq/Lambda0_sq)`.
- Rewrote the corrected kappa-squared sector as `1/Lambda0_sq - 1/Lambda_prime_sq`.
- Added exact checks at the on-shell subtraction point and Phase 36 regression coverage.

## 0.58.0

- Added Phase 37 corner outer quadratic-form bridge.
- Generates the bulk inner denominator coefficients directly from
  `Lambda'^2 = Lambda0^2 + u^2 v(1-v) k^2 + u v(1-u) D(k)`.
- Combines photon/electron/inner denominators with `(a_p,a_d,a_l)` and regenerates
  the downstream `H`, shift coefficient, and `Q(a_d)` by square completion.
- Applies the same construction to the z-interpolated denominator and regenerates
  `H_z` and `Q_z` exactly.
- No archived `Q`/`Q_z` polynomial is used as an input; archived forms are checkpoints only.

## v0.59.0
- Added a raw one-loop corner inner-vertex bridge that derives the shifted numerator directly from the Dirac chain with x=u v, y=u(1-v).
- Verified that the inner-loop rank-two numerator coefficient is exactly gamma_nu for all four Lorentz components, so the UV pole is purely in the gamma_nu channel.
- Added the dimensionally-regulated finite on-shell difference, normalized so the logarithmic term is gamma_nu log(Lambda_prime^2/Lambda0^2), without importing the historical K_nu numerator.
- Verified the generated finite inner vertex vanishes pointwise at k=0 and that its Lambda_prime denominator matches the v0.58 outer bridge.
- Added Phase 38 validation and ZIP-producing run_v059_validation.bat.

## v0.60.0
- Connected the raw on-shell finite inner vertex directly to the right-hand outer Breit magnetic projector without using the historical long-form K_nu numerator.
- Split the finite remainder into log, 1/Lambda_prime^2, and 1/Lambda0^2 scalar streams.  The projected base/transverse term counts are 4/2, 21/15, and 6/2 respectively.
- Generated the finite-rho completed outer denominator families for the Lambda_prime, Lambda_z, and Lambda0 streams; their rho=0 limits reproduce the v0.58 H/Q and H_z/Q_z forms exactly.
- Corner regression: 40 tests pass.

## v0.61.0

- Corrected the corner inner-vertex renormalization route: the physical on-shell subtraction removes the local `B*gamma_nu` term, not the full `k=0` matrix.
- The generated physical remainder is now organized as the universal logarithm, `+C_nu(k)/(2 Lambda_prime^2)`, and the local `-2(1-u-u^2/2) gamma_nu/Lambda0^2` term.
- Added common-denominator magnetic-projector division `N_common = D Q_eff + R_odd`; every remainder monomial is transverse-odd and therefore integrates to zero.
- Fixed the exact decomposition `Lambda_prime^2-Lambda0^2 = u^2 v(1-v) K + u v(1-u) D`.
- Added pole-free compact Gaussian templates and direct physical parameter kernels without using archived `I_K`, `I_kappa^2`, or `I_z` formulas as inputs.

## v0.62.0

- Added Phase 43: an exact D-dimensional audit of the inner corner rank-two gamma channel before on-shell subtraction.
- Generated `c(D)=(D-2)^2/D` directly and verified `c(4-2 epsilon)=1-3 epsilon/2+O(epsilon^2)`.
- Combined the O(epsilon) coefficient with the normalized UV radial pole and generated the evanescent local finite shift `-3/2` exactly.
- This shift is diagnostic only and is not inserted as a fitted correction.  The physical next step is to propagate the D-dimensional local term through the B*gamma subtraction and outer magnetic projector.
- Added a soft-projective QMC development audit (not used as a regression target): the v0.61 four-dimensional-first kernel reproduces the logarithmic trend but misses the known finite normalization, motivating the D-dimensional bridge.

## v0.63.0

- Added Phase 44: exact propagation of the D-dimensional inner-radial evanescent local term through the on-shell `B gamma_nu` subtraction.
- Verified that the phase-43 local finite shift `-3/2 gamma_nu` appears identically in the bare local gamma channel and in the on-shell charge counterterm, so it cancels in the renormalized inner-vertex remainder before outer integration.
- Verified cancellation independently after the generated outer Breit projector: both base and transverse residuals are exactly zero.
- Therefore the remaining corner finite-part mismatch cannot be repaired by adding the phase-43 `-3/2` as an ad-hoc physical correction.

## 0.64.0
- Added Phase 45 operator-level reconstruction of the three-sector corner inner remainder directly from generated `C_nu`, with `K_nu^gen = C_nu/2 - 2 f(u) gamma_nu`.
- Verified all four Dirac components reproduce the physical remainder exactly before outer integration.
- Added an independent one-loop Schwinger calibration for the outer local `gamma_nu` projector/Gaussian route.
- The raw outer gamma kernel is exactly `-4` times the standard Schwinger kernel; after the existing Eq.(42) `1/4` normalization the remaining convention ratio is `-1`.
- No ad-hoc sign correction is applied in v0.64.0; the residual is exposed as a diagnostic for the next prefactor/Wick audit.


## v0.65.0

- Added Phase 46: explicit ownership of the two Feynman-gauge photon numerator signs in the sequential corner route.
- The generated raw inner chain omits the inner `-g_{alpha beta}` sign and the compact outer chain omits the remaining outer `-g_{rho sigma}` sign; their product in the full corner amplitude is `(+1)`.
- An outer-only local-gamma calibration requires the outer `-1` and then reproduces the Schwinger kernel exactly after the Eq.(42) `1/4` normalization.
- Applying only that outer sign to the full corner was explicitly rejected because it reverses the physical IR-log orientation in QMC.  The full physical parameter kernels therefore retain their v0.64 overall sign.
- This resolves the Phase-45 sign diagnostic as a sign-ownership issue rather than a full-kernel sign correction.

## v0.66.0 - exact corner log-family denominator cancellation

- Audited the finite-photon-mass scalar denominators before cancelling the `Lambda_prime-Lambda0` numerator.
- Fixed both lower-denominator log-family signs using `P=rho^2-k^2` and `E=-D(k)`.
- Added the previously omitted photon-mass residual family proportional to `rho^2/(P E^2 Lambda_z)`.
- Added an exact symbolic identity audit; no finite constant is inserted by hand.

### v0.66 Phase 48 audit
- Fixed the mirror-normalization bookkeeping: the documented alpha^2/(4 pi^4) Eq.(42) prefactor already contains the factor two from the mirror pair; no explicit second projector stream is to be added.
- Independently calibrated the physical B_gamma family pointwise against the one-loop Schwinger kernel: raw ratio 4, Eq.(42) 1/4-normalized ratio 1.
- Exposed (without yet changing) the v0.61 LP sign transition: the raw radial finite bridge contains -C/(2 Lambda') while the current physical bridge uses +C/(2 Lambda').
- Proved that the current LP quotient cannot simply be moved from the K D^2 Lambda' n=4 family to a K D Lambda' n=3 family: a nonzero Gamma(0) coefficient remains. Historical Q_K must be regenerated independently before an LP correction is accepted.


## v0.67.0 - independent historical K_nu projector regeneration

- Added `corner_historical_K_projector_audit()` as an independent transcription of the preserved on-shell `K_nu` operator; no stored `Q_K` or final finite kernel is loaded.
- Split the operator into denominator-preserving, explicit `D(k) gamma_nu`, and explicit `k^2 gamma_nu` pieces.
- Re-ran the full 4x4 outer magnetic projector including the first electron denominator q derivative.
- Regenerated the exact polynomial identity `P_K = D(k) Q_K + R_odd`.
- Regenerated the stronger archived structure `R_odd = k1*k2 * polynomial`, proving its symmetric integral vanishes.
- Phase-49 term counts are 21/14/21/4 for base/transverse/Q_K/remainder.
- Kept the independently regenerated historical `Q_K` separate from the current raw-`C_nu` LP quotient; no sign or denominator-power patch is applied by hand.
- Updated README/README_EN and REFERENCE/REFERENCE_EN with the v0.66 log-family correction, Phase-49 APIs, convention boundary, and current corner status.


## 0.68.0

- Added Phase 50 convention-resolved historical K_nu tensor-basis audit.
- Solved the projector-equivalent basis coefficients exactly as (-1, 1, 0, -1, i, 1, -1/2); the third basis is exactly projector-null.
- Verified exact agreement with K_current=C/2-2 f gamma at base, transverse, and common-numerator levels.
- Added Phase 51 exact K+kappa^2 versus LP+B rational regrouping through the Gaussian-template layer.
- Updated README/REFERENCE in Japanese and English; next corner target is direct log-sector reconstruction and soft-QMC validation.


## 0.69.0

- Added Phase 52 direct unsplit reconstruction of the corner logarithmic sector from `log(Lambda_prime^2/Lambda0^2)`.
- Added a pole-free direct `P*E^2*Lz` Gaussian template and finite-rho parameter kernel before denominator cancellation.
- Added exact generated checks for the `u^2 v(1-v)` and `uv(1-u)` delta coefficients and zero residual of the scalar split identity.
- Added two corner regression tests and the Phase 52 example/batch runner.
- Updated README/REFERENCE in Japanese and English and advanced the corner roadmap to common soft-importance QMC for direct versus split log routes.

- Added Phase 53 exact projective soft-importance maps and compact-template numerical routing for endpoint stability.
- Direct and split logarithmic routes agree within auxiliary scrambled-Sobol uncertainty when evaluated through compact templates.
- Added Phase 54 independent D-dimensional derivation of the one-loop B finite normalization, `B_fin = 2 log(rho) + 11/4 + o(1)`, and the associated `-11/8` local magnetic counterterm checkpoint.


## 0.70.0
- Phase 55: exact local finite-normalization ownership audit; the phase-54 -11/8 counterterm constant cancels against the matching bare local charge channel before outer integration.
- Phase 56: rederived one-side, mirror-pair, and physical 1/4 normalization from current Feynman-rule factors.
- Made external u du integration-measure ownership explicit for all physical corner kernels.

## 0.71.0
- Phase 57 regenerates the `a_d=u*r` joint `K+kappa^2` soft kernel and proves the exact large-r coefficient `8 v/(1-a_l)^2`.
- Added a smooth add-subtract overlap profile whose subtraction removes the complete `1/r` tail without treating its finite part as a physical correction.
- Phase 58 derives the exact simplex endpoint `r_max=(1-a_l)/u` and the associated `log(1/u)` ownership.
- Updated README and REFERENCE in Japanese and English; next target is compact finite-rho full-corner QMC with the overlap subtraction and analytic add-back on the same domain.

## 0.72.0
- Added Phase 59 exact same-domain large-r overlap add-subtract routing.
- Added Phase 60 analytic normalization of the measure-included joint soft density.
- Froze the rule that overlap subtraction must be applied to the joint soft density, not to one sequential family in isolation.
- Updated README and reference documentation in Japanese and English.


## 0.73.0
- Phase 61 analytically integrates the normalized joint soft density over the actual finite triangle and proves its cutoff tail is only O(rho log(1/rho)).
- Phase 62 fixes printed-vs-shift-consistent Eq.(28) ownership and prevents double counting of the archived shift correction in the finite-rho raw route.
- Updated README and REFERENCE in Japanese and English.


## 0.74.0
- Phase 63: exact zero ownership of the pure finite-rho matching constant.
- Archived corrected QMC values are regression-only checkpoints; rho=0.002 is compatible with zero matching within its quoted uncertainty.
- Next target: regenerate independent I_K/I_kappa^2/I_z reference kernels for pointwise comparison.


## v0.75.0

- Added Phase 64 exact numerical-measure ownership for all five generated corner parameter families.
- Added optional scrambled-Sobol finite-rho evaluator using NumPy/SciPy when available.
- The evaluator applies `u du`, family Jacobians, and the Eq. (42) `1/4` normalization exactly once.
- Reproduced the current finite-rho mismatch as a package-level diagnostic without using archived corrected values as inputs.
- Narrowed the active corner discrepancy to the rational raw-radial -> physical-remainder transition; no ad-hoc sign or finite correction was inserted.


## 0.76.0
- Added Phase 65 raw radial sign ownership audit.
- Added Phase 66 on-shell charge-condition resolution of the physical +C/(2 Lambda') sign.
- Added Phase 67 secondary-overlap-aware joint rational QMC; numerical tail sampling is excluded as the main finite mismatch.


## 0.77.0

- Added Phase 68 historical-$K$ sector projector decomposition.
- Proved exact $D(k)$ and $k^2$ factors survive the full magnetic projector in their respective sectors.
- Added Phase 69 cancellation-first family routing: preserving $n=4$, $D$-cancel $n=3$, and $k^2$-cancel $n=3$.
- Verified all post-division remainders are transverse odd.
- No physical finite correction is inserted yet; the next step is the $D=4-2\epsilon$ pole/finite audit.

- Added Phase 70 convention-resolved cancellation-first kernels and a diagnostic QMC evaluator; all five rational kernels are pole-free.

## 0.78.0

- Added Phase 71 dedicated secondary-overlap maps for all five convention-resolved cancellation-first corner rational sectors.
- Triangle sectors use `a_l=y, a_d=u*r` with logarithmic sampling of `r` on the exact bound `0 <= r <= (1-y)/u`; line sectors use the same `a_d=u*r` coordinate on `0 <= r <= 1/u`.
- Added exact Jacobian and upper-boundary audits, with no change to the physical integration domain or measure.
- Replaced single-net IID-style error estimates in this diagnostic with scatter across independently scrambled Sobol replicates.
- At power 12 with eight scrambles, the assembled `rational_minus_log` remains finite down to rho=0.002: 0.0881(29), 0.1614(17), 0.1907(25), 0.2063(31) for rho=0.02, 0.01, 0.005, 0.002 respectively.
- These values are diagnostics only; no archived finite coefficient or fitted physical correction is used as input.  The next step is to combine the stabilized rational route with the independently generated log sector and audit the full corner finite constant.

## 0.79.0
- Added Phase 72: first same-convention combination of the Phase-71 stabilized cancellation-first rational route with the independently generated Phase-52 unsplit logarithmic sector.
- Added `corner_direct_log_overlap_qmc()` using the exact Phase-53 soft bijection and independent scrambled-Sobol replicate uncertainties.
- Added `corner_phase72_full_stabilized_qmc()`; the known analytic corner constant is output-side regression metadata only and is never used to fit or modify a kernel.
- The direct-log sector is numerically stable and tends to about 0.082 as rho decreases, while the combined finite estimate remains near +0.29 rather than the analytic -0.5640209413... .
- This converts the remaining corner discrepancy from a numerical-stability problem into a kernel/sector-ownership problem. No ad-hoc finite correction is inserted.

## 0.80.0

- Added Phase 73 finite-rho cancellation / Wick-parity ownership audit.
- Phase 73 originally treated the n=4-to-n=3 Wick-parity ratio as external to the Gaussian helper; Phase 75 later shows this double-counted denominator continuation and corrects the reduced-sector signs.
- Exposes the omitted finite-rho k^2 photon-mass residual, proportional to rho^2/(rho^2-k^2), without inserting it as an ad-hoc finite correction.
- Reconfirms exact rational regrouping, direct-log split identity, and zero analytic matching constant.

## 0.81.0

- Phase 74 corrects the Phase-73 interpretation of the finite-rho `k^2` photon-mass residual.
- Proves exactly that `-rho^2/(2 P)` vanishes at fixed nonzero `k^2` but remains O(1) under the soft scaling `k^2=rho^2 chi`.
- Adds a checkpoint-free QMC comparison between the Phase-64 generated physical rational route and the Phase-71 cancellation-first route.
- No physical kernel is patched yet; the next step is to reconstruct and add the retained-photon residual family explicitly and verify route equality before taking `rho -> 0`.


## 0.82.0

- Added Phase 75 retained-photon residual reconstruction directly from the Phase-69 `k2_cancel_quotient` on the original `P D^2 Lp` family.
- Direct pre-cancellation n=4 versus reduced n=3 sector checks exposed a double-counted Wick-parity sign in Phase 70/73.
- Corrected the reduced scalar-cancellation coefficients to `D_cancel = -1` and leading `k2_cancel = +1/2`; the retained photon-mass residual remains `-1/2 * rho^2/P` on the n=4 family.
- After the correction, the cancellation-first rational route plus retained residual agrees with the independent Phase-64 `LP+B_gamma` route within the Phase-64 QMC uncertainty in the audited finite-rho points.
- The retained photon residual is numerically small in the tested range and is not the source of the earlier O(1) routing gap.
- No analytic corner finite constant is used to choose these signs; the correction is determined from route-to-route and pre/post-cancellation equality only.

## 0.83.0

- Phase 76 corrects the ownership label of the stabilized corner finite-rho route.
- The log-subtracted stabilized numerical limit is identified as the hard remainder
  `H_fin = A_C,fin - C_soft`, not the complete finite constant.
- Restores the independently derived soft finite constant exactly once:
  `C_soft = pi^2/6 + log(2)^2 - 3 log(2) - 7/4`.
- Adds an exact zero-residual audit showing `H_fin + C_soft = A_C,fin` and an
  independent equality to the closed-form checkpoint without using that checkpoint
  as a numerical input.
- Adds `corner_phase76_full_finite_qmc()` for the corrected numerical assembly.

## 0.84.0

- Adds Phase 77 end-to-end corner closure checkpoint.
- Audits the historical sector assembly and the independent soft/hard matching assembly against each other with exact symbolic residual zero.
- Includes the closed-form finite coefficient and the corner/self-energy infrared-log cancellation in the same audit.
- Adds an independent finite-rho QMC checkpoint wrapper without feeding the analytic result into the numerical kernel.
- Adds `run_v084_validation.bat` and `run_phase77_corner_end_to_end_checkpoint.bat`.

## 0.85.0

- Adds Phase 78 crossed-ladder end-to-end closure checkpoint.
- Audits the Breit magnetic projector normalization (`F1 -> 0`, `F2 -> 1`), endpoint cutoff-log cancellation, and the independently reconstructed final analytic constant in one fast exact checkpoint. The expensive raw one-variable kernel -> automatic Hermite/canonical regeneration remains available in the existing dedicated crossed-ladder phases and is deliberately excluded from release validation.
- Every modern-route closure residual is exactly zero.
- Keeps the historical Karplus--Kroll discrepancy magnitude `1/32` as a separate provenance audit target; v0.85 does not claim to locate the precise lost rational term in the 1950 algebra.
- Adds `run_phase78_crossed_end_to_end_checkpoint.bat` and `run_v085_validation.bat`.

## v0.86.0

- Added Phase 79 vacuum-polarization end-to-end closure checkpoint.
- The release audit joins exact subloop transversality, on-shell subtraction, the finite D->4 scalar kernel, the outer magnetic insertion, z integration, the generated primitive/endpoints, and the final coefficient.
- The final coefficient is independently regenerated as $119/36-\pi^2/3$ with exact zero residual.
- The heavier raw-LaTeX/topology bridge remains covered separately by the existing Phase-21 tests.

## v0.88.0

- Added Phase 81 ordinary-ladder end-to-end closure checkpoint.
- Reassembles the corrected 72-term spin-sum projector through 40 canonical IBP targets into the 12-element analytic master basis.
- Verifies the leading magnetic-projector z-pole cancellation exactly.
- Reconstructs the bare finite coefficient numerically as `107/48 + pi^2/18` to high precision without feeding that value into the master assembly.
- Applies the independent one-loop on-shell subtraction `Z1^(1) F2^(1) = -3/(4 delta) + 2 + O(delta)` and closes on the renormalized ordinary-ladder coefficient `11/48 + pi^2/18`.
- Adds `run_phase81_ordinary_ladder_end_to_end_checkpoint.bat` and `run_v088_validation.bat`.

## v0.88.2

- Fixed the Phase-81 release validator so it no longer requires `sympy` or `mpmath` merely to validate the ZIP.
- Added `examples/phase81_release_validation_stdlib.py`, which uses only the Python standard library to verify the packaged 72-row projector table, 40 canonical targets, 12 terminal bases, exact reduction-table validation flags, the saved Phase-81 closure checkpoint, the exact finite subtraction of 2, and the final numerical coefficient.
- `run_v0882_validation.bat` runs the standard-library audit first. If SymPy is installed it additionally runs the full Phase-81 extended symbolic/high-precision audit; otherwise that optional audit is explicitly skipped rather than treated as a validation failure.
- `run_v0881_validation.bat` now forwards to the corrected v0.88.2 validator.

## v0.89.0 — Phase 82: seven-diagram unified release checkpoint

- Adds a standard-library-only exact audit for all seven two-loop vertex graphs.
- Combines the five diagram classes in the exact basis {1, pi^2, zeta(3), pi^2 ln 2, ln(1/rho)}.
- Verifies corner/self-energy IR-log cancellation exactly.
- Verifies the seven-diagram sum exactly:
  A1^(4) = 197/144 + pi^2/12 + 3/4 zeta(3) - (pi^2/2) ln 2.
- Requires no SymPy/mpmath for ZIP release validation.


## v0.90.0 — Phase 83 complete two-loop regression

- Adds `data/two_loop_v090_baseline.json`, the durable exact baseline for all seven two-loop vertex diagrams in the basis `{1, pi^2, zeta(3), pi^2 ln 2, ln(1/rho)}`.
- Adds `examples/phase83_two_loop_completion_regression_stdlib.py`, which validates the complete two-loop release without importing SymPy, mpmath, NumPy, or QEDCalc itself.
- The release regression verifies Phase 77–82 provenance, the ordinary-ladder `72 -> 40 -> 12` reduction invariants, exact corner/self-energy IR cancellation, diagram count 7, and the final exact coefficient.
- Adds an optional scientific regression that reruns the exact corner, crossed-ladder, vacuum-polarization, and self-energy analytic checkpoints when SymPy is available.
- Keeps the historical crossed-ladder Karplus--Kroll `1/32` discrepancy explicitly separate: the modern crossed-ladder value is closed, while the precise location of the lost 1950 rational term remains unresolved.
