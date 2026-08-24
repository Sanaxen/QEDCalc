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
