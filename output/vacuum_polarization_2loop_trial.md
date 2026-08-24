# QEDCalc two-loop trial: vacuum polarization

Generated: 2026-08-22T11:10:33

## Scope

v0.21 parses the bare two-loop RHS as one LoopIntegralExpression. The overall normalization is preserved as LaTeX, the k/l loop measures are structural objects, and the closed electron loop is discovered from an explicit DiracTrace node. The trace propagators are scalarized automatically before the trace numerator is evaluated. The final renormalized scalar VP kernel is still supplied by the dedicated renormalization layer rather than reconstructed from the complete outer diagram in one command.

## Bare two-loop RHS parsed from LaTeX

$$
-\frac{e^4}{(2\pi)^8 i^2}\,\int d^{4}k\,d^{4}l\,\gamma^{\rho}\,\frac{1}{m - \left(\rlap{/}p'\right) + \rlap{/}k - \left(i\,\varepsilon\right)}\,\gamma_{\mu}\,\frac{1}{m - \left(\rlap{/}p\right) + \rlap{/}k - \left(i\,\varepsilon\right)}\,\gamma^{\sigma}\,\left(-\left(g_{\rho\alpha} + \left(1 - \left(\alpha\right)\right)\,\frac{k_{\rho}\,k_{\alpha}}{-\left(k\cdot k\right) - \left(i\,\varepsilon\right)}\right)\,\frac{1}{-\left(k\cdot k\right) - \left(i\,\varepsilon\right)}\right)\,\operatorname{tr}\left[\frac{1}{m - \left(\rlap{/}l\right) - \left(\rlap{/}k\right) - \left(i\,\varepsilon\right)}\,\gamma^{\alpha}\,\frac{1}{m - \left(\rlap{/}l\right) - \left(i\,\varepsilon\right)}\,\gamma^{\beta}\right]\,\left(-\left(g_{\beta\sigma} + \left(1 - \left(\alpha\right)\right)\,\frac{k_{\beta}\,k_{\sigma}}{-\left(k\cdot k\right) - \left(i\,\varepsilon\right)}\right)\,\frac{1}{-\left(k\cdot k\right) - \left(i\,\varepsilon\right)}\right)
$$

## Detected Dirac traces

1

## Scalarized closed-loop fraction

$$
\frac{\left(m + \rlap{/}l + \rlap{/}k\right)\,\gamma^{\alpha}\,\left(m + \rlap{/}l\right)\,\gamma^{\beta}}{\left(m^{2} - \left(\left(-\left(l\right) - \left(k\right)\right)^{2}\right) - \left(i\,\varepsilon\right)\right)\,\left(m^{2} - \left(\left(-\left(l\right)\right)^{2}\right) - \left(i\,\varepsilon\right)\right)}
$$

## Closed-loop trace numerator

$$
4\left(m\,m\,g_{\alpha\beta}\right) + 4\left(l^{\alpha}\,l^{\beta} - \left(l\cdot l\,g_{\alpha\beta}\right) + l^{\beta}\,l^{\alpha}\right) + 4\left(k^{\alpha}\,l^{\beta} - \left(k\cdot l\,g_{\alpha\beta}\right) + k^{\beta}\,l^{\alpha}\right)
$$

## Closed-loop scalar denominator

$$
\left(m^{2} - \left(\left(-\left(l\right) - \left(k\right)\right)^{2}\right) - \left(i\,\varepsilon\right)\right)\,\left(m^{2} - \left(\left(-\left(l\right)\right)^{2}\right) - \left(i\,\varepsilon\right)\right)
$$

## After l = r - z k

$$
4\left(m\,m\,g_{\alpha\beta}\right) + 4\left(r^{\alpha}\,r^{\beta}\right) - 4\left(r^{\alpha}\,z\,k^{\beta}\right) - 4\left(z\,k^{\alpha}\,r^{\beta}\right) + 4\left(z\,k^{\alpha}\,z\,k^{\beta}\right) - 4\left(r\cdot r\,g_{\alpha\beta}\right) + 4\left(z\,r\cdot k\,g_{\alpha\beta}\right) + 4\left(z\,k\cdot r\,g_{\alpha\beta}\right) - 4\left(z\,z\,k\cdot k\,g_{\alpha\beta}\right) + 4\left(r^{\beta}\,r^{\alpha}\right) - 4\left(r^{\beta}\,z\,k^{\alpha}\right) - 4\left(z\,k^{\beta}\,r^{\alpha}\right) + 4\left(z\,k^{\beta}\,z\,k^{\alpha}\right) + 4\left(k^{\alpha}\,r^{\beta}\right) - 4\left(k^{\alpha}\,z\,k^{\beta}\right) - 4\left(k\cdot r\,g_{\alpha\beta}\right) + 4\left(z\,k\cdot k\,g_{\alpha\beta}\right) + 4\left(k^{\beta}\,r^{\alpha}\right) - 4\left(k^{\beta}\,z\,k^{\alpha}\right)
$$

## After removing odd powers of r

$$
4\left(m\,m\,g_{\alpha\beta}\right) + 4\left(r^{\alpha}\,r^{\beta}\right) + 4\left(z\,k^{\alpha}\,z\,k^{\beta}\right) - 4\left(r\cdot r\,g_{\alpha\beta}\right) - 4\left(z\,z\,k\cdot k\,g_{\alpha\beta}\right) + 4\left(r^{\beta}\,r^{\alpha}\right) + 4\left(z\,k^{\beta}\,z\,k^{\alpha}\right) - 4\left(k^{\alpha}\,z\,k^{\beta}\right) + 4\left(z\,k\cdot k\,g_{\alpha\beta}\right) - 4\left(k^{\beta}\,z\,k^{\alpha}\right)
$$

## After rank-2 symmetric tensor reduction

$$
4\left(m\,m\,g_{\alpha\beta}\right) + 4\left(\frac{1}{4}\left(g_{\alpha\beta}\,r\cdot r\right)\right) + 4\left(z\,k^{\alpha}\,z\,k^{\beta}\right) - 4\left(r\cdot r\,g_{\alpha\beta}\right) - 4\left(z\,z\,k\cdot k\,g_{\alpha\beta}\right) + 4\left(\frac{1}{4}\left(g_{\beta\alpha}\,r\cdot r\right)\right) + 4\left(z\,k^{\beta}\,z\,k^{\alpha}\right) - 4\left(k^{\alpha}\,z\,k^{\beta}\right) + 4\left(z\,k\cdot k\,g_{\alpha\beta}\right) - 4\left(k^{\beta}\,z\,k^{\alpha}\right)
$$

## Reference transverse tensor checkpoint

$$
\Pi^{\alpha\beta}(k)=\left(k^2g^{\alpha\beta}-k^\alpha k^\beta\right)\Pi(k^2)
$$

## On-shell subtraction condition

$$
\Pi_R(k^2)=\Pi(k^2)-\Pi(0),\qquad \Pi_R(0)=0
$$

## Renormalized scalar vacuum-polarization integrand

$$
- 2 z \left(z - 1\right) \log{\left(\frac{m^{2}}{k_{2} z \left(z - 1\right) + m^{2}} \right)}
$$

## Two-parameter g-2 coefficient kernel

$$
2 z \left(x - 1\right) \left(z - 1\right) \log{\left(\frac{x^{2} z \left(z - 1\right) + x - 1}{x - 1} \right)}
$$

## z-integrated kernel H(x)

$$
\frac{3 x^{3} \log{\left(1 - x \right)} - 5 x^{3} - 12 x^{2} - 18 x \log{\left(1 - x \right)} + 12 x + 12 \log{\left(1 - x \right)}}{9 x^{3}}
$$

## Numerical coefficient

A_VP = 0.01568742185910268261072522226350517711766

## Analytic recognition from the numerical value

$$
\frac{119}{36} - \frac{\pi^{2}}{3}
$$

## Reference analytic coefficient

$$
\frac{119}{36} - \frac{\pi^{2}}{3}
$$

## Recognition check

PASS

## Two-loop anomalous-moment contribution

$$
a_{\mathrm{VP}}=\left(\frac{\alpha}{\pi}\right)^2\left(\frac{119}{36}-\frac{\pi^2}{3}\right)
$$
