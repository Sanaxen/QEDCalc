# QEDCalc Two-Loop Milestone, Automation Scope, and Remaining Manual Work

## 0. Purpose of this document

This document summarizes the status of the two-loop calculation of the electron anomalous magnetic moment $a_e$ as of QEDCalc v0.90.0, across the five validated sample calculation routes.

Its purpose is to clarify:

- what can now actually be calculated,
- which parts QEDCalc can process automatically,
- where physical judgment and derivation of input expressions by a human are still required,
- how reproducible the seven two-loop diagrams have become,
- and what should be implemented next to increase the degree of automation.

This document does not replace the detailed derivations themselves. For the derivation of individual formulas and the concrete QEDCalc inputs and outputs, see the following five documents.

1. `01_crossed_ladder_QEDCalcサンプル説明書兼計算過程説明書.md`
2. `02_ordinary_ladder_QEDCalcサンプル説明書兼計算過程説明書.md`
3. `03_corner_2図_QEDCalcサンプル説明書兼計算過程説明書.md`
4. `04_self_energy_insertion_2図_QEDCalcサンプル説明書兼計算過程説明書.md`
5. `05_vacuum_polarization_QEDCalcサンプル説明書兼計算過程説明書.md`

---

## 1. Structure of the seven two-loop diagrams

With the classification adopted in this project, the two-loop vertex correction contributing to the electron anomalous magnetic moment consists of the following seven diagrams.

| Class | Number of diagrams |
|---|---:|
| crossed ladder | 1 |
| ordinary ladder | 1 |
| corner | 2 |
| self-energy insertion | 2 |
| vacuum polarization | 1 |
| **Total** | **7** |

Therefore,

$$
1+1+2+2+1=7
$$

At QEDCalc v0.90.0, release checkpoints exist for all five classes and all seven diagrams, and the sum of all seven diagrams can be tested by regression.

---

## 2. Final two-loop result

Write the electron anomalous magnetic moment as

$$
a_e = \frac12 \left( \frac{\alpha}{\pi} \right) + A_1^{(4)} \left( \frac{\alpha}{\pi} \right)^2 + O(\alpha^3)
$$

The seven-diagram QEDCalc checkpoint reconstructs the two-loop coefficient as

$$
\boxed{ A_1^{(4)} = \frac{197}{144} + \frac{\pi^2}{12} + \frac34\zeta(3) - \frac{\pi^2}{2}\ln2 }
$$

In the integrated regression of QEDCalc v0.90.0, the exact coefficients with respect to the basis

$$
1, \quad \pi^2, \quad \zeta(3), \quad \pi^2\ln2, \quad \ln\frac1\rho
$$

are

$$
\boxed{ \left( \frac{197}{144}, \frac1{12}, \frac34, -\frac12, 0 \right) }
$$

The final zero means that the infrared logarithms from the corner and self-energy-insertion diagrams cancel exactly.

---

## 3. What “semi-automatic processing” means

At present, QEDCalc is not a program that accepts an image of a Feynman diagram and automatically returns the final value of $a_e$.

On the other hand, it can mechanically process a large fraction of the work that previously had to be carried out by hand, including Dirac algebra, traces, projectors, Feynman parameterization, tensor reduction, IBP reduction, sector-identity checks, and renormalization residual checks.

Thus, at v0.90.0, the two-loop calculation is “semi-automatic” in the following sense.

$$
\boxed{ \text{The human determines the physical strategy and correct input expression} \longrightarrow \text{QEDCalc performs the large algebraic calculation} \longrightarrow \text{The human checks the physical meaning and connects the result to the next stage} }
$$

This division of responsibility is the present design principle.

---

## 4. Automation-level classification

In this document, each calculation step is classified into one of four levels.

### Level H: Human decision

These are steps that require physical judgment.

Examples include:

- determining the noncommuting order of gamma matrices and propagators from a Feynman diagram,
- choosing the loop-momentum routing,
- identifying which subgraph contains a UV subdivergence,
- deciding which renormalization condition must be imposed,
- deciding how long an IR regulator must be retained,
- choosing a variable transformation or sector decomposition suitable for analytic evaluation.

At present, QEDCalc is intentionally not allowed to guess these steps.

### Level A: Automatic QEDCalc processing

Once a correct input expression and processing instruction are supplied, QEDCalc performs the algebraic manipulation.

Examples include:

- LaTeX parsing,
- propagator and subdiagram detection,
- Dirac traces,
- gamma contractions,
- magnetic projection,
- loop-momentum shifts,
- removal of odd integrands,
- tensor reduction,
- generation of Feynman-parameter families,
- reconstruction of IBP-reduction data,
- exact symbolic residual checks.

### Level C: Human-controlled connection

At this level, a QEDCalc output is passed to the next specialized calculation stage.

Little or no hand algebra may be required, but the human must understand and specify

$$
\text{“what this output is to be used as in the next step.”}
$$

### Level R: Automated release regression

Once a calculation route has been established, QEDCalc rechecks stored invariants and analytic results automatically.

At v0.90.0, the complete two-loop release regression checks, using only the Python standard library:

- diagram count = 7,
- IR log residual = 0,
- ordinary ladder reduction = `72 -> 40 -> 12`,
- exact basis sum of all seven diagrams.

---

## 5. Current automation status for the five diagram classes

### 5.1 Crossed ladder: one diagram

The main calculation route is

$$
\text{raw graph} \longrightarrow \text{magnetic projector} \longrightarrow \text{projective polynomials} \longrightarrow \text{triangular variables} \longrightarrow \text{raw one-variable kernel} \longrightarrow \text{canonical kernel} \longrightarrow \text{endpoint evaluation}
$$

#### Human decisions

- the fermion-chain ordering of the crossed-ladder graph,
- loop-momentum routing,
- the physical meaning of the projector extracting $F_2(0)$,
- adoption of the variable transformation from the projective representation to a triangular domain,
- the strategy for separating and treating endpoint singularities.

#### QEDCalc processing

- parsing the raw LaTeX expression,
- constructing the crossed-ladder denominator/projective family,
- generating the projector table,
- exact checks of the Jacobian and logarithm argument,
- constructing the raw one-variable kernel,
- Hermite/total-derivative reduction,
- checking cancellation between endpoint sectors and boundary terms,
- checkpointing the final analytic coefficient.

The final result is

$$
\boxed{ A_{\mathrm X} = \frac16 + \frac{13\pi^2}{36} + \frac54\zeta(3) - \frac{5\pi^2}{6}\ln2 }
$$

#### Remaining manual work

The largest remaining manual component is the choice of momentum routing and variable transformation when translating the raw Feynman graph into the crossed-ladder calculation route.

The historical origin of the $1/32$ discrepancy in the Karplus--Kroll result remains unresolved. This does not mean that the modern crossed-ladder value is uncertain.

---

### 5.2 Ordinary ladder: one diagram

The ordinary ladder is one of the most algebraically demanding examples among the seven two-loop diagrams.

The calculation proceeds as

$$
\text{raw graph} \longrightarrow D\text{-dimensional projector} \longrightarrow \text{scalar integrals} \longrightarrow 72\text{ projector terms} \longrightarrow 40\text{ canonical targets} \longrightarrow 12\text{ master basis} \longrightarrow \text{bare coefficient} \longrightarrow \text{on-shell subtraction}
$$

#### Human decisions

- why the calculation must be performed in $D$ dimensions,
- the projector ansatz,
- the strategy of separating the $q\to0$ limit into $A_0$ and $C_1=B_1-2A_1$,
- which one-loop counterterm must be combined in the on-shell renormalization.

#### QEDCalc processing

- $D$-dimensional gamma traces,
- solving the linear equations that determine the projector coefficients,
- expansion into scalar integrals,
- generation of 72 projector terms,
- organization into 40 canonical IBP targets,
- reduction to 12 terminal master integrals,
- reconstruction of the bare finite coefficient,
- assembly of the one-loop subtraction series,
- exact checkpoint of the renormalized coefficient.

The bare result is reconstructed as

$$
A_{\mathrm L,bare} = -\frac{3}{4(D-4)} + \frac{107}{48} + \frac{\pi^2}{18} + O(D-4)
$$

After on-shell subtraction,

$$
\boxed{ A_{\mathrm L} = \frac{11}{48} + \frac{\pi^2}{18} }
$$

#### A representative example of two-loop semi-automation

The ordinary-ladder reduction

$$
72 \longrightarrow 40 \longrightarrow 12
$$

clearly demonstrates the value of QEDCalc.

A human no longer needs to expand and classify all 72 terms manually or track the complete IBP-reduction chain by hand.

However, the choice of projector and the reason that the chosen $q\to0$ expansion is valid remain human responsibilities.

---

### 5.3 Corner: two diagrams

The corner pair is difficult not merely because of long algebra, but because it involves a UV subdivergence, a renormalized inner vertex, soft/hard sectors, and an IR regulator.

The route is

$$
\text{raw pair} \longrightarrow \text{topology audit} \longrightarrow \text{magnetic projector} \longrightarrow \text{parametric family} \longrightarrow \text{UV local subtraction} \longrightarrow \text{renormalized sectors} \longrightarrow \text{soft/hard split} \longrightarrow \text{IR asymptotic}
$$

#### Human decisions

- the noncommuting ordering of the two diagrams,
- the decision that the inner vertex subgraph must be renormalized,
- the physical meaning of the local UV counterterm,
- introduction of the photon-mass regulator

$$
\rho=\frac{\lambda}{m}
$$

and the requirement not to set $\rho=0$ prematurely,
- the physical separation into soft and hard sectors.

#### QEDCalc processing

- reading the two raw LaTeX files and auditing their topology,
- generating the first-order-in-$q$ magnetic-projector polynomial,
- generating the Feynman-parameter family and square-completion data,
- exactly comparing the bare UV residue with the local counterterm residue,
- checking renormalized sector identities,
- extracting the soft kernel and the coefficient of the IR logarithm,
- combining the momentum-shift correction, hard sector, and $z$ sector,
- exact checking of soft/hard ownership,
- checking IR cancellation after combination with the self-energy insertion.

The sum of the two corner diagrams is

$$
A_{\mathrm C} = \ln\frac1\rho - \frac{67}{24} + \frac{\pi^2}{18} - \frac12\zeta(3) + \frac{\pi^2}{3}\ln2 + o(1)
$$

The finite part is

$$
\boxed{ A_{\mathrm C,fin} = -\frac{67}{24} + \frac{\pi^2}{18} - \frac12\zeta(3) + \frac{\pi^2}{3}\ln2 }
$$

#### Remaining manual work

For the corner graphs, important physical decisions remain on the human side, including which subgraph is to be treated as the renormalized inner vertex and which sector is to be separated as soft.

---

### 5.4 Self-energy insertion: two diagrams

For the self-energy-insertion pair, QEDCalc detects the internal self-energy subdiagram in the two raw diagrams, contracts it, renormalizes the self-energy on shell, and reinserts it into the outer vertex graph.

The route is

$$
\text{raw pair} \longrightarrow \text{self-energy subdiagram detection} \longrightarrow \Sigma\text{ numerator reduction} \longrightarrow \Sigma_R\text{ on-shell subtraction} \longrightarrow \text{outer insertion} \longrightarrow \text{finite part + IR part}
$$

#### Human decisions

- the Feynman-rule ordering for the left and right insertions,
- the on-shell renormalization condition,
- the requirement to perform UV subtraction of the self-energy before reinserting it into the outer loop,
- the requirement not to set $\rho=0$ before taking the IR asymptotic form.

#### QEDCalc processing

- pattern detection of the self-energy subdiagram inside the raw diagram,
- subdiagram contraction,
- gamma contraction,
- loop shift and odd-term removal,
- auditing UV cancellation,
- generation of the compact outer diagram,
- staged integration of the finite kernel,
- extraction of the IR asymptotic part,
- raw-to-final auditing,
- checking cancellation of the IR logarithm against the corner contribution.

The result is

$$
A_{\mathrm S}(\rho) = \ln\rho + \frac{11}{24} - \frac{\pi^2}{18} + o(1)
$$

and therefore

$$
\boxed{ A_{\mathrm S,fin} = \frac{11}{24} - \frac{\pi^2}{18} }
$$

Combined with the corner IR term,

$$
\ln\frac1\rho + \ln\rho = 0
$$

This cancellation is checked exactly by the v0.90.0 regression.

---

### 5.5 Vacuum polarization: one diagram

Vacuum polarization is a comparatively advanced example of the connection between topology and algebra in QEDCalc because the closed electron loop can be recognized automatically.

The route is

$$
\text{complete raw graph} \longrightarrow \text{closed trace detection} \longrightarrow \text{Dirac trace} \longrightarrow \text{tensor reduction} \longrightarrow \Pi_R(k^2) \longrightarrow \text{outer magnetic kernel} \longrightarrow \text{analytic integration}
$$

#### Human decisions

- the complete raw Feynman-rule expression,
- the physical meaning of the transverse form of the vacuum-polarization tensor,
- adoption of the on-shell charge-renormalization condition

$$
\Pi_R(0)=0
$$

- insertion of the renormalized scalar vacuum-polarization function into the outer photon propagator.

#### QEDCalc processing

- parsing the complete raw diagram,
- detecting the closed Dirac trace,
- scalarizing propagators,
- performing the four-dimensional Dirac trace,
- loop shift,
- removal of odd terms,
- rank-2 tensor reduction,
- checking the transversality residual,
- constructing the finite kernel after on-shell subtraction,
- constructing the two-variable outer magnetic kernel,
- integrating over $z$ to obtain a one-variable kernel,
- checking the primitive derivative and endpoint evaluation.

The final result is

$$
\boxed{ A_{\mathrm{VP}} = \frac{119}{36} - \frac{\pi^2}{3} }
$$

#### Present status

Because QEDCalc can detect the closed electron loop starting from the complete raw LaTeX expression, vacuum polarization is one of the five classes with the most advanced raw-input automation.

However, the physical interpretation of the transverse decomposition and the choice of renormalization condition remain human responsibilities.

---

## 6. Automation-status table for the five diagram classes

| Diagram class | Raw-expression parsing | Topology/subgraph detection | Dirac/trace | Projector | Parameter/tensor | Renormalization | Final analytic checkpoint | Main human decisions |
|---|---|---|---|---|---|---|---|---|
| crossed ladder | Yes | Partial | Yes | Yes | Yes | Yes | Yes | routing, variable transformation, endpoint split |
| ordinary ladder | Yes | Partial | Yes | Yes | Yes | Yes | Yes | $D$-dimensional projector, $A_0/C_1$ separation |
| corner, 2 diagrams | Yes | Yes | Yes | Yes | Yes | Yes | Yes | inner subgraph, soft/hard split, IR regulator |
| self-energy insertion, 2 diagrams | Yes | Yes | Yes | Yes | Yes | Yes | Yes | on-shell conditions, reinsertion into outer graph |
| vacuum polarization | Yes | Yes | Yes | Yes | Yes | Yes | Yes | transverse form, charge renormalization |

Here, “Partial” means that the topology or family must still be specified explicitly by the user.

This table must not be interpreted as meaning that any unknown two-loop graph can be processed fully automatically.

The current automation means that **validated specialized routes exist for all seven two-loop diagrams considered here**.

---

## 7. How much human work has been eliminated?

In a fully manual calculation, a human would traditionally have to perform work such as:

- expanding tens to hundreds of gamma-matrix terms,
- large Dirac-trace expansions,
- Lorentz-index contractions,
- re-expanding numerators after loop-momentum shifts,
- removing odd terms,
- symmetric tensor integration,
- organizing Feynman-parameter denominators,
- expanding projectors in $q$,
- extensive IBP bookkeeping,
- checking UV-pole cancellation,
- comparing IR-log coefficients,
- checking endpoint-singularity cancellation.

With QEDCalc, much of this work is replaced by the requirement to prepare the correct input expression.

Therefore, the written calculation record no longer needs to preserve every large algebraic expansion.

In future derivation documents, it is generally sufficient to retain

$$
\boxed{ \text{why the input expression is needed} \;+\; \text{how the input expression is derived} \;+\; \text{the QEDCalc input and output} }
$$

while omitting long purely algebraic expansions that QEDCalc can reproduce.

This is also the basic philosophy of the five newly prepared “QEDCalc sample manual and calculation-process guide” documents.

---

## 8. What must still be documented by humans

Even as automation improves, the following parts must not disappear from the documentation.

### 8.1 How the input expression is constructed from the original Feynman diagram

Fermion propagators and gamma matrices are noncommuting.

Therefore, the ordering of factors derived from the diagram must always be explained explicitly by a human.

### 8.2 Why a particular projector is used

Even if QEDCalc can carry out the projector algebra, the documentation must explain why

$$
F_2(0)
$$

corresponds to the anomalous magnetic moment and why the projector eliminates $F_1$ while extracting $F_2$.

### 8.3 Renormalization target and conditions

Even when QEDCalc can exactly check a counterterm residual, the documentation must state:

- which subgraph is being renormalized,
- which condition of the on-shell scheme is used,
- the physical meaning of the subtraction.

### 8.4 When the IR regulator may be removed

For the corner and self-energy-insertion diagrams in particular, one must not set $\rho\to0$ in each diagram separately.

The important combination is

$$
A_{\mathrm C}^{\mathrm{IR}} = \ln\frac1\rho
$$

with

$$
A_{\mathrm S}^{\mathrm{IR}} = \ln\rho
$$

before taking the limit.

### 8.5 Why a variable transformation or sector decomposition is chosen

A computer may verify the transformation algebraically, but the reason for choosing that representation should be retained for future readers.

---

## 9. Regression structure achieved in v0.90.0

QEDCalc v0.90.0 can verify that the completed two-loop calculation has not been broken by running

`run_v090_validation.bat`

The standard-library release regression checks

```text
Phase-83 complete two-loop regression PASS
diagram count = 7
IR log residual = 0
ordinary ladder reduction = 72 -> 40 -> 12
total basis coefficients = ('197/144', '1/12', '3/4', '-1/2', '0')
historical 1/32 origin resolved = False
QEDCalc 0.90.0
v0.90 validation PASS
```

This is an important milestone.

Even after future additions such as three-loop support or further generalization, the v0.90 regression can be rerun to confirm that no regression has been introduced into the completed two-loop calculation.

---

## 10. Parts that are not yet fully automatic

The fact that all seven two-loop diagrams can now be calculated does not mean that arbitrary two-loop Feynman graphs can be solved fully automatically.

The main remaining non-automatic components are as follows.

### 10.1 Automatic topology recognition directly from the Feynman graph

At present, the user normally supplies a LaTeX expression already written according to the Feynman rules.

In the future, if graph-topology data could automatically generate

- fermion-chain ordering,
- photon connections,
- momentum routing,
- symmetry/sign factors,

the initial human workload would be reduced significantly.

### 10.2 Automatic renormalization planning for arbitrary subgraphs

Pattern detection for specific self-energy and vacuum-polarization subgraphs is already implemented.

For an arbitrary graph, however, a fully automatic route

$$
\text{divergent subgraphs} \longrightarrow \text{forest} \longrightarrow \text{local counterterms}
$$

together with automatic construction of the correct on-shell counterterms remains future work.

### 10.3 Automatic selection of optimal parameterization and variable transformations

For the crossed ladder and corner graphs, the human still chooses transformations that make the analytic calculation manageable.

This becomes increasingly important at higher loop order.

### 10.4 General automatic evaluation of master integrals

For the ordinary ladder, reduction to 12 master integrals has been achieved.

For a general graph, automatic analytic evaluation of previously unknown master integrals is a separate problem.

### 10.5 Automatic recognition of the final analytic-constant basis

The current checkpoints use known structures such as $\pi^2$, $\zeta(3)$, and $\pi^2\ln2$.

At higher loop order, more complicated harmonic polylogarithms, multiple zeta values, elliptic integrals, and other structures may appear.

---

## 11. Recommended priorities for further automation

Before or alongside the move to three loops, the following order is useful if the goal is to increase the degree of automation.

### Priority 1: Generalize raw graph to ordered amplitude

One of the most error-prone human steps is constructing the noncommuting factor order from the Feynman graph.

Generating this automatically from a topology object would provide a major improvement.

### Priority 2: Generalize subgraph detection into a renormalization plan

Extend the current self-energy and vacuum-polarization detection so that QEDCalc can propose

$$
\text{graph} \longrightarrow \text{UV-divergent subgraphs} \longrightarrow \text{required counterterms}
$$

### Priority 3: Unify projector construction

The magnetic-projector routes currently used separately for the ordinary ladder, crossed ladder, and corner calculations should be consolidated into a more unified API.

### Priority 4: Build a library of parameter and sector strategies

The successful two-loop variable transformations, soft/hard splits, and endpoint-handling strategies should be retained as reusable strategies.

### Priority 5: Extend to three loops

Using the machinery above, the goal should be to increase the fraction of the 72 three-loop diagrams that can be passed through common topology, subgraph, projector, and reduction machinery rather than building every route independently.

---

## 12. Design principles that should carry over to three loops

The two-loop implementation suggests the following principles.

### 12.1 Do not turn the calculation into a black box

Do not return only the final numerical value.

Instead, save

$$
\text{input} \longrightarrow \text{intermediate invariant} \longrightarrow \text{output}
$$

at every important stage.

### 12.2 Separate human physical judgment from machine algebra

QEDCalc should not silently guess physical choices.

Human decisions should be supplied explicitly as inputs, and only the mechanical processing after those decisions should be automated.

### 12.3 Keep an exact residual at each stage

Whenever possible, use a symbolic residual equal to zero as the checkpoint, rather than relying on visual similarity or approximate numerical agreement.

### 12.4 Do not escape directly to numerical integration

Because UV divergences, subtractions, and IR cancellations are present, high-loop integrals should not be sent directly to raw numerical integration before the algebraic structure has been organized.

### 12.5 Do not separate the derivation document too far from the program manual

As in the five sample manuals prepared for the two-loop calculation, it is more reproducible to connect within the same document:

- the input expression derived by the human,
- the QEDCalc code,
- the QEDCalc output,
- and how that output is used in the next step.

---

## 13. Current assessment

At QEDCalc v0.90.0, the seven two-loop diagrams can reasonably be described as having moved from

$$
\boxed{ \text{fully manual calculation} \longrightarrow \text{semi-automatic calculation in which the human directs the physics and QEDCalc performs the algebra} }
$$

The important point is that the program does not merely contain the known final result.

Each diagram class passes through its own distinct difficulty:

- the projective and endpoint treatment of the crossed ladder,
- the $D$-dimensional projector and `72 -> 40 -> 12` reduction of the ordinary ladder,
- the UV subdivergence and soft/hard ownership of the corner pair,
- the subdiagram contraction and IR asymptotic of the self-energy insertion,
- the closed-loop trace and transversality of vacuum polarization.

These are then integrated into the exact sum of all seven diagrams.

At the same time, the most intellectual parts of the calculation,

$$
\boxed{ \text{what should be calculated, which physical structures should be separated, and which representation should be chosen} }
$$

are still human responsibilities.

Therefore, QEDCalc is not currently “a program that automatically solves QED.”

A more accurate description is

$$
\boxed{ \text{a computational framework for semi-automating higher-order QED perturbation theory while keeping the calculation human-trackable} }
$$

---

## 14. Fixed checkpoints at two-loop completion

Even after work proceeds to three loops and beyond, the following values should remain fixed checkpoints for the two-loop implementation.

### Crossed ladder

$$
A_{\mathrm X} = \frac16 + \frac{13\pi^2}{36} + \frac54\zeta(3) - \frac{5\pi^2}{6}\ln2
$$

### Ordinary ladder

$$
A_{\mathrm L} = \frac{11}{48} + \frac{\pi^2}{18}
$$

### Corner pair

$$
A_{\mathrm C} = \ln\frac1\rho - \frac{67}{24} + \frac{\pi^2}{18} - \frac12\zeta(3) + \frac{\pi^2}{3}\ln2
$$

### Self-energy-insertion pair

$$
A_{\mathrm S} = \ln\rho + \frac{11}{24} - \frac{\pi^2}{18}
$$

### Vacuum polarization

$$
A_{\mathrm{VP}} = \frac{119}{36} - \frac{\pi^2}{3}
$$

### IR cancellation

$$
\ln\frac1\rho + \ln\rho = 0
$$

### Sum of all seven diagrams

$$
\boxed{ A_1^{(4)} = \frac{197}{144} + \frac{\pi^2}{12} + \frac34\zeta(3) - \frac{\pi^2}{2}\ln2 }
$$

These values should continue to be used as the reference values for regression testing of the QEDCalc two-loop implementation.

---

## 15. Related files

### Sample calculation manuals

- `01_crossed_ladder_QEDCalcサンプル説明書兼計算過程説明書.md`
- `02_ordinary_ladder_QEDCalcサンプル説明書兼計算過程説明書.md`
- `03_corner_2図_QEDCalcサンプル説明書兼計算過程説明書.md`
- `04_self_energy_insertion_2図_QEDCalcサンプル説明書兼計算過程説明書.md`
- `05_vacuum_polarization_QEDCalcサンプル説明書兼計算過程説明書.md`

### QEDCalc release checkpoints

- Phase 77: corner end-to-end closure
- Phase 78: crossed-ladder end-to-end closure
- Phase 79: vacuum-polarization end-to-end closure
- Phase 80: self-energy-insertion end-to-end closure
- Phase 81: ordinary-ladder end-to-end closure
- Phase 82: seven-diagram release audit
- Phase 83: complete two-loop regression

### Complete two-loop regression

`run_v090_validation.bat`

---

# Conclusion

For all seven two-loop diagrams, QEDCalc v0.90.0 has achieved

$$
\boxed{ \text{semi-automatic processing in which the human understands and specifies the calculation route while QEDCalc handles the difficult algebra} }
$$

This is more than an improvement in calculation speed.

By moving large volumes of hand algebra into reproducible code, the human can concentrate on

$$
\boxed{ \text{physical judgment, correctness of the input expression, correct connection between stages, and final consistency} }
$$

which is the most important milestone of the present implementation.
