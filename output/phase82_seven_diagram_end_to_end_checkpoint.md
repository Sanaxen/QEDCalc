# Phase 82: seven-diagram end-to-end checkpoint

QEDCalc v0.89.0

## Diagram classes

- crossed ladder: 1 diagram
- ordinary ladder: 1 diagram
- corner: 2 diagrams
- self-energy insertion: 2 diagrams
- vacuum polarization: 1 diagram
- total: 7 diagrams

## Exact transcendental-basis sum

Basis: `1, pi^2, zeta(3), pi^2 ln 2, ln(1/rho)`

- X: `(1/6, 13/36, 5/4, -5/6, 0)`
- L: `(11/48, 1/18, 0, 0, 0)`
- C: `(-67/24, 1/18, -1/2, 1/3, 1)`
- S: `(11/24, -1/18, 0, 0, -1)`
- VP: `(119/36, -1/3, 0, 0, 0)`
- TOTAL: `(197/144, 1/12, 3/4, -1/2, 0)`

IR log residual: `0`

Final coefficient:

$$
A_1^{(4)} = \frac{197}{144} + \frac{\pi^2}{12} + \frac34\zeta(3) - \frac{\pi^2}{2}\ln2
$$

Exact basis residual: `0`
