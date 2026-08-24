# QEDCalc ROADMAP

## Current: v0.44.0

Completed foundations:

- project-level `conventions.txt` with typed validation and no interactive prompt
- convention-driven subdiagram normalization ownership and dim-reg scheme selection

- QED-LaTeX input and symbol validation
- Dirac / Lorentz algebra used by the one-loop workflow
- one-loop Feynman parameterization and square completion
- one-loop magnetic projector through $F_2(0)=\alpha/(2\pi)$
- multiple loop momenta
- matrix square completion for multi-loop quadratic forms
- simultaneous multi-loop numerator shifts
- general even-rank symmetric tensor reduction
- N-denominator unit-power Feynman parameterization
- positive-integer denominator powers
- general-$D$ Euclidean scalar loop integral formula
- $D=4-2\epsilon$ Laurent series helper
- UV/IR pole representation and independent UV/IR/mixed bookkeeping
- explicit counterterm definition/replacement/insertion and standard QED counterterm library
- explicit subdiagram relations and compatible Zimmermann forests
- contracted graph topology $G/F$
- multivariate Taylor subtraction and local BPHZ counterterms
- topology-driven forest-sum assembly with explicit amplitude providers
- explicit ordered topology-to-amplitude templates and safe local-vertex contraction
- mixed multi-loop tensor reduction using the inverse quadratic matrix
- crossed-ladder projective/one-variable analytic reduction and endpoint cancellation
- corner (IIc) soft/hard/z-sector analytic bookkeeping and IR cancellation
- raw bare two-loop vacuum-polarization trace discovery
- raw bare two-loop self-energy-insertion detection and S Sigma S contraction
- raw ordinary-ladder symbolic-D parsing, seven-denominator family detection, and q=0 numerator generation
- raw general-q ordinary-ladder historical 75-term audit-table regeneration (75/75 exact)
- corrected spin-sum general-q trace route kept separate from the historical audit table
- generic IBP identity generation for multi-loop denominator families
- finite sparse symbolic Laporta elimination core
- ordinary-ladder seven-denominator IBP bridge
- sector signatures and first-neighbor seed generation
- full corrected ordinary-ladder closure: 40 canonical targets -> 12 terminal basis integrals
- exact symbolic reconstruction of all 151 nonzero $c_{ia}(D,z)$ coefficients
- 91-point grid plus three independent exact-rational holdouts for every nonzero ordinary-ladder coefficient
- denominator-guided tensor-grid rational reconstruction helpers

## Next priorities

1. Evaluate / register the 12 ordinary-ladder terminal basis integrals analytically, including the three factorized lower sectors.
2. Combine the symbolic $c_{ia}(D,z)$ table with basis-integral expansions and the Pauli projector limit to reproduce the ordinary-ladder finite coefficient without the historical reduction checkpoint.
3. Generate crossed-ladder raw Dirac/projector scalar-integral families using the reusable ordinary-ladder trace/IBP infrastructure.
4. Generate corner / IIc raw projector and counterterm kernels from the original graph expressions.
5. Complete the remaining vacuum-polarization raw insertion bridge $\Pi^{\mu\nu}\to\Pi_R\to$ outer vertex.
6. Build the full seven-diagram two-loop orchestrator with UV/IR and counterterm bookkeeping.
7. Add master-integral numerical fallback / sector-decomposition interfaces for future three- and four-loop work.

## Later

- complete Laporta seed closure and master reduction
- master-integral interfaces
- sector decomposition / numerical fallback
- diagram-level reusable pipelines for the complete two-loop vertex set
- generalized three-loop and four-loop workflows

The design goal remains modular: no hard-coded final-result routine should replace transparent intermediate operations.


## After v0.16.0

- Run the first real two-loop diagram end-to-end.
- Add richer graph templates for branching/non-contiguous topologies.
- Extend reusable pipelines toward the full two-loop vertex set.
- Add denominator-family and IBP-oriented representations.

- v0.17.0: self-energy insertion trial reproduces the on-shell-renormalized finite/IR coefficient.
- Next: vertex-subloop or ladder two-loop trial; add missing generalized propagator-power/projector routines as required.

## After v0.21.0

- Reconstruct the transverse vacuum-polarization tensor directly from the reduced raw trace.
- Apply on-shell subtraction directly to the raw VP subdiagram object.
- Replace the raw DiracTrace node in the outer two-loop diagram with the renormalized transverse insertion.
- Extend the same bare-diagram path to self-energy insertion graphs.


## After v0.22.0

- Reconstruct the full general-covariant-gauge self-energy subloop, including the longitudinal photon part.
- Derive the on-shell $A(r^2),B(r^2)$ decomposition directly from the raw detected subdiagram.
- Extend raw two-loop parsing/subdiagram extraction to ordinary ladder, crossed ladder, and corner projector pipelines.


## After v0.25.0

- Implement arbitrary-length $D$-dimensional Clifford traces suitable for the ordinary-ladder projector.
- Generate the 75-term ladder coefficient table directly from the raw graph instead of loading it as validation data.
- Add an IBP equation generator and a conservative Laporta-style reduction layer.


## After v0.25.0

- Generate the general-q^2 ordinary-ladder 75-term table from the raw projector trace.
- Add a reusable IBP equation generator and Laporta-style reducer.
- Reuse the arbitrary-length D-dimensional trace engine for crossed-ladder/corner raw bridges and future 3/4-loop work.


## After v0.26.0

- Implement a reusable IBP equation generator and conservative Laporta-style reducer.
- Connect the corrected spin-sum general-$q^2$ trace to the audited finite-limit $A_0/C_1$ workflow without using the historical 75-table as a physical shortcut.
- Reuse the optimized long-trace engine for raw crossed-ladder and corner projector kernels.
- Continue toward three-loop and four-loop reusable denominator families.


## After v0.27.0

- Add sector ordering and scaleless/zero-sector detection.
- Add iterative seed expansion with closure criteria.
- Optimize rational-function coefficient arithmetic for 50-500 equation systems.
- Reduce the ordinary-ladder generated integral tables toward a stable master basis.
- Reuse the same IBP engine for crossed ladder and corner families.

- Extend v0.31 exact rational reconstruction to all corrected ladder targets with adaptive degree selection, pole-safe sample scheduling, and finite-field/modular acceleration.

### After v0.32.0

- Add sector/residue-priority closure scheduling. Do not expand every terminal residue neighborhood simultaneously.
- Track which unresolved residue blocks each target reconstruction and expand only the highest-priority sectors needed by the corrected 40-target set.
- Re-run batch reconstruction after each scheduled closure layer until the number of residue-bearing targets decreases or a stable residual basis is proven.


### After v0.33.0

- Recompute terminal residues on the 114-seed corrected ordinary-ladder system.
- Expand only one high-priority residue sector neighborhood at a time under a strict new-seed budget.
- Measure marginal pivot gain and target-closure gain after each scheduled batch.
- Continue until residue-bearing targets stabilize, then resume full symbolic coefficient reconstruction.

## After v0.34.0

- Apply the selected phase-2 seed batch and recompute the true recursive target residues.
- Add timeout/complexity guards for expensive residue recursion.
- Continue sector-by-sector closure only when marginal improvement is positive.


## After v0.36.0

- Rebuild the residue scheduler on the three remaining genuine terminal residue kinds after removing factorized lower subtopologies.
- Add a lower-sector master registry so factorized one-loop products and scaleless free-loop sectors are automatically treated as known terminal objects during recursive reduction.
- Resume symbolic coefficient reconstruction for the 18 still residue-bearing corrected targets.


### v0.36.0 next focus

- independently validate whether the three provisional local master candidates are genuine masters using a wider seed domain or an independent reduction/master-count argument
- once the master basis is validated, reconstruct the remaining corrected ordinary-ladder target coefficients in that basis
- then port the mature raw-trace/IBP/Laporta stack to crossed ladder and corner raw bridges


### v0.37.0 next focus

- Validate the three depth-2-stable provisional ordinary-ladder master candidates with a broader but scheduled degree-2 domain rather than an all-at-once Cartesian expansion.
- Add independent master-count diagnostics and, where practical, comparison hooks for external IBP reductions.
- Once the basis is sufficiently stable, reconstruct corrected-target reduction coefficients against the enlarged provisional basis.


- [x] Exhaust the primary-probe bounded full degree-2 Cartesian neighborhood for the three ordinary-ladder provisional candidates (v0.38).
- [x] Add portable exact-rational Laporta-rule checkpoints (v0.38).
- [ ] Repeat the mixed degree-2 audit at independent probes and/or with an independent reduction backend.


- Completed the three-probe full degree-2 bounded audit for the three ordinary-ladder provisional master candidates. Next: independent/global master-count validation or wider bounded domains before promoting candidates to proven masters.


## v0.40.0 status
- Full bounded degree-3 audit completed for the three provisional ordinary-ladder master candidates at three independent exact-rational probes.
- Next: independent master-count validation and symbolic reductions onto the expanded provisional basis.


## v0.42.0 status
- [x] Generate U/F/Delta projective representations for all 12 ordinary-ladder terminal basis integrals.
- [x] Evaluate 9 of 12 basis integrals analytically at z=0 in Gamma functions.
- [x] Evaluate the former z=0 masters basis 8, 10, 11; v0.43 reduces them to a single T-family and closes T1 analytically.
- [ ] Combine the 12-basis symbolic reduction with the z=0 master values and epsilon expansions to regenerate the ordinary-ladder finite coefficient without the old final checkpoint.


## v0.43.0 status

- [x] Reduce basis 8, 10, 11 to the z=0 $T_n$ family.
- [x] Symbolically reduce $T_2,T_3$ with the dedicated five-denominator IBP family.
- [x] Evaluate all lower sectors analytically or as scaleless zero sectors.
- [x] Evaluate $T_1$ by Cheng--Wu reduction and Gauss summation.
- [x] Achieve 12/12 analytic terminal basis values at $z=0$.
- [ ] Combine the 40-target symbolic reduction matrix with the 12 exact basis values and reproduce the bare/subtracted ordinary-ladder coefficient without the old final checkpoint.


## v0.44.0 status

- [x] Compose the corrected 72 raw projector monomials with the 40-target x 12-basis exact symbolic reduction.
- [x] Verify absence of a surviving `1/z^2` projector pole.
- [x] Verify exact cancellation of the complete leading `1/z` coefficient after the z=0 basis relations are inserted.
- [x] Identify the finite-limit derivative sector: only basis 0, 1, 3, 5, 6, 7, 8 require `dI/dz|_{z=0}`.
- [ ] Derive the seven first-z-derivative integrals from the projective representation and reduce them at z=0.
- [ ] Combine derivative contributions, regular coefficient parts, and epsilon expansions to regenerate the bare/subtracted ordinary-ladder coefficient without the historical final checkpoint.


## v0.55.0 progress note

Self-energy insertion is now closed from the raw two diagrams through on-shell renormalization to the final analytic result. Corner (IIc) now has a raw two-diagram parser/topology bridge, q=0 five-parameter denominator family, split-parameter q derivatives, and explicit q-linear magnetic projector generation. The next corner stage is the Gaussian/subtraction bridge to the existing UV-finite parameter representation.

## v0.56.0 progress note

Corner (IIc) is now connected from the raw two diagrams through the q-linear magnetic projector and streaming two-loop Gaussian integration to the bare five-simplex kernels. The one-loop vertex UV boundary is automatically factorized and cancelled by a local `B gamma_rho` subtraction representative. The next stage is to generate the physical renormalized inner-vertex remainder sectors (`K`, `m^2/kappa^2`, and `z`) and insert them into the outer one-loop magnetic projector, thereby connecting the raw route to the existing UV-finite physical parameter representation.


## v0.57.0 progress note
The corner inner-vertex physical renormalization layer is now separated from the local UV diagnostic layer. Next: reconstruct `Lambda_prime_sq` and `K_nu` directly in outer-loop variables and feed the three sectors through the outer magnetic projector.

## v0.62 next corner step

Phase 43 isolates a finite evanescent term lost when the UV-divergent inner radial gamma channel is reduced with strictly four-dimensional Dirac algebra before the epsilon expansion.  Next, carry this D-dimensional local term through the on-shell B*gamma subtraction and outer Breit projector, then rerun the soft-projective QMC.  Do not tune the final constant to the Petermann checkpoint.

### v0.63 status

Phase 44 closes the evanescent-local-term question: the `-3/2 gamma_nu` inner UV-local finite term cancels exactly against the same contribution in the on-shell `B gamma_nu` subtraction, including after the outer Breit projector. The remaining corner task is now narrowed to the nonlocal finite operator/kernel assembly (especially the generated `C_nu/Lambda'^2` to physical Eq.-32 remainder mapping), not dimensional local renormalization.

- v0.64 Phase 45: Eq.(32) operator reconstruction PASS; Schwinger calibration isolates an outer overall-sign convention residual. Next: derive that sign from the raw Feynman prefactor/Wick rotation and propagate the corrected convention through the finite corner QMC.


## v0.67 next corner step

Phase 49 independently regenerates the preserved historical `K_nu` full-chain projector and its exact `P_K=D Q_K+R_odd` structure. Next, compare the historical `Q_K` route with the raw-`C_nu` LP route at operator level, splitting denominator-preserving, explicit `D(k) gamma_nu`, and explicit `k^2 gamma_nu` sectors before any Gaussian-family reassignment. Do not identify the two quotients by denominator power alone.


## v0.68 next corner step

Phase 50 resolves the Karplus--Kroll/current K_nu convention at projector level, and Phase 51 proves exact equivalence of the historical K+kappa^2 regrouping and the current LP+B_gamma rational route through the Gaussian-template layer. The rational sector is therefore removed from the active finite-part discrepancy suspects. Next: regenerate the log sector directly from log(Lambda_prime^2/Lambda0^2) before denominator cancellation, compare it against the v0.66 split families including the photon-mass residual, and then rerun finite-rho soft-importance QMC.


## v0.69 next corner step

Phase 52 now regenerates the log sector before denominator cancellation and produces a pole-free direct finite-rho parameter kernel.  The exact scalar identity linking that route to the v0.66 photon-cancel, electron-cancel, and photon-mass-residual families is zero.  Next: implement one common soft-importance mapping for both the direct and split log routes, verify their numerical equality within statistical uncertainty for decreasing rho, then apply the same mapping to the complete corner kernel and re-test the finite constant.


Phase 53 removes the expanded-kernel endpoint instability by combining a projective soft map with compact Gaussian templates, and the direct/split log routes agree numerically within QMC uncertainty. Phase 54 independently derives the local one-loop subtraction checkpoint `B_fin = 2 log(rho) + 11/4 + o(1)`, implying `-11/8` after the one-loop magnetic factor. Next: audit ownership of this local finite normalization in the current Eq. (32) sequential remainder; do not add the constant by hand.


### After v0.70.0
- Resolve the non-uniform soft overlap (including the a_d=u r large-r overlap) with sector-aware compact-template QMC.
- Require stable full-corner convergence before returning to analytic endpoint integration.

## v0.71 next corner step

Phases 57--58 isolate the non-uniform `a_d=u*r` large-r overlap and attach it to the exact simplex cutoff.  Next, construct the same add-subtract pair from the finite-rho compact physical kernel, integrate the subtracted kernel numerically, add back the overlap analytically on the identical domain, and require stable `rho -> 0` convergence before any final corner claim.

## v0.72 next corner step

Phases 59--60 now fix the same-domain overlap identity and the normalized joint soft density. Next, construct the finite-rho joint compact density from the current physical sectors before family separation, apply the Phase-59 subtraction to that combined density, and rerun the controlled rho->0 QMC convergence audit.


### v0.73 next corner target
Primary finite-soft-triangle truncation and Eq.(28) shift ownership are now excluded as sources of the order-one mismatch. Continue with the secondary large-r overlap / finite-rho matching difference on a common domain, without re-adding the shift correction.


### v0.74 next corner target
Regenerate the independent corrected finite-parameter reference kernels I_K, I_kappa^2 and I_z from the archived derivation, then compare them pointwise against the raw-generated physical kernels. Do not add any extra matching constant: Phase 63 proves its analytic value is zero.


### v0.75 next corner target
Use the Phase-64 reproducible evaluator while independently auditing the raw-radial to physical on-shell rational-remainder sign, including the complete inner photon/prefactor/Wick convention. Do not choose the sign by matching the Petermann constant. Once fixed independently, rerun the same Phase-64 evaluator and require convergence to the zero-matching condition.


## After v0.76.0
- Factorize the exact difference between the independently regenerated historical Q_K and the current lp_quotient.
- Trace the differing polynomial sectors back to projector/denominator assembly before changing any physical kernel.


## v0.77 next corner step

Keep the Phase-69 $n=3$ cancellation sectors in $D=4-2\epsilon$, combine their pole and finite pieces with the preserving and $\kappa^2$ rational sectors, and compare the resulting finite kernel against the current all-in-one $n=4$ route.

- Build a sector-specific soft / secondary-overlap map for the five Phase-70 cancellation-first rational kernels before taking smaller-rho QMC values as physical diagnostics.

## v0.83.0 Phase 76 status

- Corrected the ownership label of the stabilized corner finite-rho route.
- Exact identity `H_fin + C_soft = A_C,fin` is now regression-tested.
- Next: improve the numerical extrapolation/variance so the rho->0 approach resolves the analytic constant with tighter uncertainty, then propagate the same ownership discipline to the remaining two-loop graph routes.

## v0.88 / Phase 81

ordinary ladder release checkpoint completed: corrected projector 72 terms -> 40 canonical IBP targets -> 12 analytic masters -> bare finite coefficient -> on-shell subtraction -> renormalized coefficient. Next target is a unified multi-diagram two-loop release audit across every completed diagram class.


## v0.90.0 milestone — two-loop release baseline complete

Phase 83 freezes the completed two-loop result as a durable regression baseline. All seven diagrams are represented by release checkpoints, the total transcendental-basis sum is exact, and corner/self-energy IR cancellation is exact. Future development can proceed to higher-loop automation while `run_v090_validation.bat` protects the two-loop baseline.

Remaining historical-only item: locate the precise source of the crossed-ladder Karplus--Kroll `1/32` discrepancy in the 1950 algebra. This does not block or alter the modern two-loop coefficient.
