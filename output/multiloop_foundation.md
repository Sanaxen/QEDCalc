# QEDCalc multi-loop foundation demo

Generated: 2026-08-22T11:08:34

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

## Purpose

Reusable algebra foundation for two-loop and higher-loop calculations. This demo verifies individual processing functions; it is not yet a complete two-loop diagram evaluation.

## Declared loop momenta

$$
\left\{k, l\right\}
$$

## Input quadratic form

$$
-\left(k\cdot k\right) - \left(l\cdot l\right) + k\cdot l + 2\left(k\cdot p\right) + 4\left(l\cdot q\right) + m\,m
$$

## Matrix square completion

$$
\left(\begin{pmatrix}k \\ l\end{pmatrix} + \begin{pmatrix}- \frac{4}{3}\,p -  \frac{4}{3}\,q \\ - \frac{2}{3}\,p -  \frac{8}{3}\,q\end{pmatrix}\right)^T \begin{pmatrix}-1 & \frac{1}{2} \\ \frac{1}{2} & -1\end{pmatrix}\left(\begin{pmatrix}k \\ l\end{pmatrix} + \begin{pmatrix}- \frac{4}{3}\,p -  \frac{4}{3}\,q \\ - \frac{2}{3}\,p -  \frac{8}{3}\,q\end{pmatrix}\right) + \frac{1}{3}\left(3\left(m^{2}\right) + 4\left(p\cdot p\right) + 8\left(p\cdot q\right) + 16\left(q\cdot q\right)\right)
$$

## Shifted quadratic denominator

$$
ell1\cdot ell2 + m^{2} - \left(ell1\cdot ell1\right) - \left(ell2\cdot ell2\right) + \frac{4}{3}\left(p\cdot p\right) + \frac{8}{3}\left(p\cdot q\right) + \frac{16}{3}\left(q\cdot q\right)
$$

## Input two-loop numerator

$$
\rlap{/}k\,\gamma_{\mu}\,\rlap{/}l
$$

## Simultaneously shifted numerator

$$
\left(\rlap{/}ell1 + \frac{4}{3}\left(\rlap{/}p\right) + \frac{4}{3}\left(\rlap{/}q\right)\right)\,\gamma_{\mu}\,\left(\rlap{/}ell2 + \frac{2}{3}\left(\rlap{/}p\right) + \frac{8}{3}\left(\rlap{/}q\right)\right)
$$

## Five-denominator unit-power Feynman parameterization

$$
24\,\int_{\Delta_{4}} dx1\,dx2\,dx3\,dx4\,\frac{N}{\left[x1\,D1 + x2\,D2 + x3\,D3 + x4\,D4 + \left(1 - \left(x1\right) - \left(x2\right) - \left(x3\right) - \left(x4\right)\right)\,D5\right]^{5}}
$$

## General denominator-power Feynman parameterization

$$
60\,\int_{\Delta_{2}} dx1\,dx2\,\frac{x1^{1}\,\left(1 - \left(x1\right) - \left(x2\right)\right)^{2}\,N}{\left[x1\,D1 + x2\,D2 + \left(1 - \left(x1\right) - \left(x2\right)\right)\,D3\right]^{6}}
$$

## General D-dimensional Euclidean scalar loop integral

$$
\frac{\pi^{\frac{D}{2}} D \Delta^{\frac{D}{2} - 2} \Gamma\left(2 - \frac{D}{2}\right)}{4}
$$

## Dimensional-regularization example around D=4-2 epsilon

$$
- \pi^{2} \log{\left(\Delta \right)} - \pi^{2} \log{\left(\pi \right)} - \gamma \pi^{2} + \frac{\pi^{2}}{\epsilon}
$$

## Vertex counterterm

$$
\underbrace{\delta Z_{1}\,\gamma_{\mu}}_{\delta Z_{1}}
$$

## Explicit counterterm replacement result

$$
\gamma^{\rho}\,\delta Z_{1}\,\gamma_{\mu}\,\gamma_{\rho}
$$

## General rank-6 symmetric tensor reduction

$$
\frac{1}{192}\left(\left(ell1\cdot ell1\right)^{3}\,\left(g_{\mu\nu}\,g_{\rho\sigma}\,g_{\alpha\beta} + g_{\mu\nu}\,g_{\rho\alpha}\,g_{\sigma\beta} + g_{\mu\nu}\,g_{\rho\beta}\,g_{\sigma\alpha} + g_{\mu\rho}\,g_{\nu\sigma}\,g_{\alpha\beta} + g_{\mu\rho}\,g_{\nu\alpha}\,g_{\sigma\beta} + g_{\mu\rho}\,g_{\nu\beta}\,g_{\sigma\alpha} + g_{\mu\sigma}\,g_{\nu\rho}\,g_{\alpha\beta} + g_{\mu\sigma}\,g_{\nu\alpha}\,g_{\rho\beta} + g_{\mu\sigma}\,g_{\nu\beta}\,g_{\rho\alpha} + g_{\mu\alpha}\,g_{\nu\rho}\,g_{\sigma\beta} + g_{\mu\alpha}\,g_{\nu\sigma}\,g_{\rho\beta} + g_{\mu\alpha}\,g_{\nu\beta}\,g_{\rho\sigma} + g_{\mu\beta}\,g_{\nu\rho}\,g_{\sigma\alpha} + g_{\mu\beta}\,g_{\nu\sigma}\,g_{\rho\alpha} + g_{\mu\beta}\,g_{\nu\alpha}\,g_{\rho\sigma}\right)\right)
$$

## Two-loop MS-bar scale factor

$$
\left(16 \pi^{2} \mu_{R}^{4}\right)^{\epsilon} e^{- 2 \gamma \epsilon}
$$

## MS-bar Laurent series before subtraction

$$
C_{0} + 4 \log{\left(\mu_{R} \right)} - 2 \gamma + 2 \log{\left(\pi \right)} + 4 \log{\left(2 \right)} + \frac{1}{\epsilon}
$$

## MS-bar pole part

$$
\frac{1}{\epsilon}
$$

## MS-bar result after minimal subtraction

$$
C_{0} + \log{\left(16 \pi^{2} \mu_{R}^{4} \right)} - 2 \gamma
$$

## UV pole bookkeeping

$$
\frac{A}{\epsilon_{UV}^{2}}
$$

## IR pole bookkeeping

$$
\frac{B}{\epsilon_{IR}}
$$

## Mixed UV/IR pole bookkeeping

$$
\frac{C}{\epsilon_{IR} \epsilon_{UV}}
$$

## QED counterterm library: vertex

$$
\delta Z_{1}\,\gamma_{\mu}
$$

## QED counterterm library: electron_wavefunction

$$
\delta Z_{2}\,\rlap{/}p
$$

## QED counterterm library: mass

$$
\delta m
$$

## QED counterterm library: photon_wavefunction

$$
\delta Z_{3}\,\left(k\cdot k\,g_{\mu\nu} - \left(k_{\mu}\,k_{\nu}\right)\right)
$$
