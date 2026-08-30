# Phase 24: crossed-ladder raw one-variable kernel regeneration

The t integral is generated directly from the Phase-23 triangular kernel.

A lower cutoff epsilon is retained until the rational and logarithmic sectors are combined. Its logarithmic coefficient cancels exactly:

$$
C_{\ln\varepsilon}=0.
$$

The resulting one-variable kernel closes on

$$
1,\quad L,\quad M,\quad L^2,\quad LM,\quad D(q),
$$

with $L=\ln q$, $M=\ln(1-q)$ and $D(q)=\operatorname{Li}_2(q)-\operatorname{Li}_2(2-1/q)$.

Using the audited total-derivative primitive G(q), the exact symbolic check gives

$$
\mathcal F_{\rm raw}(q)-\frac{d\mathcal G}{dq}-\mathcal F_{\rm can}(q)=0.
$$

Raw-kernel operation count: **269**.
