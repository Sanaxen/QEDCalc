# QEDCalc phase-10 ordinary-ladder basis-evaluation trial

The v0.41 corrected ordinary-ladder reduction terminates on 12 basis integrals. v0.42 starts the evaluation layer for those basis objects.

## Classification

Generic-z factorized lower sectors: **3**.

Exact analytic z=0 basis values: **9 / 12**.

Remaining genuine z=0 masters: **3** (basis 8, 10, 11).

All formulas below are convention-free Euclidean scalar integrals. Overall Minkowski i factors, Wick-rotation signs, (2pi)^D loop-measure normalization, and renormalization-scale factors belong to the convention layer.

## z=0 analytic values

### Basis 0: `(0, 0, 0, 0, 0, 1, 1)`

Status: **exact**. Method: `factorized_tadpoles_T1xT1`.

$$
\pi^{D} m_{2}^{D - 2} \Gamma^{2}\left(1 - \frac{D}{2}\right)
$$

### Basis 1: `(0, 0, 0, 0, 1, 0, 1)`

Status: **exact**. Method: `factorized_tadpoles_T1xT1`.

$$
\pi^{D} m_{2}^{D - 2} \Gamma^{2}\left(1 - \frac{D}{2}\right)
$$

### Basis 2: `(0, 0, 0, 0, 1, 1, 1)`

Status: **exact**. Method: `z0_degenerate_factorization_T2xT1`.

$$
\pi^{D} m_{2}^{D - 3} \Gamma\left(1 - \frac{D}{2}\right) \Gamma\left(2 - \frac{D}{2}\right)
$$

### Basis 3: `(0, 0, 0, 0, 2, 0, 3)`

Status: **exact**. Method: `factorized_tadpoles_T2xT3`.

$$
\frac{\pi^{D} m_{2}^{D - 5} \Gamma\left(2 - \frac{D}{2}\right) \Gamma\left(3 - \frac{D}{2}\right)}{2}
$$

### Basis 4: `(0, 0, 0, 1, 1, 1, 1)`

Status: **exact**. Method: `z0_degenerate_factorization_T2xT2`.

$$
\pi^{D} m_{2}^{D - 4} \Gamma^{2}\left(2 - \frac{D}{2}\right)
$$

### Basis 5: `(0, 1, 0, 0, 1, 0, 1)`

Status: **exact**. Method: `one_massless_two_massive_vacuum_111`.

$$
\frac{\pi^{D} m_{2}^{D - 3} \Gamma^{2}\left(2 - \frac{D}{2}\right) \Gamma\left(3 - D\right) \Gamma\left(\frac{D}{2} - 1\right)}{\Gamma\left(\frac{D}{2}\right) \Gamma\left(4 - D\right)}
$$

### Basis 6: `(0, 1, 0, 0, 1, 0, 2)`

Status: **exact**. Method: `one_massless_two_massive_vacuum_112`.

$$
\frac{\pi^{D} m_{2}^{D - 4} \Gamma\left(2 - \frac{D}{2}\right) \Gamma\left(3 - \frac{D}{2}\right) \Gamma\left(4 - D\right) \Gamma\left(\frac{D}{2} - 1\right)}{\Gamma\left(\frac{D}{2}\right) \Gamma\left(5 - D\right)}
$$

### Basis 7: `(0, 1, 1, 0, 0, 0, 1)`

Status: **exact**. Method: `massless_bubble_then_on_shell_E4`.

$$
\frac{\pi^{D} m_{2}^{D - 3} \Gamma\left(2 - \frac{D}{2}\right) \Gamma\left(3 - D\right) \Gamma^{2}\left(\frac{D}{2} - 1\right) \Gamma\left(2 D - 5\right)}{\Gamma\left(D - 2\right) \Gamma\left(\frac{3 D}{2} - 3\right)}
$$

### Basis 8: `(0, 1, 1, 0, 1, 0, 1)`

Status: **unresolved**. Method: `genuine_two_loop_z0_master`.

The current evaluator leaves this as a genuine two-loop master. Its automatically generated projective polynomials are:

$$
U=b9x1 b9x2 + b9x1 b9x3 + b9x1 b9x4 + b9x2 b9x4 + b9x3 b9x4
$$

$$
F=m_{2} \left(b9x1 b9x3^{2} + 2 b9x1 b9x3 b9x4 + b9x1 b9x4^{2} + b9x2 b9x4^{2} + b9x3^{2} b9x4 + b9x3 b9x4^{2}\right)
$$

### Basis 9: `(0, 1, 1, 1, 0, 0, 1)`

Status: **exact**. Method: `z0_E1_equals_E4_massless_bubble_E4_squared`.

$$
\frac{\pi^{D} m_{2}^{D - 4} \Gamma\left(2 - \frac{D}{2}\right) \Gamma\left(4 - D\right) \Gamma^{2}\left(\frac{D}{2} - 1\right) \Gamma\left(2 D - 6\right)}{\Gamma\left(D - 2\right) \Gamma\left(\frac{3 D}{2} - 4\right)}
$$

### Basis 10: `(0, 1, 1, 1, 0, 1, 1)`

Status: **unresolved**. Method: `genuine_two_loop_z0_master`.

The current evaluator leaves this as a genuine two-loop master. Its automatically generated projective polynomials are:

$$
U=b11x1 b11x2 + b11x1 b11x3 + b11x1 b11x4 + b11x1 b11x5 + b11x2 b11x3 + b11x2 b11x5 + b11x3 b11x4 + b11x4 b11x5
$$

$$
F=m_{2} \left(b11x1 b11x3^{2} + 2 b11x1 b11x3 b11x4 + 2 b11x1 b11x3 b11x5 + b11x1 b11x4^{2} + 2 b11x1 b11x4 b11x5 + b11x1 b11x5^{2} + b11x2 b11x3^{2} + 2 b11x2 b11x3 b11x5 + b11x2 b11x5^{2} + b11x3^{2} b11x4 + b11x3 b11x4^{2} + 2 b11x3 b11x4 b11x5 + b11x4^{2} b11x5 + b11x4 b11x5^{2}\right)
$$

### Basis 11: `(0, 1, 1, 1, 1, 0, 2)`

Status: **unresolved**. Method: `genuine_two_loop_z0_master`.

The current evaluator leaves this as a genuine two-loop master. Its automatically generated projective polynomials are:

$$
U=b12x1 b12x2 + b12x1 b12x3 + b12x1 b12x4 + b12x1 b12x5 + b12x2 b12x3 + b12x2 b12x5 + b12x3 b12x4 + b12x4 b12x5
$$

$$
F=m_{2} \left(b12x1 b12x3^{2} + 2 b12x1 b12x3 b12x4 + 2 b12x1 b12x3 b12x5 + b12x1 b12x4^{2} + 2 b12x1 b12x4 b12x5 + b12x1 b12x5^{2} + b12x2 b12x3^{2} + 2 b12x2 b12x3 b12x5 + b12x2 b12x5^{2} + b12x3^{2} b12x4 + b12x3 b12x4^{2} + 2 b12x3 b12x4 b12x5 + b12x4^{2} b12x5 + b12x4 b12x5^{2}\right)
$$

## Evaluation methods now available

1. Products of massive one-loop tadpoles.
2. z=0 degeneracies where E1=E4 and/or E2=E3.
3. The one-massless/two-equal-mass two-loop vacuum sunset in Gamma functions.
4. A massless bubble followed by a generalized on-shell massive one-loop integral.
5. Generic projective Feynman-parameter generation U, F, Delta for every one of the 12 basis integrals.

The next evaluation stage is therefore reduced to basis 8, 10, and 11.

Classification CSV: `output/ladder_12basis_parametric_classification.csv`

z=0 evaluation CSV: `output/ladder_12basis_z0_evaluation.csv`
