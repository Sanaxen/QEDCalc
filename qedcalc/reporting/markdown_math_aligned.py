r"""Safe aligned-style wrapping for long Markdown display equations.

Unlike the Phase-84 proxy formatter, this formatter keeps the original symbols
and inserts line breaks only at structurally safe additive boundaries.

Important rule: a ``\\left ... \\right`` pair is never split across aligned rows.
When a whole outer group is long, ``aligned`` is placed *inside* the complete
pair, for example::

    -\\left(\\begin{aligned}
    A {}+ \\\\
    B {}- \\\\
    C
    \\end{aligned}\\right)

This preserves TeX delimiter balance and keeps continuation rows from starting
with ``=``, ``+`` or ``-``.
"""
from __future__ import annotations

from . import markdown_math as _base


def _additive_parts(expr: str) -> list[tuple[str, str | None]] | None:
    """Return (term, following_operator) pairs for top-level + / - operators."""
    s = _base._compact(expr)
    ops = _base._top_level_ops(s, ("+", "-"))
    if not ops:
        return None

    parts: list[tuple[str, str | None]] = []
    start = 0
    for pos, op in ops:
        term = s[start:pos].strip()
        if not term:
            return None
        parts.append((term, op))
        start = pos + len(op)
    last = s[start:].strip()
    if not last:
        return None
    parts.append((last, None))
    return parts


def _additive_rows(expr: str, max_width: int) -> list[str] | None:
    """Wrap a top-level sum while leaving the operator at the end of a row."""
    parts = _additive_parts(expr)
    if not parts:
        return None

    rows: list[str] = []
    current = parts[0][0]

    for index in range(len(parts) - 1):
        op = parts[index][1]
        next_term = parts[index + 1][0]
        if op is None:
            return None

        candidate = f"{current} {op} {next_term}"
        if _base._visible_len(candidate) <= max_width:
            current = candidate
            continue

        # The continuation operator belongs to the preceding row so that the
        # following row begins with an expression, never with + or -.
        rows.append(f"{current} {{}}{op}")
        current = next_term

    rows.append(current)
    return rows


def _signed_outer_group(expr: str):
    """Recognize an optional unary sign followed by one whole outer group."""
    s = _base._compact(expr)
    sign = ""
    body = s
    if body.startswith(("+", "-")):
        sign = body[0]
        body = body[1:].lstrip()
    group = _base._whole_outer_group(body)
    if group is None:
        return None
    opening, inner, closing = group
    return sign, opening, inner, closing


def _wrap_outer_group(expr: str, max_width: int) -> str | None:
    """Put aligned inside a complete outer delimiter pair."""
    parsed = _signed_outer_group(expr)
    if parsed is None:
        return None
    sign, opening, inner, closing = parsed

    rows = _additive_rows(inner, max_width)
    if rows is None or len(rows) < 2:
        return None

    body = " \\\\\n".join(rows)
    return (
        f"{sign}{opening}"
        "\\begin{aligned}\n"
        f"{body}\n"
        "\\end{aligned}"
        f"{closing}"
    )


def _wrap_assignment(expr: str, max_width: int) -> str | None:
    assignment = _base._top_level_assignment(expr)
    if assignment is None:
        return None
    lhs, rhs = assignment

    # Prefer a complete outer group on the RHS.  This avoids nesting one
    # aligned environment inside another aligned environment just to show '='.
    wrapped_rhs = _wrap_outer_group(rhs, max_width)
    if wrapped_rhs is not None:
        return f"{lhs} = {wrapped_rhs}"

    rhs_rows = _additive_rows(rhs, max_width=max(20, max_width - _base._visible_len(lhs) - 4))
    if rhs_rows is None or len(rhs_rows) < 2:
        return None

    lines = [f"{lhs} &= {rhs_rows[0]}"]
    lines.extend(f"&\quad {row}" for row in rhs_rows[1:])
    return "\\begin{aligned}\n" + " \\\\\n".join(lines) + "\n\\end{aligned}"


def _format_display(block: str, max_width: int) -> str:
    raw = block.strip()
    if not raw or any(marker in raw for marker in _base._STRUCTURED):
        return raw
    if _base._visible_len(raw) <= max_width:
        return raw

    assignment = _wrap_assignment(raw, max_width)
    if assignment is not None:
        return assignment

    outer = _wrap_outer_group(raw, max_width)
    if outer is not None:
        return outer

    rows = _additive_rows(raw, max_width)
    if rows is not None and len(rows) >= 2:
        return "\\begin{aligned}\n" + " \\\\\n".join(rows) + "\n\\end{aligned}"

    # Deliberately leave an indivisible expression unchanged rather than
    # invent proxy symbols or split through a TeX group.
    return raw


def format_markdown_math_aligned(markdown: str, max_width: int = 92) -> str:
    """Wrap long ``$$ ... $$`` blocks with structurally safe aligned rows.

    This is presentation-only.  It never introduces proxy variables and never
    splits a ``\\left ... \\right`` pair across rows.  Expressions that cannot
    be split safely are left unchanged.
    """
    parts = markdown.split("$$")
    if len(parts) % 2 == 0:
        return markdown

    for i in range(1, len(parts), 2):
        parts[i] = "\n" + _format_display(parts[i], max_width) + "\n"
    return "$$".join(parts)


__all__ = ["format_markdown_math_aligned"]
