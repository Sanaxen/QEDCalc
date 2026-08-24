# QEDCalc CHANGELOG

This top-level changelog is the concise, newest-first release summary from the v0.90 documentation cleanup onward.

The former cumulative changelog, including the detailed development history of earlier phases, is preserved verbatim at:

```text
doc/archive/CHANGELOG_pre_v090_cleanup.md
```

---

## v0.90.0

### Phase 83 — complete two-loop regression baseline

- Added a durable complete two-loop regression checkpoint.
- Verified diagram count = 7.
- Verified exact corner/self-energy IR-log cancellation.
- Verified ordinary-ladder reduction baseline `72 -> 40 -> 12`.
- Verified the exact seven-diagram coefficient vector in the basis

$$
\left\{
1,
\pi^2,
\zeta(3),
\pi^2\ln2,
\ln\frac1\rho
\right\}
$$

as

$$
\left(
\frac{197}{144},
\frac1{12},
\frac34,
-\frac12,
0
\right).
$$

- Added `data/two_loop_v090_baseline.json`.
- Added `run_v090_validation.bat` as the protected two-loop regression entry point.
- Kept the historical Karplus--Kroll crossed-ladder `1/32` origin explicitly unresolved as a provenance question only.

---

## v0.89.0

### Phase 82 — seven-diagram release audit

- Combined all five two-loop diagram classes into one exact release audit.
- Counted all seven diagrams as `1 + 1 + 2 + 2 + 1`.
- Performed exact basis-coefficient addition with Python `Fraction` arithmetic.
- Verified the final two-loop coefficient

$$
A_1^{(4)}
=
\frac{197}{144}
+\frac{\pi^2}{12}
+\frac34\zeta(3)
-\frac{\pi^2}{2}\ln2.
$$

- Verified exact IR-log residual = 0.

---

## v0.88.2

### Phase 81 validation portability fix

- Reworked ordinary-ladder ZIP validation so that the required release audit uses only the Python standard library.
- Removed mandatory runtime dependence on SymPy/mpmath from the release-validation path.
- Verified projector rows = 72, canonical targets = 40, terminal bases = 12.
- Retained scientific symbolic/high-precision regeneration as an optional extended audit.

---

## v0.88.1

- Fixed the Phase-81 Windows validation path after a direct `mpmath` import caused failure in environments without the package.
- Made high-precision numerical regeneration optional.
- No physics formula or reduction data changed.

---

## v0.88.0

### Phase 81 — ordinary-ladder end-to-end checkpoint

- Connected the corrected 72-term spin-sum projector to 40 symmetry-canonical IBP targets.
- Applied the exact 40-target to 12-basis symbolic reduction.
- Reconstructed the bare ladder coefficient

$$
A_{\mathrm L,bare}
=
-\frac{3}{4(D-4)}
+\frac{107}{48}
+\frac{\pi^2}{18}
+O(D-4).
$$

- Applied the one-loop on-shell subtraction and obtained

$$
A_{\mathrm L}
=
\frac{11}{48}
+\frac{\pi^2}{18}.
$$

- Verified exact leading physical `1/z` projector-pole cancellation.

---

## v0.87.0

### Phase 80 — self-energy-insertion end-to-end checkpoint

- Unified the raw two-diagram self-energy-insertion route into a release checkpoint.
- Audited the raw pair, UV subdivergence, on-shell-renormalized self-energy insertion, finite part, and IR part.
- Fixed the self-energy asymptotic convention as

$$
A_{\mathrm S}(\rho)
=
\ln\rho
+\frac{11}{24}
-\frac{\pi^2}{18}
+o(1).
$$

- Verified exact cancellation with the corner `+ln(1/rho)` term.

---

## v0.86.0

### Phase 79 — vacuum-polarization end-to-end closure

- Unified dimensional transversality, on-shell subtraction `Pi_R(0)=0`, finite `D -> 4` kernel, outer magnetic insertion, primitive derivative, endpoints, and final analytic coefficient.
- Final result:

$$
A_{\mathrm{VP}}
=
\frac{119}{36}
-\frac{\pi^2}{3}.
$$

---

## v0.85.0

### Phase 78 — crossed-ladder end-to-end closure

- Added a fast release checkpoint for the crossed-ladder route.
- Verified Breit-projector `F1/F2` normalization.
- Verified endpoint cutoff-log cancellation.
- Verified half-sector plus endpoint-sector analytic assembly.
- Final result:

$$
A_{\mathrm X}
=
\frac16
+\frac{13\pi^2}{36}
+\frac54\zeta(3)
-\frac{5\pi^2}{6}\ln2.
$$

- Kept the historical Karplus--Kroll `1/32` discrepancy separate from the validated modern result.

---

## v0.84.0

### Phase 77 — corner end-to-end closure

- Unified the corner sector assembly, independent soft/hard ownership assembly, closed-form finite coefficient, and corner/self-energy IR cancellation.
- All analytic residuals are exact zero.
- Final corner asymptotic:

$$
A_{\mathrm C}
=
\ln\frac1\rho
-\frac{67}{24}
+\frac{\pi^2}{18}
-\frac12\zeta(3)
+\frac{\pi^2}{3}\ln2
+o(1).
$$

---

## Earlier development history

Detailed development history before the v0.90 documentation cleanup is preserved in:

```text
doc/archive/CHANGELOG_pre_v090_cleanup.md
```

That archive contains the earlier multi-loop infrastructure, ordinary-ladder IBP/Laporta development, crossed-ladder reconstruction phases, corner phases, raw self-energy/vacuum-polarization bridges, and all intermediate diagnostic work.
