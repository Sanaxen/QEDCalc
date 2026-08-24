# QEDCalc two-loop trial: self-energy insertion

Generated: 2026-08-22T11:10:31

## Version

QEDCalc v0.23.0

## Loaded conventions

- **metric_signature:** `+---`
- **gauge:** `feynman`
- **renormalization_scheme:** `on_shell`
- **dimreg_dimension:** `4 - 2*epsilon`
- **dimreg_subtraction:** `MSbar`
- **msbar_factor:** `true`
- **subdiagram_include_coupling:** `true`
- **subdiagram_include_loop_measure:** `true`
- **subdiagram_include_i:** `true`
- **coupling_symbol:** `e`
- **loop_measure_denominator_latex:** `(2\pi)^4`
- **loop_i_factor_latex:** `i`

## Outer prefactor generated from conventions.txt

$$
\frac{e^{2}}{(2\pi)^4 i}
$$

## Scope

v0.22 parses each bare two-loop self-energy-insertion RHS as one LoopIntegralExpression, discovers the open one-loop self-energy block from the repeated electron propagator pattern, identifies whether the insertion is left or right of the external photon vertex, and contracts it to S Sigma S. After the existing on-shell UV cancellation check passes, the same topology is rendered with Sigma_R. The internal-photon reduction currently selects the Feynman-gauge metric part; automatic finite on-shell counterterm reconstruction directly from the raw general-gauge expression remains a later step.

## Raw right-insertion two-loop RHS

$$
\frac{e^4}{(2\pi)^8 i^2}\,\int d^{4}k\,d^{4}l\,\gamma^{\rho}\,\frac{1}{m - \left(\rlap{/}p'\right) + \rlap{/}k - \left(i\,\varepsilon\right)}\,\gamma_{\mu}\,\frac{1}{m - \left(\rlap{/}p\right) + \rlap{/}k - \left(i\,\varepsilon\right)}\,\gamma^{\alpha}\,\frac{1}{m - \left(\rlap{/}p\right) + \rlap{/}k + \rlap{/}l - \left(i\,\varepsilon\right)}\,\gamma^{\beta}\,\frac{1}{m - \left(\rlap{/}p\right) + \rlap{/}k - \left(i\,\varepsilon\right)}\,\gamma^{\sigma}\,\left(-\left(g_{\rho\sigma} + \left(1 - \left(\alpha\right)\right)\,\frac{k_{\rho}\,k_{\sigma}}{-\left(k\cdot k\right) - \left(i\,\varepsilon\right)}\right)\,\frac{1}{-\left(k\cdot k\right) - \left(i\,\varepsilon\right)}\right)\,\left(-\left(g_{\alpha\beta} + \left(1 - \left(\alpha\right)\right)\,\frac{l_{\alpha}\,l_{\beta}}{-\left(l\cdot l\right) - \left(i\,\varepsilon\right)}\right)\,\frac{1}{-\left(l\cdot l\right) - \left(i\,\varepsilon\right)}\right)
$$

## Right subdiagram detection

PASS: side=right, subloop=l, external momentum=p - \left(k\right)

## Right self-energy numerator extracted from raw RHS

$$
4\left(m\right) - 2\left(\rlap{/}\left(p - \left(k\right)\right)\right) + 2\left(\rlap{/}l\right)
$$

## Right compact bare outer diagram

$$
\frac{e^{2}}{(2\pi)^4 i}\,\int d^{4}k\,\gamma^{\rho}\,\frac{1}{m - \left(\rlap{/}p'\right) + \rlap{/}k - \left(i\,\varepsilon\right)}\,\gamma_{\mu}\,\frac{1}{m - \left(\rlap{/}p\right) + \rlap{/}k - \left(i\,\varepsilon\right)}\,\Sigma^{(1)}\left(p - \left(k\right)\right)\,\frac{1}{m - \left(\rlap{/}p\right) + \rlap{/}k - \left(i\,\varepsilon\right)}\,\gamma^{\sigma}\,\left(-\left(g_{\rho\sigma} + \left(1 - \left(\alpha\right)\right)\,\frac{k_{\rho}\,k_{\sigma}}{-\left(k\cdot k\right) - \left(i\,\varepsilon\right)}\right)\,\frac{1}{-\left(k\cdot k\right) - \left(i\,\varepsilon\right)}\right)
$$

## Raw left-insertion two-loop RHS

$$
\frac{e^4}{(2\pi)^8 i^2}\,\int d^{4}k\,d^{4}l\,\gamma^{\rho}\,\frac{1}{m - \left(\rlap{/}p'\right) + \rlap{/}k - \left(i\,\varepsilon\right)}\,\gamma^{\alpha}\,\frac{1}{m - \left(\rlap{/}p'\right) + \rlap{/}k + \rlap{/}l - \left(i\,\varepsilon\right)}\,\gamma^{\beta}\,\frac{1}{m - \left(\rlap{/}p'\right) + \rlap{/}k - \left(i\,\varepsilon\right)}\,\gamma_{\mu}\,\frac{1}{m - \left(\rlap{/}p\right) + \rlap{/}k - \left(i\,\varepsilon\right)}\,\gamma^{\sigma}\,\left(-\left(g_{\rho\sigma} + \left(1 - \left(\alpha\right)\right)\,\frac{k_{\rho}\,k_{\sigma}}{-\left(k\cdot k\right) - \left(i\,\varepsilon\right)}\right)\,\frac{1}{-\left(k\cdot k\right) - \left(i\,\varepsilon\right)}\right)\,\left(-\left(g_{\alpha\beta} + \left(1 - \left(\alpha\right)\right)\,\frac{l_{\alpha}\,l_{\beta}}{-\left(l\cdot l\right) - \left(i\,\varepsilon\right)}\right)\,\frac{1}{-\left(l\cdot l\right) - \left(i\,\varepsilon\right)}\right)
$$

## Left subdiagram detection

PASS: side=left, subloop=l, external momentum=p' - \left(k\right)

## Left self-energy numerator extracted from raw RHS

$$
4\left(m\right) - 2\left(\rlap{/}\left(p' - \left(k\right)\right)\right) + 2\left(\rlap{/}l\right)
$$

## Left compact bare outer diagram

$$
\frac{e^{2}}{(2\pi)^4 i}\,\int d^{4}k\,\gamma^{\rho}\,\frac{1}{m - \left(\rlap{/}p'\right) + \rlap{/}k - \left(i\,\varepsilon\right)}\,\Sigma^{(1)}\left(p' - \left(k\right)\right)\,\frac{1}{m - \left(\rlap{/}p'\right) + \rlap{/}k - \left(i\,\varepsilon\right)}\,\gamma_{\mu}\,\frac{1}{m - \left(\rlap{/}p\right) + \rlap{/}k - \left(i\,\varepsilon\right)}\,\gamma^{\sigma}\,\left(-\left(g_{\rho\sigma} + \left(1 - \left(\alpha\right)\right)\,\frac{k_{\rho}\,k_{\sigma}}{-\left(k\cdot k\right) - \left(i\,\varepsilon\right)}\right)\,\frac{1}{-\left(k\cdot k\right) - \left(i\,\varepsilon\right)}\right)
$$

## Self-energy subloop numerator input

$$
\gamma^{\alpha}\,\left(m + \rlap{/}r - \left(\rlap{/}l\right)\right)\,\gamma_{\alpha}
$$

## After expansion and gamma contraction

$$
4\left(m\right) - 2\left(\rlap{/}r\right) + 2\left(\rlap{/}l\right)
$$

## After l = t + a r

$$
4\left(m\right) - 2\left(\rlap{/}r\right) + 2\left(\rlap{/}t\right) + 2\left(a\,\rlap{/}r\right)
$$

## After removing odd t terms

$$
4\left(m\right) - 2\left(\rlap{/}r\right) + 2\left(a\,\rlap{/}r\right)
$$

## Self-energy denominator

$$
a m^{2} + a r_{2} \left(a - 1\right) + \lambda^{2} \left(1 - a\right)
$$

## On-shell denominator

$$
a^{2} m^{2} + \lambda^{2} \left(1 - a\right)
$$

## UV numerator after on-shell counterterms

$$
0
$$

## UV cancellation check

PASS

## Right compact renormalized outer diagram

$$
\frac{e^{2}}{(2\pi)^4 i}\,\int d^{4}k\,\gamma^{\rho}\,\frac{1}{m - \left(\rlap{/}p'\right) + \rlap{/}k - \left(i\,\varepsilon\right)}\,\gamma_{\mu}\,\frac{1}{m - \left(\rlap{/}p\right) + \rlap{/}k - \left(i\,\varepsilon\right)}\,\Sigma_R^{(1)}\left(p - \left(k\right)\right)\,\frac{1}{m - \left(\rlap{/}p\right) + \rlap{/}k - \left(i\,\varepsilon\right)}\,\gamma^{\sigma}\,\left(-\left(g_{\rho\sigma} + \left(1 - \left(\alpha\right)\right)\,\frac{k_{\rho}\,k_{\sigma}}{-\left(k\cdot k\right) - \left(i\,\varepsilon\right)}\right)\,\frac{1}{-\left(k\cdot k\right) - \left(i\,\varepsilon\right)}\right)
$$

## Left compact renormalized outer diagram

$$
\frac{e^{2}}{(2\pi)^4 i}\,\int d^{4}k\,\gamma^{\rho}\,\frac{1}{m - \left(\rlap{/}p'\right) + \rlap{/}k - \left(i\,\varepsilon\right)}\,\Sigma_R^{(1)}\left(p' - \left(k\right)\right)\,\frac{1}{m - \left(\rlap{/}p'\right) + \rlap{/}k - \left(i\,\varepsilon\right)}\,\gamma_{\mu}\,\frac{1}{m - \left(\rlap{/}p\right) + \rlap{/}k - \left(i\,\varepsilon\right)}\,\gamma^{\sigma}\,\left(-\left(g_{\rho\sigma} + \left(1 - \left(\alpha\right)\right)\,\frac{k_{\rho}\,k_{\sigma}}{-\left(k\cdot k\right) - \left(i\,\varepsilon\right)}\right)\,\frac{1}{-\left(k\cdot k\right) - \left(i\,\varepsilon\right)}\right)
$$

## Rationalized logarithm prefactor

$$
- a \left(a - 1\right) \left(m^{2} - r_{2}\right)
$$

## Rationalized logarithm denominator

$$
a^{2} m^{2} - a z \left(a - 1\right) \left(m^{2} - r_{2}\right) + \lambda^{2} \left(1 - a\right)
$$

## Finite four-parameter integrand G_A

$$
\frac{\left(a - 1\right) \left(b - q\right) \left(q - 1\right) \left(4 a^{2} b q + 2 a^{2} b - 3 a^{2} q^{3} z - 3 a^{2} q^{2} z - 4 a b q + 4 a b + 6 a q^{3} z + 2 a q^{2} z - 3 q^{3} z + q^{2} z\right)}{\left(a b - q^{2} z \left(a - 1\right)\right)^{2}}
$$

## Analytic b-integrated kernel

$$
\frac{q \left(a - 1\right) \left(q - 1\right) \left(a \left(5 a q + a - 5 q + 7\right) - \left(2 a \left(2 a q + a - 2 q + 2\right) - q z \left(a - 1\right) \left(5 a q + a - 5 q + 7\right)\right) \log{\left(\frac{- a + q z \left(a - 1\right)}{q z \left(a - 1\right)} \right)}\right)}{a^{2}}
$$

## Final one-variable finite kernel

$$
\frac{\frac{a^{2} \left(a - 1\right)^{2}}{4} - \frac{a^{2} \left(\left(1 - 3 a\right) \left(a - 1\right) + 1\right) \log{\left(a \right)}}{6} + \frac{a \left(a - 1\right)}{6} + \frac{\left(a - 1\right) \left(a^{2} \left(1 - 3 a\right) + a + 1\right) \log{\left(1 - a \right)}}{6}}{a^{2} \left(a - 1\right)}
$$

## Finite coefficient numerical value

A_A = -0.5899780222827421454908045555486750630724843581250211812

## Finite coefficient analytic recognition

$$
- \frac{\pi^{2}}{18} - \frac{1}{24}
$$

## Finite coefficient reference

$$
- \frac{\pi^{2}}{18} - \frac{1}{24}
$$

## Finite-part recognition check

PASS

## IR part through O(rho^0)

$$
\log{\left(\rho \right)} + \frac{1}{2}
$$

## Total self-energy-insertion coefficient

$$
\log{\left(\rho \right)} - \frac{\pi^{2}}{18} + \frac{11}{24}
$$

## Equivalent conventional form

$$
A_{\mathrm S}=-\frac12\ln\rho^{-2}+\frac{11}{24}-\frac{\pi^2}{18}
$$
