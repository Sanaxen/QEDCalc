# QEDCalc IBP / finite Laporta trial

## 1. One-loop sanity check

For the tadpole family $T=k^2-m^2$, QEDCalc generates

$$
D - 2\,J\left(1\right)- 2 m_{2}\,J\left(2\right)=0
$$

Solving the finite system with $J(1)$ protected gives

$$
J\left(2\right)=\frac{D - 2}{2 m_{2}}\,J\left(1\right)
$$

## 2. Ordinary-ladder seven-denominator family

The family is

$$
J(n_K,n_L,n_H,n_1,n_2,n_3,n_4)
$$

with denominator basis $(K,L,H,E_1,E_2,E_3,E_4)$. For the bare seed

$$
J(1,1,0,1,1,1,1)
$$

QEDCalc generates the eight canonical identities from $(\partial_k,\partial_l)$ contracted with $(k,l,p,p\prime)$.

### d/dk · k

$$
-J\left(0,1,0,1,1,1,2\right)-J\left(0,1,0,2,1,1,1\right)+J\left(1,0,0,1,1,2,1\right)+J\left(1,0,0,1,2,1,1\right)-J\left(1,1,-1,1,1,2,1\right)-J\left(1,1,-1,1,2,1,1\right)-J\left(1,1,0,0,2,1,1\right)+D - 4\,J\left(1,1,0,1,1,1,1\right)-J\left(1,1,0,1,1,2,0\right)=0
$$

### d/dk · l

$$
J\left(1,0,0,1,1,1,2\right)-J\left(1,0,0,1,1,2,1\right)-J\left(1,0,0,1,2,1,1\right)+J\left(1,0,0,2,1,1,1\right)+J\left(1,1,0,0,2,1,1\right)-J\left(1,1,0,1,1,0,2\right)+J\left(1,1,0,1,1,1,1\right)+J\left(1,1,0,1,1,2,0\right)-J\left(1,1,0,2,0,1,1\right)+J\left(2,0,0,1,1,1,1\right)-J\left(2,1,-1,1,1,1,1\right)=0
$$

### d/dk · p

$$
-J\left(0,1,0,1,1,1,2\right)-J\left(0,1,0,2,1,1,1\right)-J\left(1,1,-1,1,1,2,1\right)-J\left(1,1,-1,1,2,1,1\right)+J\left(1,1,0,1,1,1,1\right)-2\,J\left(1,1,0,1,1,1,2\right)-2\,J\left(1,1,0,1,1,2,1\right)+J\left(1,1,0,1,2,0,1\right)+z - 2\,J\left(1,1,0,1,2,1,1\right)+J\left(1,1,0,2,1,1,0\right)+z - 2\,J\left(1,1,0,2,1,1,1\right)+J\left(2,1,0,1,1,1,0\right)=0
$$

### d/dk · p'

$$
-J\left(0,1,0,1,1,1,2\right)-J\left(0,1,0,2,1,1,1\right)-J\left(1,1,-1,1,1,2,1\right)-J\left(1,1,-1,1,2,1,1\right)+J\left(1,1,0,0,1,1,2\right)+J\left(1,1,0,1,0,2,1\right)+J\left(1,1,0,1,1,1,1\right)+z - 2\,J\left(1,1,0,1,1,1,2\right)+z - 2\,J\left(1,1,0,1,1,2,1\right)-2\,J\left(1,1,0,1,2,1,1\right)-2\,J\left(1,1,0,2,1,1,1\right)+J\left(2,1,0,0,1,1,1\right)=0
$$

### d/dl · k

$$
J\left(0,2,0,1,1,1,1\right)+J\left(1,0,0,1,1,2,1\right)+J\left(1,0,0,1,2,1,1\right)-J\left(1,1,-1,1,1,2,1\right)-J\left(1,1,-1,1,2,1,1\right)-J\left(1,1,0,0,2,1,1\right)+J\left(1,1,0,1,1,1,1\right)-J\left(1,1,0,1,1,2,0\right)-J\left(1,2,-1,1,1,1,1\right)=0
$$

### d/dl · l

$$
-J\left(1,0,0,1,1,2,1\right)-J\left(1,0,0,1,2,1,1\right)+J\left(1,1,0,0,2,1,1\right)+D - 4\,J\left(1,1,0,1,1,1,1\right)+J\left(1,1,0,1,1,2,0\right)=0
$$

### d/dl · p

$$
J\left(0,2,0,1,1,1,1\right)-J\left(1,1,-1,1,1,2,1\right)-J\left(1,1,-1,1,2,1,1\right)+J\left(1,1,0,1,1,1,1\right)-2\,J\left(1,1,0,1,1,2,1\right)+J\left(1,1,0,1,2,0,1\right)+z - 2\,J\left(1,1,0,1,2,1,1\right)-J\left(1,2,-1,1,1,1,1\right)+J\left(1,2,0,1,1,0,1\right)-J\left(1,2,0,1,1,1,0\right)=0
$$

### d/dl · p'

$$
J\left(0,2,0,1,1,1,1\right)-J\left(1,1,-1,1,1,2,1\right)-J\left(1,1,-1,1,2,1,1\right)+J\left(1,1,0,1,0,2,1\right)+J\left(1,1,0,1,1,1,1\right)+z - 2\,J\left(1,1,0,1,1,2,1\right)-2\,J\left(1,1,0,1,2,1,1\right)-J\left(1,2,-1,1,1,1,1\right)-J\left(1,2,0,0,1,1,1\right)+J\left(1,2,0,1,0,1,1\right)=0
$$

## 3. Finite Laporta elimination on the base-seed system

Distinct integrals appearing in the eight equations: **31**.

Pivots solved by the finite sparse eliminator: **8**.

Integrals left unsolved in this deliberately small system: **23**.

The bare seed itself can already be solved in this finite system as

$$
J(1,1,0,1,1,1,1)=\frac{1}{D - 4}\,J\left(1,0,0,1,1,2,1\right)+\frac{1}{D - 4}\,J\left(1,0,0,1,2,1,1\right)- \frac{1}{D - 4}\,J\left(1,1,0,0,2,1,1\right)- \frac{1}{D - 4}\,J\left(1,1,0,1,1,2,0\right)
$$

## 4. Sector ordering and zero-sector detection

Structurally scaleless sector IDs detected in the ordinary-ladder family: **[0, 1, 2, 3, 4, 5, 6, 7]**.

These are the sectors built only from the massless loop-only denominators $K,L,H$; sectors containing any $E_i$ are not discarded by this conservative test.

## 5. First-neighbor forward sparse Laporta

Generated seeds: **8**.

Generated IBP equations: **64**.

Distinct integrals in the first neighborhood: **181**.

Forward sparse pivots solved: **63**.

Unsolved integrals in this finite domain: **118**.

The unsolved count is not a physical master-integral count; the seed domain is not closed yet.

## 6. Bounded seed closure

Degree-2 bounded seeds: **36**.

Degree-2 IBP equations: **288**.

Distinct integrals appearing at degree 2: **623**.

Degree 2 is generated symbolically; the next subsection applies graph symmetries and a generic rational-point probe before elimination.

## 7. Ordinary-ladder family symmetry

Symmetry-group order: **4**.

Degree-2 seeds before/after canonicalization: **36 -> 24**.

Distinct degree-2 integrals before/after canonicalization: **623 -> 335**.

The generators are external exchange $p\leftrightarrow p\prime$ and the unit-Jacobian loop reparametrization $k\to k+l$, $l\to-l$.

## 8. Generic rational-point rank probe

For a fast rank diagnostic only, coefficients are specialized to

$$
D=\frac{37}{10},\qquad z=\frac25,\qquad m^2=1
$$

Forward sparse pivots at this generic exact-rational point: **162**.

Unsolved integrals in the finite degree-2 probe domain: **173**.

This probe does not replace the symbolic reduction; it is a fast rank/closure diagnostic.

## 9. Automation boundary

This version contains conservative zero-sector detection, sector-aware ranking, bounded seed domains, and a forward sparse Laporta eliminator that can process the full 64-equation first neighborhood. Graph symmetries are now included. Complete iterative closure to a stable symbolic master basis, coefficient reconstruction from generic probes, and master-integral boundary data remain future work.
