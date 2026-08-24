# Phase 21: automatic crossed-ladder P_X generation

The long projective numerator is reconstructed from the raw crossed Dirac chain; no stored P_X table is read.

## Streaming route

1. Differentiate the two p'=p+q electron numerators before distributing the Dirac chain.
2. Apply the Breit magnetic projector at O(q).
3. Include the q-linear denominator correction D^-6 -> D^-6 - 6 deltaD D^-7.
4. Wick rotate and square-complete both loop momenta.
5. Reduce centered monomials by bivariate Gaussian/Wick moments term by term.
6. Collect only by powers of Delta and W, then form the common denominator.

P_X monomials: **244**.

Total degree: **8**; homogeneous: **True**.

Projective P_X monomials after scale removal: **227**.

## Exact checks

Apparent Gamma(0) coefficient after the full sum: **0**.

Graph-reversal difference x<->z, u<->v: **0**.

deg_V(projective P_X) = **4**. Since Delta^4 W^2 has V-degree 6, the V-integrand is O(V^-2); the logarithmic 1/V coefficient therefore vanishes.

The generated integrand is

$$
G_{\mathrm X}=\frac{yP_{\mathrm X}}{4\Delta^4W^2}.
$$

The complete 244-term polynomial is written to output/crossed_PX_generated.txt rather than expanded inline here.
