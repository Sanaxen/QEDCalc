# Phase 81: ordinary ladder end-to-end checkpoint

QEDCalc version: `0.88.2`

## Reduction chain

- corrected spin-sum projector table: 72 terms
- canonical IBP targets after symmetry combination: 40
- terminal analytic basis size: 12
- leading magnetic-projector z-pole residual: `0`

## Bare finite coefficient

The full 40-to-12 basis assembly gives

$$
F_{2,\mathrm L}^{\mathrm{bare}}=-\frac{3}{4\delta}+C_{\mathrm{bare}}+O(\delta),
$$

Numerically reconstructed `C_bare`: **2.7774780222827421454846518587600728587736922181285**

Independent analytic checkpoint:

$$
C_{\mathrm{bare}}=\frac{107}{48}+\frac{\pi^2}{18}.
$$

Absolute reconstruction difference: **6.1531967886e-21**

## On-shell subtraction

$$
Z_1^{(1)}F_2^{(1)}=-\frac{3}{4\delta}+2+O(\delta).
$$

Pole coefficient: `-3/4`
Finite subtraction: `2`

The pole cancels against the bare ladder pole, while the finite subtraction removes 2.

## Renormalized ordinary ladder

$$
A_{\mathrm L}=\frac{11}{48}+\frac{\pi^2}{18}.
$$

Numerical end-to-end reconstruction: **0.77747802228274214548465185876007285877369221812845**
Independent analytic value: **0.77747802228274214549080505554867506307298330040227**
Absolute difference: **6.1531967886e-21**
Symbolic renormalized residual: `0`

No final ordinary-ladder coefficient is fed into the 72 -> 40 -> 12 master reconstruction; the closed form is used only as the output-side checkpoint.
