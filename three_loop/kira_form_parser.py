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


def _coefficient_before_integral(rhs: str, start: int, previous_end: int) -> str:
    """Extract the coefficient multiplying one RHS integral.

    After Kira back substitution every additive top-level term contains one
    integral token.  We find the additive term boundary by scanning backwards
    from the integral while respecting parenthesis depth, so plus/minus signs
    inside ``num(...)`` do not split the coefficient.
    """
    depth = 0
    boundary = previous_end
    i = start - 1
    while i >= previous_end:
        ch = rhs[i]
        if ch == ")":
            depth += 1
        elif ch == "(":
            depth -= 1
            if depth < 0:
                raise ValueError("unbalanced parentheses while parsing FORM coefficient")
        elif depth == 0 and ch in "+-":
            # Treat exponent signs and unary signs inside a multiplicative
            # token conservatively; Kira FORM coefficients normally use
            # num(...), products and rational literals here.
            prev = rhs[i - 1] if i > 0 else ""
            if prev not in "eE^":
                boundary = i
                break
        i -= 1
    coefficient = rhs[boundary:start].strip()
    if not coefficient:
        coefficient = "+1"
    elif coefficient in {"+", "-"}:
        coefficient += "1"
    # Kira normally writes ``+ coeff*Integral``.  Remove only the final
    # multiplication marker belonging to the integral, not internal products.
    if coefficient.endswith("*"):
        coefficient = coefficient[:-1].rstrip()
    return coefficient


def parse_form_rule(statement: str, *, expected_family: str | None = None) -> KiraFormRule:
    match = _LHS_RE.match(statement)
    if not match:
        raise ValueError(f"not a Kira FORM reduction rule: {statement[:160]!r}")

    family = match.group("family")
    if expected_family is not None and family != expected_family:
        raise ValueError(f"unexpected LHS family {family!r}, expected {expected_family!r}")
    lhs = KiraFormIntegral(family, _parse_indices(match.group("args")))
    rhs = match.group("rhs").strip()

    integral_matches = list(_INTEGRAL_RE.finditer(rhs))
    if not integral_matches:
        return KiraFormRule(lhs=lhs, terms=(), rhs_form=rhs)

    terms: list[KiraFormTerm] = []
    previous_end = 0
    for integral_match in integral_matches:
        target_family = integral_match.group("family")
        if expected_family is not None and target_family != expected_family:
            raise ValueError(
                f"unexpected RHS family {target_family!r}, expected {expected_family!r}"
            )
        coeff = _coefficient_before_integral(
            rhs, integral_match.start(), previous_end
        )
        terms.append(
            KiraFormTerm(
                coefficient_form=coeff,
                integral=KiraFormIntegral(
                    target_family, _parse_indices(integral_match.group("args"))
                ),
            )
        )
        previous_end = integral_match.end()

    # Ensure text between one integral and the next is only the next term's
    # coefficient; after the final integral only whitespace may remain.
    trailing = rhs[previous_end:].strip()
    if trailing:
        raise ValueError(f"unexpected trailing FORM text after final integral: {trailing!r}")

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
