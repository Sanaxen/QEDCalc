# Topology-to-amplitude and mixed multi-loop tensor demo

Generated: 2026-08-22T09:28:22

## Version

QEDCalc v0.15.0

## Design rule

The topology-to-amplitude bridge uses an explicit ordered factor template. QEDCalc does not reconstruct lost graph ordering from a bare algebraic expression.

## Bare amplitude assembled from topology factors

$$
D_outer\,\gamma^{\rho}\,S_left\,\gamma_{\mu}\,S_right\,\gamma_{\sigma}
$$

## Contracted topology members

`vL, S_left, CT[vertex_sub], S_right, vR, D_outer`

## Amplitude after explicit local vertex replacement

$$
D_outer\,\gamma^{\rho}\,S_left\,\delta Z_{1}\,\gamma_{\mu}\,S_right\,\gamma_{\sigma}
$$

## Two-loop quadratic form

$$
2\left(k\cdot k\right) + 3\left(l\cdot l\right) + 2\left(k\cdot l\right)
$$

## Mixed rank-2 tensor reduction

$$
- \frac{1}{40}\left(Q\,g_{\alpha\beta}\right)
$$

## Mixed rank-4 tensor reduction

$$
Q^{2}\,\left(\frac{1}{2000}\left(g_{\alpha\beta}\,g_{\rho\sigma}\right) + \frac{3}{1000}\left(g_{\alpha\rho}\,g_{\beta\sigma}\right) + \frac{1}{2000}\left(g_{\alpha\sigma}\,g_{\beta\rho}\right)\right)
$$

## Tensor convention

The mixed tensor reducer is used only after square completion, when the loop dependence is through Q = L^T M L. It uses M^{-1} and the isotropic average in n*D dimensions.
