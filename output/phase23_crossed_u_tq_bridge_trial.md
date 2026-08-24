# Phase 23: crossed-ladder analytic U integration and triangular bridge

After V integration use h=S(R+U)-1. The original S>=1 domain gives

$$
0\le U\le h-R+1.
$$

With Y=R+U, every generated U integrand is polynomial(Y)/Y^p, so the U integral is evaluated exactly by monomial primitives and log((h+1)/R).

After

$$
h=\frac{1-t}{t},\qquad R=\frac{q}{t},
$$

the Jacobian is 1/t^3 and the domain becomes

$$
0<t<q<1.
$$

The generated logarithm argument is

$$
\frac{q^2+(1-2q)t}{q^2(1-t)}.
$$

U-integrated component operation counts: `(286, 195, 100, 105)`

(t,q) component operation counts: `(263, 243, 72, 63)`
