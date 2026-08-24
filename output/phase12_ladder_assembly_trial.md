# Phase 12: ordinary-ladder projector/reduction assembly

The corrected 72 raw projector monomials are first canonicalized under the ordinary-ladder graph symmetries and then composed with the exact 40-target x 12-basis symbolic IBP matrix.

- Corrected raw monomials: **72**
- Symmetry-canonical targets: **40**
- Terminal basis size: **12**

## Leading z-pole audit

Several individual basis coefficients contain a simple magnetic-projector pole `1/z`. No `1/z^2` pole remains after composition.

Basis 0 residue:

$$
\frac{\left(D - 6\right) \left(D - 5\right) \left(D - 2\right) \left(5 D^{2} - 31 D + 46\right)}{2 \left(D - 4\right) \left(D - 3\right)^{2}}
$$

Basis 1 residue:

$$
\frac{\left(D - 2\right) \left(6 D^{4} - 98 D^{3} + 573 D^{2} - 1410 D + 1240\right)}{2 \left(D - 4\right) \left(D - 3\right) \left(3 D - 8\right)}
$$

Basis 3 residue:

$$
\frac{16 \left(D - 5\right) \left(D^{2} - 9 D + 16\right)}{\left(D - 4\right)^{2} \left(D - 3\right) \left(D - 2\right)}
$$

Basis 5 residue:

$$
\frac{9 D^{5} - 182 D^{4} + 1414 D^{3} - 5289 D^{2} + 9550 D - 6680}{\left(D - 4\right) \left(D - 3\right) \left(D - 2\right)}
$$

Basis 6 residue:

$$
\frac{4 \left(9 D^{5} - 182 D^{4} + 1414 D^{3} - 5289 D^{2} + 9550 D - 6680\right)}{\left(D - 4\right) \left(D - 3\right) \left(D - 2\right) \left(3 D - 8\right)}
$$

Basis 7 residue:

$$
\frac{3 D^{4} - 45 D^{3} + 251 D^{2} - 605 D + 530}{\left(D - 3\right) \left(D - 2\right)}
$$

Basis 8 residue:

$$
- \frac{4 \left(3 D^{4} - 45 D^{3} + 251 D^{2} - 605 D + 530\right)}{\left(D - 2\right) \left(3 D - 8\right)}
$$

After inserting the exact v0.43 values of all twelve basis integrals at z=0, the coefficient of the complete `1/z` term is

$$
0
$$

so the leading projector singularity cancels exactly.

## What remains for the finite z->0 limit

Because some basis coefficients have `C_i(z)=r_i/z+c_i+...`, the finite term also contains `r_i I_i'(0)`. Therefore the exact z=0 basis values alone are not sufficient. The next stage is to derive and IBP-reduce the first z-derivatives of basis 0, 1, 3, 5, 6, 7, and 8 (zero weights can be skipped), then combine them with the regular coefficient parts and perform the epsilon expansion.
