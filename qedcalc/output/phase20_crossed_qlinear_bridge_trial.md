# Phase 20: crossed-ladder q-linear magnetic-projector bridge

The raw crossed numerator is rewritten with p' = p + q and truncated at first order before the magnetic projector is assembled.

q^0 Dirac-chain terms: **144**.

q^1 Dirac-chain terms: **84** (=48+36).

Total through O(q): **228**.

## q=0 five-denominator Feynman-parameter bridge

At q=0 the two central electron denominators coincide.  The scalar core is therefore K L Dk Dkl^2 Dl and the parameter powers are (1,1,1,2,1).

$$
a=x+y+u,\qquad b=y+z+v,\qquad c=y,\qquad r=x+y,\qquad s=y+z
$$

Automatically generated U:

$$
u v + u y + u z + v x + v y + x y + x z + y z
$$

Automatically generated F at rho=0:

$$
u y^{2} + 2 u y z + u z^{2} + v x^{2} + 2 v x y + v y^{2} + x^{2} y + x^{2} z + x y^{2} + 2 x y z + x z^{2} + y^{2} z + y z^{2}
$$

Feynman-parameter numerator monomial: `$y` (expected y).

Exact checks: U-Delta = 0, F-W = 0, measure-y = 0.

## Breit-frame projector normalization

F1 coefficient: **0**; F2 coefficient: **1**.

## q-linear denominator correction

$$
2 SP^{k q} x + SP^{k q} y + SP^{l q} y
$$

This reproduces delta D = 2 x k.q + y (k+l).q.

The remaining gap to P_X is now isolated to external-spinor O(q), the 84 q-linear numerator chains, loop shifts/tensor reduction, and Gaussian recombination.
