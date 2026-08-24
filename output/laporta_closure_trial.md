# QEDCalc target-aware Laporta closure trial

## 1. Purpose

This trial expands the IBP seed domain around the integrals that actually occur in the ordinary-ladder projector output. It keeps the archived historical 75-term audit route separate from the corrected spin-sum route whose 72-term checkpoint was generated and regression-tested from the raw bare LaTeX input.

A stable unreduced candidate is not yet declared to be a physical master integral. Stability here means that the target-aware neighborhood stops growing and the same candidate set is obtained at all configured exact-rational probe points.

## 2. Exact-rational probes

Probe 1:

$$
D=\frac{37}{10},\qquad z=\frac{2}{5},\qquad m^2=1
$$

Probe 2:

$$
D=\frac{41}{11},\qquad z=\frac{3}{7},\qquad m^2=1
$$

Probe 3:

$$
D=\frac{29}{8},\qquad z=- \frac{1}{3},\qquad m^2=1
$$

## 3. Historical 75-term audit route

Original target monomials: **75**.

Canonical targets after symmetry: **42**.

### Round 0

- canonical seeds: **42**
- symbolic IBP rows after pruning: **332**
- distinct integrals in the row system: **440**
- exact-rational probe pivots: **[286, 286, 286]**
- solved targets: **34/42**
- unreduced targets: **8**
- identical candidate set across probes: **True**

### Round 1

- canonical seeds: **80**
- symbolic IBP rows after pruning: **634**
- distinct integrals in the row system: **838**
- exact-rational probe pivots: **[562, 562, 562]**
- solved targets: **35/42**
- unreduced targets: **7**
- identical candidate set across probes: **True**

Closure status: **stable_candidates**.

Stable unreduced candidates: **7**.

$$
J\left(0,0,0,0,1,1,1\right)
$$

$$
J\left(0,0,0,1,1,1,1\right)
$$

$$
J\left(0,1,0,0,1,0,1\right)
$$

$$
J\left(0,1,1,0,0,0,1\right)
$$

$$
J\left(0,1,1,0,1,0,1\right)
$$

$$
J\left(0,1,1,1,0,0,1\right)
$$

$$
J\left(0,1,1,1,0,1,1\right)
$$

Candidate CSV: `output/ladder_historical_stable_unreduced_candidates.csv`

## 4. Corrected spin-sum route

Original target monomials: **72**.

Canonical targets after symmetry: **40**.

### Round 0

- canonical seeds: **40**
- symbolic IBP rows after pruning: **316**
- distinct integrals in the row system: **423**
- exact-rational probe pivots: **[272, 272, 272]**
- solved targets: **31/40**
- unreduced targets: **9**
- identical candidate set across probes: **True**

### Round 1

- canonical seeds: **84**
- symbolic IBP rows after pruning: **666**
- distinct integrals in the row system: **892**
- exact-rational probe pivots: **[598, 598, 598]**
- solved targets: **34/40**
- unreduced targets: **6**
- identical candidate set across probes: **True**

Closure status: **stable_candidates**.

Stable unreduced candidates: **6**.

$$
J\left(0,0,0,0,1,1,1\right)
$$

$$
J\left(0,0,0,1,1,1,1\right)
$$

$$
J\left(0,1,0,0,1,0,1\right)
$$

$$
J\left(0,1,1,0,0,0,1\right)
$$

$$
J\left(0,1,1,0,1,0,1\right)
$$

$$
J\left(0,1,1,1,0,0,1\right)
$$

Candidate CSV: `output/ladder_corrected_stable_unreduced_candidates.csv`

## 5. Interpretation

The historical route stabilizes at seven unreduced candidates. The corrected spin-sum route stabilizes at six. The corrected route is the physically relevant projector ordering; the historical result is retained only as an audit/regression path.

The six corrected candidates are stable under three independent exact-rational probes and under the implemented target-neighborhood expansion. Further sector completion, additional identities, symbolic coefficient reconstruction, and master-integral boundary data are still required before calling them the final physical master basis.
