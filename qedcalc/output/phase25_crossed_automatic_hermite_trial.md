# Phase 25: automatic crossed-ladder Hermite reduction

The raw one-variable kernel is reduced without using a stored R,T,U,V,P,Q,Z table.

The generated total-derivative coefficients are:

## R(q)

$$
3/(4*(q - 1)) + 17/(4*(q - 1)**2) + 35/(12*(q - 1)**3) + 1/(4*(q - 1)**4)
$$

## T(q)

$$
-5/(12*(q - 1)) + 4/(3*(q - 1)**2) + 13/(12*(q - 1)**3)
$$

## U(q)

$$
7/(4*(q - 1)) + 31/(6*(q - 1)**2) + 31/(12*(q - 1)**3)
$$

## V(q)

$$
29/(12*(q - 1)) + 1/(4*(q - 1)**2)
$$

## P(q)

$$
3/(32*(2*q - 1)) - 27/(4*(q - 1)) - 23/(6*(q - 1)**2)
$$

## Q(q)

$$
-q/4 - 3/(32*(2*q - 1)) + 13/(12*(q - 1)) - 1/(16*q)
$$

## Z(q)

$$
9*q/16 + 5/(4*(q - 1))
$$

The automatically generated primitive agrees with the audited primitive exactly,

$$
\mathcal G_{\rm auto}(q)-\mathcal G_{\rm audited}(q)=0.
$$

The square-free remainder agrees with the audited canonical kernel exactly,

$$
\mathcal F_{\rm can,auto}(q)-\mathcal F_{\rm can,audited}(q)=0.
$$

Finally,

$$
\mathcal F_{\rm raw}(q)-\frac{d\mathcal G_{\rm auto}}{dq}-\mathcal F_{\rm can,auto}(q)=0.
$$
