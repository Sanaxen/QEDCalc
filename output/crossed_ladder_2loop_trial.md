# QEDCalc crossed-ladder two-loop trial

Generated: 2026-08-22T10:14:03

## Scope

This trial starts from the independently derived projective/one-variable representation of the crossed-ladder graph. The raw several-hundred-term Dirac reduction is not yet regenerated automatically.

## Projective Delta

$$
R S + R V + S U + U V - 1
$$

## Projective W

$$
R^{2} S + R^{2} V + R S^{2} - 2 R S + S^{2} U
$$

## Linearity check

degree_V(Delta)=1, degree_V(W)=1

## h transformation

$$
\frac{1 - t}{t}
$$

## R transformation

$$
\frac{q}{t}
$$

## Jacobian

$$
\frac{1}{t^{3}}
$$

## Reduced logarithm argument

$$
- \frac{q^{2} - 2 q t + t}{q^{2} \left(t - 1\right)}
$$

## Canonical one-variable kernel

$$
\frac{64 q \left(q - 1\right) \left(\log{\left(q \right)} - \log{\left(1 - q \right)}\right) \left(5 \log{\left(q \right)} + 6\right) + q \left(2 q - 1\right) \left(- 80 \log{\left(q \right)}^{2} + 80 \log{\left(q \right)} + 80 \operatorname{Li}_{2}\left(q\right) - 80 \operatorname{Li}_{2}\left(\frac{2 q - 1}{q}\right) - 41\right) + \left(q - 1\right) \left(2 q - 1\right) \left(- 80 \log{\left(q \right)}^{2} + 160 \log{\left(q \right)} \log{\left(1 - q \right)} - 224 \log{\left(q \right)} + 384 \log{\left(1 - q \right)} - 80 \operatorname{Li}_{2}\left(q\right) + 80 \operatorname{Li}_{2}\left(\frac{2 q - 1}{q}\right) - 271\right)}{96 q \left(q - 1\right) \left(2 q - 1\right)}
$$

## Dilogarithm reflection sum

$$
\frac{\log{\left(q \right)}^{2}}{2} - 2 \log{\left(q \right)} \log{\left(1 - q \right)} + \frac{\log{\left(1 - q \right)}^{2}}{2} + \frac{\pi^{2}}{6}
$$

## q=1/2 sector

$$
- \frac{5 \pi^{2} \log{\left(2 \right)}}{6} - \frac{35 \zeta\left(3\right)}{12} + \pi^{2}
$$

## Endpoint canonical finite part

$$
- \frac{19 \pi^{2}}{36} + \frac{25 \zeta\left(3\right)}{6}
$$

## Endpoint boundary finite part

$$
\frac{1}{6} - \frac{\pi^{2}}{9}
$$

## Endpoint total

$$
- \frac{23 \pi^{2}}{36} + \frac{1}{6} + \frac{25 \zeta\left(3\right)}{6}
$$

## Endpoint divergent-log cancellation

$$
0
$$

## Crossed-ladder final coefficient

$$
- \frac{5 \pi^{2} \log{\left(2 \right)}}{6} + \frac{1}{6} + \frac{5 \zeta\left(3\right)}{4} + \frac{13 \pi^{2}}{36}
$$

## Independent closed-form checkpoint

$$
- \frac{5 \pi^{2} \log{\left(2 \right)}}{6} + \frac{1}{6} + \frac{5 \zeta\left(3\right)}{4} + \frac{13 \pi^{2}}{36}
$$

## Difference

$$
0
$$

## Result

PASS: the analytic crossed-ladder coefficient matches the independent derivation.
