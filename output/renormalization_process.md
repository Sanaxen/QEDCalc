# Renormalization Process Demo

## Bare amplitude

$$
\frac{A}{\epsilon} + B
$$

## Declared UV subdiagram

- Name: `vertex_subgraph_1`
- Kind: `vertex`
- Loop order: `1`

Topology members:

```text
fermion_e2, fermion_e3, photon_k, v2, v3
```

## Counterterm amplitude

$$
- \frac{A}{\epsilon}
$$

## Renormalized sum

$$
B
$$

## Remaining pole part

$$
0
$$

## Finite / regular part

$$
B
$$

## Forest bookkeeping

Compatible forests: `2`

- Forest 1: empty forest
- Forest 2: vertex_subgraph_1

## Design rule

QEDCalc does not infer UV subgraphs from a bare algebraic formula alone.
Subdiagram topology is declared explicitly, while algebraic counterterm amplitudes may be generated or supplied separately.
This keeps the physical renormalization decision inspectable and avoids ambiguous automatic guesses.
