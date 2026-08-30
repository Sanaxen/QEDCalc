# Phase 13: ordinary-ladder basis z-derivative reduction

The phase-12 projector audit shows derivative weights only for basis 0, 1, 3, 5, 6, 7, and 8. This phase checks which of those derivatives are actually nonzero and closes all required analytic sectors, including basis 8 through a D+2 dimensional shift followed by z=0 IBP reduction.

## Basis 0: `(0, 0, 0, 0, 0, 1, 1)`

Status: **exact**. Method: `z_independent_factorized_lower`.

$$
0
$$

## Basis 1: `(0, 0, 0, 0, 1, 0, 1)`

Status: **exact**. Method: `z_independent_factorized_lower`.

$$
0
$$

## Basis 3: `(0, 0, 0, 0, 2, 0, 3)`

Status: **exact**. Method: `z_independent_factorized_lower`.

$$
0
$$

## Basis 5: `(0, 1, 0, 0, 1, 0, 1)`

Status: **exact**. Method: `three_denominator_projective_beta`.

$$
\frac{4 \pi^{D} \Gamma^{2}\left(3 - \frac{D}{2}\right)}{D \left(D - 5\right) \left(D - 4\right) \left(D - 2\right)}
$$

## Basis 6: `(0, 1, 0, 0, 1, 0, 2)`

Status: **exact**. Method: `three_denominator_projective_beta`.

$$
\frac{4 \pi^{D} \Gamma\left(3 - \frac{D}{2}\right) \Gamma\left(4 - \frac{D}{2}\right)}{D \left(D - 6\right) \left(D - 5\right) \left(D - 2\right)}
$$

## Basis 7: `(0, 1, 1, 0, 0, 0, 1)`

Status: **exact**. Method: `z_independent_projective_F`.

$$
0
$$

## Basis 8: `(0, 1, 1, 0, 1, 0, 1)`

Status: **exact**. Method: `dimension_shift_Dplus2_then_z0_IBP`.

$$
- \frac{\pi^{D} \left(D - 2\right) \left(19 D^{5} \Gamma^{2}\left(\frac{D}{2}\right) \Gamma\left(D\right) \Gamma\left(2 - D\right) \Gamma\left(2 - \frac{D}{2}\right) \Gamma\left(\frac{D}{2} - 1\right) \Gamma\left(\frac{3 D}{2} - 2\right) \Gamma\left(2 D - 3\right) - 246 D^{4} \Gamma^{2}\left(\frac{D}{2}\right) \Gamma\left(D\right) \Gamma\left(2 - D\right) \Gamma\left(2 - \frac{D}{2}\right) \Gamma\left(\frac{D}{2} - 1\right) \Gamma\left(\frac{3 D}{2} - 2\right) \Gamma\left(2 D - 3\right) + 18 D^{4} \Gamma^{2}\left(\frac{D}{2}\right) \Gamma\left(D\right) \Gamma\left(2 - \frac{D}{2}\right) \Gamma\left(3 - D\right) \Gamma\left(\frac{D}{2} - 1\right) \Gamma\left(\frac{3 D}{2} - 1\right) \Gamma\left(2 D - 4\right) - 8 D^{4} \Gamma^{2}\left(\frac{D}{2}\right) \Gamma\left(1 - \frac{D}{2}\right) \Gamma\left(2 - D\right) \Gamma\left(\frac{D}{2} + 1\right) \Gamma\left(D - 1\right) \Gamma\left(\frac{3 D}{2} - 2\right) \Gamma\left(2 D - 2\right) + 8 D^{4} \Gamma^{2}\left(1 - \frac{D}{2}\right) \Gamma\left(\frac{D}{2} + 1\right) \Gamma^{2}\left(D - 1\right) \Gamma\left(\frac{3 D}{2} - 2\right) \Gamma\left(\frac{3 D}{2} - 1\right) + 1143 D^{3} \Gamma^{2}\left(\frac{D}{2}\right) \Gamma\left(D\right) \Gamma\left(2 - D\right) \Gamma\left(2 - \frac{D}{2}\right) \Gamma\left(\frac{D}{2} - 1\right) \Gamma\left(\frac{3 D}{2} - 2\right) \Gamma\left(2 D - 3\right) - 194 D^{3} \Gamma^{2}\left(\frac{D}{2}\right) \Gamma\left(D\right) \Gamma\left(2 - \frac{D}{2}\right) \Gamma\left(3 - D\right) \Gamma\left(\frac{D}{2} - 1\right) \Gamma\left(\frac{3 D}{2} - 1\right) \Gamma\left(2 D - 4\right) + 116 D^{3} \Gamma^{2}\left(\frac{D}{2}\right) \Gamma\left(1 - \frac{D}{2}\right) \Gamma\left(2 - D\right) \Gamma\left(\frac{D}{2} + 1\right) \Gamma\left(D - 1\right) \Gamma\left(\frac{3 D}{2} - 2\right) \Gamma\left(2 D - 2\right) - 116 D^{3} \Gamma^{2}\left(1 - \frac{D}{2}\right) \Gamma\left(\frac{D}{2} + 1\right) \Gamma^{2}\left(D - 1\right) \Gamma\left(\frac{3 D}{2} - 2\right) \Gamma\left(\frac{3 D}{2} - 1\right) - 2256 D^{2} \Gamma^{2}\left(\frac{D}{2}\right) \Gamma\left(D\right) \Gamma\left(2 - D\right) \Gamma\left(2 - \frac{D}{2}\right) \Gamma\left(\frac{D}{2} - 1\right) \Gamma\left(\frac{3 D}{2} - 2\right) \Gamma\left(2 D - 3\right) + 676 D^{2} \Gamma^{2}\left(\frac{D}{2}\right) \Gamma\left(D\right) \Gamma\left(2 - \frac{D}{2}\right) \Gamma\left(3 - D\right) \Gamma\left(\frac{D}{2} - 1\right) \Gamma\left(\frac{3 D}{2} - 1\right) \Gamma\left(2 D - 4\right) - 632 D^{2} \Gamma^{2}\left(\frac{D}{2}\right) \Gamma\left(1 - \frac{D}{2}\right) \Gamma\left(2 - D\right) \Gamma\left(\frac{D}{2} + 1\right) \Gamma\left(D - 1\right) \Gamma\left(\frac{3 D}{2} - 2\right) \Gamma\left(2 D - 2\right) + 632 D^{2} \Gamma^{2}\left(1 - \frac{D}{2}\right) \Gamma\left(\frac{D}{2} + 1\right) \Gamma^{2}\left(D - 1\right) \Gamma\left(\frac{3 D}{2} - 2\right) \Gamma\left(\frac{3 D}{2} - 1\right) + 1600 D \Gamma^{2}\left(\frac{D}{2}\right) \Gamma\left(D\right) \Gamma\left(2 - D\right) \Gamma\left(2 - \frac{D}{2}\right) \Gamma\left(\frac{D}{2} - 1\right) \Gamma\left(\frac{3 D}{2} - 2\right) \Gamma\left(2 D - 3\right) - 760 D \Gamma^{2}\left(\frac{D}{2}\right) \Gamma\left(D\right) \Gamma\left(2 - \frac{D}{2}\right) \Gamma\left(3 - D\right) \Gamma\left(\frac{D}{2} - 1\right) \Gamma\left(\frac{3 D}{2} - 1\right) \Gamma\left(2 D - 4\right) + 1524 D \Gamma^{2}\left(\frac{D}{2}\right) \Gamma\left(1 - \frac{D}{2}\right) \Gamma\left(2 - D\right) \Gamma\left(\frac{D}{2} + 1\right) \Gamma\left(D - 1\right) \Gamma\left(\frac{3 D}{2} - 2\right) \Gamma\left(2 D - 2\right) - 1524 D \Gamma^{2}\left(1 - \frac{D}{2}\right) \Gamma\left(\frac{D}{2} + 1\right) \Gamma^{2}\left(D - 1\right) \Gamma\left(\frac{3 D}{2} - 2\right) \Gamma\left(\frac{3 D}{2} - 1\right) - 1360 \Gamma^{2}\left(\frac{D}{2}\right) \Gamma\left(1 - \frac{D}{2}\right) \Gamma\left(2 - D\right) \Gamma\left(\frac{D}{2} + 1\right) \Gamma\left(D - 1\right) \Gamma\left(\frac{3 D}{2} - 2\right) \Gamma\left(2 D - 2\right) + 1360 \Gamma^{2}\left(1 - \frac{D}{2}\right) \Gamma\left(\frac{D}{2} + 1\right) \Gamma^{2}\left(D - 1\right) \Gamma\left(\frac{3 D}{2} - 2\right) \Gamma\left(\frac{3 D}{2} - 1\right)\right)}{16 D \left(D - 5\right) \left(D - 4\right) \left(D - 3\right) \left(2 D - 5\right) \Gamma\left(\frac{D}{2}\right) \Gamma\left(D\right) \Gamma\left(D - 1\right) \Gamma\left(\frac{3 D}{2} - 2\right) \Gamma\left(\frac{3 D}{2} - 1\right)}
$$

## Result

- Basis 0, 1, 3: derivative is exactly zero because the factorized lower-sector value is z-independent.
- Basis 7: derivative is exactly zero because its projective F polynomial contains no z.
- Basis 5 and 6: first derivatives are analytic Gamma-function expressions.
- Basis 8: the derivative is mapped to a D+2 shifted scalar integral and reduced by z=0 IBP to T1 plus known lower sectors.
- Remaining unresolved required first-z derivatives: **0**.
