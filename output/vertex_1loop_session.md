# QED 1-loop vertex correction - calculation session

Generated: 2026-08-22T12:27:37

## Version

QEDCalc v0.28.0

## Symbol definitions

`symbols.txt`

- **Scalar:** \alpha, e, epsilon_IR, epsilon_UV, \lambda, m, \varepsilon
- **Constants:** i, \pi
- **Vector:** k, l, p, p', q, r
- **Index:** \alpha, \beta, \lambda, \mu, \nu, \rho, \sigma

## Input file

`input/vertex_1loop_integrand.tex`

## Original input

$$
\gamma^\rho
\frac{1}{m-\rlap{/}p'+\rlap{/}k-i\varepsilon}
\gamma_\mu
\frac{1}{m-\rlap{/}p+\rlap{/}k-i\varepsilon}
\gamma^\sigma
\left(
-\frac{g_{\rho\sigma}}{-k^2-i\varepsilon}
\right)
$$

## Numerator after symmetric loop reduction

$$
-\left(-2\left(m\,m\,\gamma_{\mu}\right) + 4\left(m\,p_{\mu}\right) - 4\left(m\,x\,p'_{\mu} + m\,y\,p_{\mu}\right) + 4\left(m\,p'_{\mu}\right) - 2\left(\rlap{/}p\,\gamma_{\mu}\,\rlap{/}p'\right) + 2\left(x\,\rlap{/}p'\,\gamma_{\mu}\,\rlap{/}p' + y\,\rlap{/}p\,\gamma_{\mu}\,\rlap{/}p'\right) - 4\left(m\,x\,p'_{\mu} + m\,y\,p_{\mu}\right) + 2\left(\rlap{/}p\,\gamma_{\mu}\,x\,\rlap{/}p' + \rlap{/}p\,\gamma_{\mu}\,y\,\rlap{/}p\right) - 2\left(- \frac{1}{2}\left(l\cdot l\,\gamma_{\mu}\right) + x\,\rlap{/}p'\,\gamma_{\mu}\,x\,\rlap{/}p' + x\,\rlap{/}p'\,\gamma_{\mu}\,y\,\rlap{/}p + y\,\rlap{/}p\,\gamma_{\mu}\,x\,\rlap{/}p' + y\,\rlap{/}p\,\gamma_{\mu}\,y\,\rlap{/}p\right)\right)
$$

## Step 15: Non-commutative normalization

### Input

$$
-\left(-2\left(m\,m\,\gamma_{\mu}\right) + 4\left(m\,p_{\mu}\right) - 4\left(m\,x\,p'_{\mu} + m\,y\,p_{\mu}\right) + 4\left(m\,p'_{\mu}\right) - 2\left(\rlap{/}p\,\gamma_{\mu}\,\rlap{/}p'\right) + 2\left(x\,\rlap{/}p'\,\gamma_{\mu}\,\rlap{/}p' + y\,\rlap{/}p\,\gamma_{\mu}\,\rlap{/}p'\right) - 4\left(m\,x\,p'_{\mu} + m\,y\,p_{\mu}\right) + 2\left(\rlap{/}p\,\gamma_{\mu}\,x\,\rlap{/}p' + \rlap{/}p\,\gamma_{\mu}\,y\,\rlap{/}p\right) - 2\left(- \frac{1}{2}\left(l\cdot l\,\gamma_{\mu}\right) + x\,\rlap{/}p'\,\gamma_{\mu}\,x\,\rlap{/}p' + x\,\rlap{/}p'\,\gamma_{\mu}\,y\,\rlap{/}p + y\,\rlap{/}p\,\gamma_{\mu}\,x\,\rlap{/}p' + y\,\rlap{/}p\,\gamma_{\mu}\,y\,\rlap{/}p\right)\right)
$$

### Applied rule

Move commutative scalar coefficients outside slash/gamma chains so the Dirac ordering is explicit.

### Output

$$
-\left(-2\left(m\,m\,\gamma_{\mu}\right) + 4\left(m\,p_{\mu}\right) - 4\left(m\,x\,p'_{\mu} + m\,y\,p_{\mu}\right) + 4\left(m\,p'_{\mu}\right) - 2\left(\rlap{/}p\,\gamma_{\mu}\,\rlap{/}p'\right) + 2\left(x\,\rlap{/}p'\,\gamma_{\mu}\,\rlap{/}p' + y\,\rlap{/}p\,\gamma_{\mu}\,\rlap{/}p'\right) - 4\left(m\,x\,p'_{\mu} + m\,y\,p_{\mu}\right) + 2\left(x\,\rlap{/}p\,\gamma_{\mu}\,\rlap{/}p' + y\,\rlap{/}p\,\gamma_{\mu}\,\rlap{/}p\right) - 2\left(- \frac{1}{2}\left(l\cdot l\,\gamma_{\mu}\right) + x\,x\,\rlap{/}p'\,\gamma_{\mu}\,\rlap{/}p' + x\,y\,\rlap{/}p'\,\gamma_{\mu}\,\rlap{/}p + y\,x\,\rlap{/}p\,\gamma_{\mu}\,\rlap{/}p' + y\,y\,\rlap{/}p\,\gamma_{\mu}\,\rlap{/}p\right)\right)
$$

## Step 16: Exact external Dirac reduction

### Input

$$
-\left(-2\left(m\,m\,\gamma_{\mu}\right) + 4\left(m\,p_{\mu}\right) - 4\left(m\,x\,p'_{\mu} + m\,y\,p_{\mu}\right) + 4\left(m\,p'_{\mu}\right) - 2\left(\rlap{/}p\,\gamma_{\mu}\,\rlap{/}p'\right) + 2\left(x\,\rlap{/}p'\,\gamma_{\mu}\,\rlap{/}p' + y\,\rlap{/}p\,\gamma_{\mu}\,\rlap{/}p'\right) - 4\left(m\,x\,p'_{\mu} + m\,y\,p_{\mu}\right) + 2\left(x\,\rlap{/}p\,\gamma_{\mu}\,\rlap{/}p' + y\,\rlap{/}p\,\gamma_{\mu}\,\rlap{/}p\right) - 2\left(- \frac{1}{2}\left(l\cdot l\,\gamma_{\mu}\right) + x\,x\,\rlap{/}p'\,\gamma_{\mu}\,\rlap{/}p' + x\,y\,\rlap{/}p'\,\gamma_{\mu}\,\rlap{/}p + y\,x\,\rlap{/}p\,\gamma_{\mu}\,\rlap{/}p' + y\,y\,\rlap{/}p\,\gamma_{\mu}\,\rlap{/}p\right)\right)
$$

### Applied rule

Recursively commute /p' left and /p right. Each recursion lowers the distance to an external spinor, then the on-shell Dirac equation is applied.

### Output

$$
\bar u(p')\,\left[-\left(-2\left(m\,m\,\gamma_{\mu}\right) + 4\left(m\,p_{\mu}\right) - 4\left(m\,x\,p'_{\mu} + m\,y\,p_{\mu}\right) + 4\left(m\,p'_{\mu}\right) - 2\left(2\left(p'_{\mu}\,m\right) - \left(2\left(p\cdot p'\,\gamma_{\mu}\right) - \left(2\left(m\,p_{\mu}\right) - \left(m\,m\,\gamma_{\mu}\right)\right)\right)\right) + 2\left(2\left(x\,m\,p'_{\mu}\right) - \left(x\,m\,m\,\gamma_{\mu}\right) + 2\left(y\,p'_{\mu}\,m\right) - \left(y\,\left(2\left(p\cdot p'\,\gamma_{\mu}\right) - \left(2\left(m\,p_{\mu}\right) - \left(m\,m\,\gamma_{\mu}\right)\right)\right)\right)\right) - 4\left(m\,x\,p'_{\mu} + m\,y\,p_{\mu}\right) + 2\left(2\left(x\,p'_{\mu}\,m\right) - \left(x\,\left(2\left(p\cdot p'\,\gamma_{\mu}\right) - \left(2\left(m\,p_{\mu}\right) - \left(m\,m\,\gamma_{\mu}\right)\right)\right)\right) + 2\left(y\,m\,p_{\mu}\right) - \left(y\,m\,m\,\gamma_{\mu}\right)\right) - 2\left(- \frac{1}{2}\left(l\cdot l\,\gamma_{\mu}\right) + 2\left(x\,x\,m\,p'_{\mu}\right) - \left(x\,x\,m\,m\,\gamma_{\mu}\right) + x\,y\,m\,m\,\gamma_{\mu} + 2\left(y\,x\,p'_{\mu}\,m\right) - \left(y\,x\,\left(2\left(p\cdot p'\,\gamma_{\mu}\right) - \left(2\left(m\,p_{\mu}\right) - \left(m\,m\,\gamma_{\mu}\right)\right)\right)\right) + 2\left(y\,y\,m\,p_{\mu}\right) - \left(y\,y\,m\,m\,\gamma_{\mu}\right)\right)\right)\right]\,u(p)
$$

## Step 17: Momentum-transfer introduction

### Input

$$
\bar u(p')\,\left[-\left(-2\left(m\,m\,\gamma_{\mu}\right) + 4\left(m\,p_{\mu}\right) - 4\left(m\,x\,p'_{\mu} + m\,y\,p_{\mu}\right) + 4\left(m\,p'_{\mu}\right) - 2\left(2\left(p'_{\mu}\,m\right) - \left(2\left(p\cdot p'\,\gamma_{\mu}\right) - \left(2\left(m\,p_{\mu}\right) - \left(m\,m\,\gamma_{\mu}\right)\right)\right)\right) + 2\left(2\left(x\,m\,p'_{\mu}\right) - \left(x\,m\,m\,\gamma_{\mu}\right) + 2\left(y\,p'_{\mu}\,m\right) - \left(y\,\left(2\left(p\cdot p'\,\gamma_{\mu}\right) - \left(2\left(m\,p_{\mu}\right) - \left(m\,m\,\gamma_{\mu}\right)\right)\right)\right)\right) - 4\left(m\,x\,p'_{\mu} + m\,y\,p_{\mu}\right) + 2\left(2\left(x\,p'_{\mu}\,m\right) - \left(x\,\left(2\left(p\cdot p'\,\gamma_{\mu}\right) - \left(2\left(m\,p_{\mu}\right) - \left(m\,m\,\gamma_{\mu}\right)\right)\right)\right) + 2\left(y\,m\,p_{\mu}\right) - \left(y\,m\,m\,\gamma_{\mu}\right)\right) - 2\left(- \frac{1}{2}\left(l\cdot l\,\gamma_{\mu}\right) + 2\left(x\,x\,m\,p'_{\mu}\right) - \left(x\,x\,m\,m\,\gamma_{\mu}\right) + x\,y\,m\,m\,\gamma_{\mu} + 2\left(y\,x\,p'_{\mu}\,m\right) - \left(y\,x\,\left(2\left(p\cdot p'\,\gamma_{\mu}\right) - \left(2\left(m\,p_{\mu}\right) - \left(m\,m\,\gamma_{\mu}\right)\right)\right)\right) + 2\left(y\,y\,m\,p_{\mu}\right) - \left(y\,y\,m\,m\,\gamma_{\mu}\right)\right)\right)\right]\,u(p)
$$

### Applied rule

Introduce q = p' - p, apply p^2 = p'^2 = m^2, and use p.q = -q^2/2.

### Output

$$
\bar u(p')\,\left[-\left(-2\left(m\,m\,\gamma_{\mu}\right) + 4\left(m\,p_{\mu}\right) - 4\left(m\,x\,p_{\mu} + m\,x\,q_{\mu} + m\,y\,p_{\mu}\right) + 4\left(m\,p_{\mu} + m\,q_{\mu}\right) - 2\left(2\left(p_{\mu}\,m + q_{\mu}\,m\right) - \left(2\left(m^{2}\,\gamma_{\mu} - 0.5\left(q\cdot q\,\gamma_{\mu}\right)\right) - \left(2\left(m\,p_{\mu}\right) - \left(m\,m\,\gamma_{\mu}\right)\right)\right)\right) + 2\left(2\left(x\,m\,p_{\mu} + x\,m\,q_{\mu}\right) - \left(x\,m\,m\,\gamma_{\mu}\right) + 2\left(y\,p_{\mu}\,m + y\,q_{\mu}\,m\right) - \left(2\left(y\,m^{2}\,\gamma_{\mu}\right) - \left(y\,q\cdot q\,\gamma_{\mu}\right) - 2\left(y\,m\,p_{\mu}\right) + y\,m\,m\,\gamma_{\mu}\right)\right) - 4\left(m\,x\,p_{\mu} + m\,x\,q_{\mu} + m\,y\,p_{\mu}\right) + 2\left(2\left(x\,p_{\mu}\,m + x\,q_{\mu}\,m\right) - \left(2\left(x\,m^{2}\,\gamma_{\mu}\right) - \left(x\,q\cdot q\,\gamma_{\mu}\right) - 2\left(x\,m\,p_{\mu}\right) + x\,m\,m\,\gamma_{\mu}\right) + 2\left(y\,m\,p_{\mu}\right) - \left(y\,m\,m\,\gamma_{\mu}\right)\right) - 2\left(- \frac{1}{2}\left(l\cdot l\,\gamma_{\mu}\right) + 2\left(x\,x\,m\,p_{\mu} + x\,x\,m\,q_{\mu}\right) - \left(x\,x\,m\,m\,\gamma_{\mu}\right) + x\,y\,m\,m\,\gamma_{\mu} + 2\left(y\,x\,p_{\mu}\,m + y\,x\,q_{\mu}\,m\right) - \left(2\left(y\,x\,m^{2}\,\gamma_{\mu}\right) - \left(y\,x\,q\cdot q\,\gamma_{\mu}\right) - 2\left(y\,x\,m\,p_{\mu}\right) + y\,x\,m\,m\,\gamma_{\mu}\right) + 2\left(y\,y\,m\,p_{\mu}\right) - \left(y\,y\,m\,m\,\gamma_{\mu}\right)\right)\right)\right]\,u(p)
$$

## Step 18: First-order q truncation

### Input

$$
\bar u(p')\,\left[-\left(-2\left(m\,m\,\gamma_{\mu}\right) + 4\left(m\,p_{\mu}\right) - 4\left(m\,x\,p_{\mu} + m\,x\,q_{\mu} + m\,y\,p_{\mu}\right) + 4\left(m\,p_{\mu} + m\,q_{\mu}\right) - 2\left(2\left(p_{\mu}\,m + q_{\mu}\,m\right) - \left(2\left(m^{2}\,\gamma_{\mu} - 0.5\left(q\cdot q\,\gamma_{\mu}\right)\right) - \left(2\left(m\,p_{\mu}\right) - \left(m\,m\,\gamma_{\mu}\right)\right)\right)\right) + 2\left(2\left(x\,m\,p_{\mu} + x\,m\,q_{\mu}\right) - \left(x\,m\,m\,\gamma_{\mu}\right) + 2\left(y\,p_{\mu}\,m + y\,q_{\mu}\,m\right) - \left(2\left(y\,m^{2}\,\gamma_{\mu}\right) - \left(y\,q\cdot q\,\gamma_{\mu}\right) - 2\left(y\,m\,p_{\mu}\right) + y\,m\,m\,\gamma_{\mu}\right)\right) - 4\left(m\,x\,p_{\mu} + m\,x\,q_{\mu} + m\,y\,p_{\mu}\right) + 2\left(2\left(x\,p_{\mu}\,m + x\,q_{\mu}\,m\right) - \left(2\left(x\,m^{2}\,\gamma_{\mu}\right) - \left(x\,q\cdot q\,\gamma_{\mu}\right) - 2\left(x\,m\,p_{\mu}\right) + x\,m\,m\,\gamma_{\mu}\right) + 2\left(y\,m\,p_{\mu}\right) - \left(y\,m\,m\,\gamma_{\mu}\right)\right) - 2\left(- \frac{1}{2}\left(l\cdot l\,\gamma_{\mu}\right) + 2\left(x\,x\,m\,p_{\mu} + x\,x\,m\,q_{\mu}\right) - \left(x\,x\,m\,m\,\gamma_{\mu}\right) + x\,y\,m\,m\,\gamma_{\mu} + 2\left(y\,x\,p_{\mu}\,m + y\,x\,q_{\mu}\,m\right) - \left(2\left(y\,x\,m^{2}\,\gamma_{\mu}\right) - \left(y\,x\,q\cdot q\,\gamma_{\mu}\right) - 2\left(y\,x\,m\,p_{\mu}\right) + y\,x\,m\,m\,\gamma_{\mu}\right) + 2\left(y\,y\,m\,p_{\mu}\right) - \left(y\,y\,m\,m\,\gamma_{\mu}\right)\right)\right)\right]\,u(p)
$$

### Applied rule

Discard terms of explicit order q^2 and higher. The magnetic form factor requires the current through first order in q.

### Output

$$
\bar u(p')\,\left[-\left(-2\left(m\,m\,\gamma_{\mu}\right) + 4\left(m\,p_{\mu}\right) - 4\left(m\,x\,p_{\mu} + m\,x\,q_{\mu} + m\,y\,p_{\mu}\right) + 4\left(m\,p_{\mu} + m\,q_{\mu}\right) - 2\left(2\left(p_{\mu}\,m + q_{\mu}\,m\right) - \left(2\left(m^{2}\,\gamma_{\mu}\right) - \left(2\left(m\,p_{\mu}\right) - \left(m\,m\,\gamma_{\mu}\right)\right)\right)\right) + 2\left(2\left(x\,m\,p_{\mu} + x\,m\,q_{\mu}\right) - \left(x\,m\,m\,\gamma_{\mu}\right) + 2\left(y\,p_{\mu}\,m + y\,q_{\mu}\,m\right) - \left(2\left(y\,m^{2}\,\gamma_{\mu}\right) - 2\left(y\,m\,p_{\mu}\right) + y\,m\,m\,\gamma_{\mu}\right)\right) - 4\left(m\,x\,p_{\mu} + m\,x\,q_{\mu} + m\,y\,p_{\mu}\right) + 2\left(2\left(x\,p_{\mu}\,m + x\,q_{\mu}\,m\right) - \left(2\left(x\,m^{2}\,\gamma_{\mu}\right) - 2\left(x\,m\,p_{\mu}\right) + x\,m\,m\,\gamma_{\mu}\right) + 2\left(y\,m\,p_{\mu}\right) - \left(y\,m\,m\,\gamma_{\mu}\right)\right) - 2\left(- \frac{1}{2}\left(l\cdot l\,\gamma_{\mu}\right) + 2\left(x\,x\,m\,p_{\mu} + x\,x\,m\,q_{\mu}\right) - \left(x\,x\,m\,m\,\gamma_{\mu}\right) + x\,y\,m\,m\,\gamma_{\mu} + 2\left(y\,x\,p_{\mu}\,m + y\,x\,q_{\mu}\,m\right) - \left(2\left(y\,x\,m^{2}\,\gamma_{\mu}\right) - 2\left(y\,x\,m\,p_{\mu}\right) + y\,x\,m\,m\,\gamma_{\mu}\right) + 2\left(y\,y\,m\,p_{\mu}\right) - \left(y\,y\,m\,m\,\gamma_{\mu}\right)\right)\right)\right]\,u(p)
$$

## Gamma_mu coefficient

$$
-\left(l\cdot l\right) - 4\left(m^{2}\right) - 2\left(m^{2}\,x^{2}\right) - 2\left(m^{2}\,y^{2}\right) + 8\left(x\,m^{2}\right) + 8\left(y\,m^{2}\right) - 4\left(x\,y\,m^{2}\right)
$$

## p_mu coefficient

$$
4\left(m\,\left(x + y\right)\,\left(-1 + x + y\right)\right)
$$

## q_mu coefficient

$$
4\left(m\,\left(x^{2} - \left(y\right) + x\,y\right)\right)
$$

## Residual current structures

$$
0
$$

## Gordon-pair coefficient B multiplying (p' + p)_mu

$$
2\left(m\,\left(x + y\right)\,\left(-1 + x + y\right)\right)
$$

## Longitudinal q_mu coefficient

$$
2\left(m\,\left(x - \left(y\right)\right)\,\left(1 + x + y\right)\right)
$$

## Projected F2 numerator

$$
-4\left(m^{2}\,\left(x + y\right)\,\left(-1 + x + y\right)\right)
$$

## Shifted denominator at q = 0

$$
-\left(l\cdot l\right) + x^{2}\,m^{2} + 2\left(x\,y\,m^{2}\right) + y^{2}\,m^{2} - \left(i\,\varepsilon\right)
$$

## Delta

$$
m^{2}\,\left(x + y\right)^{2}
$$

## Scalar loop integral convention

For the cubic denominator, QEDCalc uses the convention `int d^4l / (-l^2 + Delta - i epsilon)^3 = i*pi^2/(2*Delta)`. Together with the original vertex prefactor and the Feynman-parameter factor 2, this leaves alpha/(4*pi) times the triangle parameter integral.

## Parameter integrand after loop integration

$$
\frac{- 4 x - 4 y + 4}{x + y}
$$

## Triangle parameter integral

`2`

## Final one-loop anomalous magnetic moment correction

$$
\frac{\alpha}{2\,\pi}
$$

## Index validation

- [INFO] \mu: appears once; it may be a free index.
- [OK] \rho: appears twice; it is a contraction-index candidate.
- [OK] \sigma: appears twice; it is a contraction-index candidate.
