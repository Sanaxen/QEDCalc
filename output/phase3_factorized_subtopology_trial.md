# QEDCalc phase-3 factorized lower-subtopology trial

## 1. Recursive check of the v0.34 phase-2 pair

Phase-1 pivots: **823**.

After inserting the two selected phase-2 seeds: **837** pivots.

Residue-bearing corrected targets after actual recursive reduction: **27**.

The direct-pivot scheduling metric did not by itself close these targets; the high-power residues descended to simpler lower-sector integrals.

## 2. Factorized lower sectors

Factorized terminal residues recognized: **3**.

- `(0, 0, 0, 0, 0, 1, 1)` -> denominators `('E3', 'E4')`, powers `(1, 1)`, loop-direction determinant `-1`, unimodular = **True**.
  Convention-free Euclidean product: `$\pi^{D} m_{2}^{D - 2} \Gamma^{2}\left(1 - \frac{D}{2}\right)$`.
- `(0, 0, 0, 0, 1, 0, 1)` -> denominators `('E2', 'E4')`, powers `(1, 1)`, loop-direction determinant `-1`, unimodular = **True**.
  Convention-free Euclidean product: `$\pi^{D} m_{2}^{D - 2} \Gamma^{2}\left(1 - \frac{D}{2}\right)$`.
- `(0, 0, 0, 0, 2, 0, 3)` -> denominators `('E2', 'E4')`, powers `(2, 3)`, loop-direction determinant `-1`, unimodular = **True**.
  Convention-free Euclidean product: `$\frac{\pi^{D} m_{2}^{D - 5} \Gamma\left(2 - \frac{D}{2}\right) \Gamma\left(3 - \frac{D}{2}\right)}{2}$`.

These are not promoted to new genuine two-loop masters. They are known lower-subtopology products of one-loop massive tadpoles after an invertible loop-momentum change of variables.

## 3. Closure after recognizing the lower sectors

Residue-bearing corrected targets: **27 -> 18**.

Remaining terminal residue kinds: **3**.

- `(0, 1, 0, 0, 1, 0, 2)` blocks **18** target(s).
- `(0, 1, 1, 1, 0, 1, 1)` blocks **6** target(s).
- `(0, 1, 1, 1, 1, 0, 2)` blocks **6** target(s).

## 4. Extended zero-sector diagnostic

`(0, 0, 0, 0, 0, 0, 2)` is classified as zero by the extended diagnostic because one of the two loop directions is completely unconstrained by positive denominators: **True**.

CSV: `output/ladder_phase3_factorized_lower_sectors.csv`
