# Phase 11: complete z=0 ordinary-ladder basis evaluation

All twelve terminal basis integrals are analytic in the convention-free Euclidean normalization.

## 1. Reduced z=0 T family

At z=0, E1=E4 and E3=E2, so basis 8, 10 and 11 become

$$
T_n=\int\frac{d^Dk\,d^Dl}{L\,H\,E_2\,E_4^n},\qquad n=1,2,3.
$$

The reduced IBP family keeps K as an auxiliary denominator and uses (K,L,H,E2,E4). Degree-1 seeds already pivot T2 and T3.

### T2 reduction

$$
T_2=-\frac{D-3}{2m^2}T_1-\frac{1}{2m^2}A,
$$

where the other lower sector in the raw IBP relation is scaleless and vanishes.

### T3 reduction

$$
T_3=\frac{(D-6)(D-4)(D-3)}{8(m^2)^2(D-5)}T_1+\frac{(D-4)^2}{2(m^2)^2(D-5)}A+\frac{D-4}{4m^2(D-5)}E,
$$

with A and E given by massless two-point subloops followed by generalized on-shell one-loop electron integrals; both are Gamma-function closed forms.

## 2. T1 Cheng-Wu reduction

Write D=4-2 epsilon and choose the Cheng-Wu gauge x_E2+x_E4=1. After integrating the two massless-line parameters, the remaining integral is

$$
\frac{1}{(1-\epsilon)(1-2\epsilon)}\int_0^1dt\,t^{-1+\epsilon}\left[(1-t)^{-1+\epsilon}-(1-t)^{-\epsilon}\right]{}_2F_1(2\epsilon,1;2-\epsilon;t).
$$

Using the Euler-Beta integral, the two terms become 3F2(1). A common upper/lower parameter cancels in each term, leaving Gauss-summable 2F1(1) functions. Hence T1 is Gamma-only.

$$
T_1=\pi^{4-2\epsilon}(m^2)^{-2\epsilon}\Gamma(2\epsilon)\,\mathcal I(\epsilon),
$$

with

$$
\mathcal I(\epsilon)=\frac{1}{(1-\epsilon)(1-2\epsilon)}\left[\frac{\Gamma(\epsilon)^2}{\Gamma(2\epsilon)}\frac{\Gamma(2-\epsilon)\Gamma(1-2\epsilon)}{\Gamma(1-\epsilon)\Gamma(2-2\epsilon)}-\Gamma(\epsilon)\Gamma(1-\epsilon)\frac{\Gamma(2-\epsilon)\Gamma(2-4\epsilon)}{\Gamma(2-3\epsilon)\Gamma(2-2\epsilon)}\right].
$$

## 3. Completion status

- Exact z=0 terminal basis values: **12 / 12**
- Remaining unresolved z=0 basis integrals: **0**
- Basis 8: Cheng-Wu + hypergeometric reduction + Gauss summation
- Basis 10/11: dedicated z=0 symbolic IBP + Gamma lower sectors

Complete evaluation CSV: `output/ladder_12basis_z0_complete_evaluation.csv`

## 4. Boundary of the result

These are convention-free Euclidean scalar-integral values. Overall Minkowski i factors, loop-measure conventions, renormalization-scale factors and the projector/reduction coefficients remain in their respective QEDCalc layers.
