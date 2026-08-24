# Phase 83: complete two-loop regression checkpoint

QEDCalc v0.90.0

## Completion matrix

| Phase | Diagram class | Multiplicity | Status | Release invariant |
| --- | --- | ---: | --- | --- |
| 77 | corner pair | 2 | PASS | sector + soft/hard + IR closure |
| 78 | crossed ladder | 1 | PASS | projector + endpoint + analytic closure |
| 79 | vacuum polarization | 1 | PASS | transversality + OS subtraction + final closure |
| 80 | self-energy insertion pair | 2 | PASS | raw-to-final + IR closure |
| 81 | ordinary ladder | 1 | PASS | 72 -> 40 -> 12 + OS subtraction |
| 82 | seven-diagram total | 7 | PASS | exact transcendental-basis sum |

## Exact seven-diagram basis sum

Basis: `1, pi^2, zeta(3), pi^2 ln 2, ln(1/rho)`

- crossed_ladder: `(1/6, 13/36, 5/4, -5/6, 0)`
- ordinary_ladder: `(11/48, 1/18, 0, 0, 0)`
- corner_pair: `(-67/24, 1/18, -1/2, 1/3, 1)`
- self_energy_pair: `(11/24, -1/18, 0, 0, -1)`
- vacuum_polarization: `(119/36, -1/3, 0, 0, 0)`
- total: `(197/144, 1/12, 3/4, -1/2, 0)`

IR log residual: `0`

Final coefficient:

$$
A_1^{(4)} = \frac{197}{144} + \frac{\pi^2}{12} + \frac34\zeta(3) - \frac{\pi^2}{2}\ln2
$$

Exact basis residual: `0`

## Regression baseline

- ordinary-ladder projector rows: `72`
- ordinary-ladder canonical IBP targets: `40`
- ordinary-ladder terminal master bases: `12`
- diagram count: `7`
- scientific-package-free release audit: `PASS`

## Known unresolved provenance item

The crossed-ladder Karplus--Kroll historical gap has magnitude `1/32`.  Its precise lost term in the 1950 algebra remains unresolved.  This is not an uncertainty in the modern crossed-ladder value and is not used as an input to the two-loop closure.

## Completion status

`TWO-LOOP RELEASE REGRESSION PASS`
