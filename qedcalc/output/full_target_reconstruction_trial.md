# QEDCalc full corrected-target reconstruction trial

## 1. Purpose

This trial applies exact-rational symbolic coefficient reconstruction to every symmetry-canonical target of the corrected ordinary-ladder projector route.

A target is reconstructed only if recursive Laporta reduction closes entirely on the six stable candidate integrals at every probe point. Targets leaving any non-candidate residue are explicitly skipped rather than interpolated.

## 2. Domain

Corrected raw monomials: **72**.

Symmetry-canonical targets: **40**.

Stable candidate basis elements: **6**.

Final closure seeds: **84**.

Symbolic IBP rows: **666**.

Valid exact-rational sample points: **16** = 12 training + 4 holdout.

## 3. Candidate basis

$M_1$:

$$
J\left(0,0,0,0,1,1,1\right)
$$

$M_2$:

$$
J\left(0,0,0,1,1,1,1\right)
$$

$M_3$:

$$
J\left(0,1,0,0,1,0,1\right)
$$

$M_4$:

$$
J\left(0,1,1,0,0,0,1\right)
$$

$M_5$:

$$
J\left(0,1,1,0,1,0,1\right)
$$

$M_6$:

$$
J\left(0,1,1,1,0,0,1\right)
$$

## 4. Batch result

Candidate-basis targets: **6**.

Non-master targets reconstructed and holdout-validated: **6**.

Targets still containing non-candidate IBP residues: **28**.

Closed targets whose rational ansatz still failed: **0**.

## 5. Reconstructed targets

Target:

$$
J\left(-1,0,0,1,1,1,1\right)
$$

$$
J\left(-1,0,0,1,1,1,1\right)=\left(1\right)M_{1}+\left(\frac{z - 4}{2}\right)M_{2}
$$

Target:

$$
J\left(0,0,1,1,0,1,1\right)
$$

$$
J\left(0,0,1,1,0,1,1\right)=\left(- \frac{D - 2}{2 \left(D - 3\right)}\right)M_{1}
$$

Target:

$$
J\left(0,0,1,1,1,1,1\right)
$$

$$
J\left(0,0,1,1,1,1,1\right)=\left(\frac{D - 2}{\left(D - 4\right) \left(z - 4\right)}\right)M_{1}+\left(\frac{2 \left(D - 3\right)}{\left(D - 4\right) \left(z - 4\right)}\right)M_{2}
$$

Target:

$$
J\left(0,1,0,0,1,1,0\right)
$$

The target reduces identically to zero in the current IBP system.

Target:

$$
J\left(0,1,1,0,0,1,0\right)
$$

The target reduces identically to zero in the current IBP system.

Target:

$$
J\left(0,1,1,0,1,1,0\right)
$$

The target reduces identically to zero in the current IBP system.

## 6. Residue diagnostic

The residual targets demonstrate that pivot membership is weaker than full basis closure. Their recursive reductions terminate on additional non-candidate integrals, so coefficient reconstruction is intentionally not attempted for them.

Target:

$$
J\left(-2,1,1,1,0,1,1\right)
$$

Non-candidate residues in sampled reductions: **32**.

Target:

$$
J\left(-2,1,1,1,1,1,1\right)
$$

Non-candidate residues in sampled reductions: **30**.

Target:

$$
J\left(-1,0,1,1,0,1,1\right)
$$

Non-candidate residues in sampled reductions: **2**.

Target:

$$
J\left(-1,0,1,1,1,1,1\right)
$$

Non-candidate residues in sampled reductions: **2**.

Target:

$$
J\left(-1,1,0,0,1,1,1\right)
$$

Non-candidate residues in sampled reductions: **2**.

Target:

$$
J\left(-1,1,0,1,0,1,1\right)
$$

Non-candidate residues in sampled reductions: **2**.

Target:

$$
J\left(-1,1,0,1,1,1,1\right)
$$

Non-candidate residues in sampled reductions: **2**.

Target:

$$
J\left(-1,1,1,0,0,1,1\right)
$$

Non-candidate residues in sampled reductions: **1**.

Target:

$$
J\left(-1,1,1,0,1,0,1\right)
$$

Non-candidate residues in sampled reductions: **1**.

Target:

$$
J\left(-1,1,1,0,1,1,1\right)
$$

Non-candidate residues in sampled reductions: **2**.

(Only the first ten residue-bearing targets are printed here; the CSV contains the complete status table.)

## 7. Interpretation

The corrected 40-target set is therefore not yet symbolically closed on the six candidate integrals, even though many targets appear as Laporta pivots. The next required step is residue-aware seed closure: collect the actual terminal non-candidate integrals from recursive target reductions, add only their canonical neighborhoods, and repeat until the target reductions themselves close or the residual set stabilizes.

Status CSV: `output/ladder_corrected_target_reconstruction_status.csv`

Reconstructed coefficient CSV: `output/ladder_corrected_reconstructed_coefficients.csv`
