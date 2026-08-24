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
