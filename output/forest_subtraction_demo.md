# Zimmermann / BPHZ Forest Demo

## Local Taylor subtraction

### Vertex subdiagram amplitude

$$
7 p^{2} + 5 p + 3
$$

Taylor degree: `0`

Taylor projector result

$$
3
$$

Local BPHZ counterterm

$$
-3
$$

Subtracted subdiagram amplitude

$$
p \left(7 p + 5\right)
$$

### Electron self-energy subdiagram amplitude

$$
17 q^{2} + 13 q + 11
$$

Taylor degree: `1`

Taylor projector result

$$
13 q + 11
$$

Local BPHZ counterterm

$$
- 13 q - 11
$$

Subtracted subdiagram amplitude

$$
17 q^{2}
$$

## Contracted graph metadata

### Forest: empty forest

```text
Members: e1, e2, e3, e4, tail, v1, v4
```

### Forest: gamma_V

```text
Members: CT[gamma_V], e3, e4, tail, v4
```

### Forest: gamma_SE

```text
Members: CT[gamma_SE], e1, e2, e3, tail, v1
```

### Forest: gamma_V, gamma_SE

```text
Members: CT[gamma_SE], CT[gamma_V], e3, tail
```

## Forest-formula sign structure

The amplitude provider is explicit; QEDCalc does not infer contracted amplitudes from the bare formula alone.

- `empty forest`: sign = `1`
- `gamma_V`: sign = `-1`
- `gamma_SE`: sign = `-1`
- `gamma_V, gamma_SE`: sign = `1`

Forest sum

$$
I_{G} - I_{G over SE} - I_{G over V} + I_{G over V SE}
$$

## Overlapping-subdiagram check

Relation between `gamma_V` and `gamma_O`: `overlapping`

They cannot appear together in one Zimmermann forest.

## Important design boundary

Topology contraction is automatic after subdiagrams are declared.
Taylor subtraction is automatic after the external variables and subtraction degree are declared.
The algebraic amplitude associated with each contracted graph remains explicit and is supplied by the caller/evaluator.
This avoids reconstructing graph topology from a bare algebraic expression where that information is no longer unique.
