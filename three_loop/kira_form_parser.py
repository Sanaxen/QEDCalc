"""Parser for Kira ``kira2form`` reduction tables.

The first import stage is deliberately lossless: coefficients are retained as
FORM source text while integral arguments are parsed into integer tuples.  A
later layer can translate coefficient syntax to SymPy only after the complete
Kira table has been structurally validated.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterator


_INTEGRAL_RE = re.compile(r"(?P<family>[A-Za-z_]\w*)\((?P<args>-?\d+(?:\s*,\s*-?\d+)*)\)")
_LHS_RE = re.compile(
    r"^\s*id\s+(?P<family>[A-Za-z_]\w*)\((?P<args>-?\d+(?:\s*,\s*-?\d+)*)\)\s*=\s*(?P<rhs>.*)\s*;\s*$",
    re.S,
)


@dataclass(frozen=True)
class KiraFormIntegral:
    family: str
    indices: tuple[int, ...]

    def text(self) -> str:
        return f"{self.family}({','.join(str(v) for v in self.indices)})"


@dataclass(frozen=True)
class KiraFormTerm:
    coefficient_form: str
    integral: KiraFormIntegral


@dataclass(frozen=True)
class KiraFormRule:
    lhs: KiraFormIntegral
    terms: tuple[KiraFormTerm, ...]
    rhs_form: str

    @property
    def is_zero(self) -> bool:
        return not self.terms and self.rhs_form.strip() in {"0", "+0", "-0"}


def _parse_indices(text: str) -> tuple[int, ...]:
    return tuple(int(part.strip()) for part in text.split(","))


def iter_form_statements(path: str | Path) -> Iterator[str]:
    """Yield semicolon-terminated FORM statements without loading the file.

    Kira emits reduction rules over multiple physical lines.  Semicolon is the
    statement terminator, so line boundaries are not semantically relevant.
    """
    buffer: list[str] = []
    with Path(path).open("r", encoding="utf-8", errors="strict") as handle:
        for line in handle:
            buffer.append(line)
            joined = "".join(buffer)
            while ";" in joined:
                statement, joined = joined.split(";", 1)
                statement = statement.strip()
                if statement:
                    yield statement + ";"
            buffer = [joined] if joined else []
    tail = "".join(buffer).strip()
    if tail:
        raise ValueError(f"unterminated FORM statement at end of file: {tail[:120]!r}")


def _split_top_level_additive_terms(rhs: str) -> list[str]:
    """Split a FORM RHS at additive signs outside all parentheses.

    Kira coefficients can contain ``+`` and ``-`` inside ``num(...)`` or other
    parenthesised factors.  Those signs are part of one coefficient and must
    not split a reduction term.  A leading sign is retained on each returned
    term so the coefficient remains exact.
    """
    text = rhs.strip()
    if not text:
        return []

    terms: list[str] = []
    depth = 0
    start = 0
    for i, ch in enumerate(text):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth < 0:
                raise ValueError("unbalanced parentheses in FORM RHS")
        elif depth == 0 and ch in "+-" and i > start:
            # Do not split an exponent sign such as 1e-10.  FORM/Kira mostly
            # emits exact rational expressions, but keeping this guard costs
            # nothing and makes the structural parser less brittle.
            prev = text[i - 1]
            if prev in "eE^":
                continue
            piece = text[start:i].strip()
            if piece:
                terms.append(piece)
            start = i

    if depth != 0:
        raise ValueError("unbalanced parentheses in FORM RHS")

    piece = text[start:].strip()
    if piece:
        terms.append(piece)
    return terms


def _coefficient_from_term(term: str, integral_match: re.Match[str]) -> str:
    """Remove one integral token and retain all surrounding FORM factors.

    Kira 3.1 may emit either ``num(...)*I(...)`` or ``I(...)*(1)`` (and, in
    general, products on both sides of the integral token).  The previous
    parser assumed that the coefficient always preceded the integral.  Here we
    reconstruct the full multiplicative coefficient from both sides while
    preserving FORM source syntax.
    """
    before = term[: integral_match.start()].strip()
    after = term[integral_match.end() :].strip()

    # The stars immediately adjacent to the removed integral are multiplication
    # separators, not coefficient content.  Remove only those separators; all
    # other FORM source text is kept verbatim.
    if before.endswith("*"):
        before = before[:-1].rstrip()
    if after.startswith("*"):
        after = after[1:].lstrip()

    if not before and not after:
        return "+1"
    if before in {"+", "-"} and not after:
        return before + "1"
    if before in {"+", "-"} and after:
        return before + after
    if not before:
        return after
    if not after:
        return before
    return f"{before}*{after}"


def parse_form_rule(statement: str, *, expected_family: str | None = None) -> KiraFormRule:
    match = _LHS_RE.match(statement)
    if not match:
        raise ValueError(f"not a Kira FORM reduction rule: {statement[:160]!r}")

    family = match.group("family")
    if expected_family is not None and family != expected_family:
        raise ValueError(f"unexpected LHS family {family!r}, expected {expected_family!r}")
    lhs = KiraFormIntegral(family, _parse_indices(match.group("args")))
    rhs = match.group("rhs").strip()

    # Zero rules do not contain an integral at all.
    if not _INTEGRAL_RE.search(rhs):
        return KiraFormRule(lhs=lhs, terms=(), rhs_form=rhs)

    terms: list[KiraFormTerm] = []
    for additive_term in _split_top_level_additive_terms(rhs):
        integral_matches = list(_INTEGRAL_RE.finditer(additive_term))
        if not integral_matches:
            # A non-zero standalone scalar term would not be a valid reduction
            # of this integral family and should not be silently discarded.
            if additive_term.strip() not in {"0", "+0", "-0"}:
                raise ValueError(
                    f"FORM RHS term has no integral token: {additive_term!r}"
                )
            continue
        if len(integral_matches) != 1:
            raise ValueError(
                "FORM RHS additive term contains more than one integral token: "
                f"{additive_term!r}"
            )

        integral_match = integral_matches[0]
        target_family = integral_match.group("family")
        if expected_family is not None and target_family != expected_family:
            raise ValueError(
                f"unexpected RHS family {target_family!r}, expected {expected_family!r}"
            )

        terms.append(
            KiraFormTerm(
                coefficient_form=_coefficient_from_term(additive_term, integral_match),
                integral=KiraFormIntegral(
                    target_family, _parse_indices(integral_match.group("args"))
                ),
            )
        )

    return KiraFormRule(lhs=lhs, terms=tuple(terms), rhs_form=rhs)


def iter_kira_form_rules(
    path: str | Path,
    *,
    family: str | None = None,
) -> Iterator[KiraFormRule]:
    for statement in iter_form_statements(path):
        stripped = statement.lstrip()
        if not stripped.startswith("id "):
            continue
        yield parse_form_rule(statement, expected_family=family)
