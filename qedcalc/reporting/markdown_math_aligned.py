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

The same rule is applied recursively when a long group is embedded in a product
such as ``\\bar u(p')\\,\\left[ ... \\right]\\,u(p)`` or when one aligned row
still contains a long factor such as ``2\\left(A+B+C+...\\right)``.

This preserves TeX delimiter balance and keeps continuation rows from starting
with ``=``, ``+`` or ``-``.
"""
from __future__ import annotations

from . import markdown_math as _base

_MAX_RECURSION = 12


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


def _rows_to_aligned(rows: list[str]) -> str:
    return "\\begin{aligned}\n" + " \\\\\n".join(rows) + "\n\\end{aligned}"


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


def _refine_rows(rows: list[str], max_width: int, depth: int) -> list[str]:
    """Recursively reformat any aligned row that still exceeds ``max_width``.

    The refinement never inserts a row break through a delimiter pair.  It only
    descends into a *complete* embedded ``\\left...\\right`` group and places a
    nested aligned environment inside that group when the group's own contents
    have safe additive boundaries.
    """
    if depth >= _MAX_RECURSION:
        return rows

    refined: list[str] = []
    for row in rows:
        if _base._visible_len(row) <= max_width:
            refined.append(row)
            continue

        wrapped = _wrap_embedded_group(row, max_width, depth + 1)
        if wrapped is None:
            wrapped = _wrap_outer_group(row, max_width, depth + 1)

        refined.append(wrapped if wrapped is not None else row)

    return refined


def _wrap_outer_group(expr: str, max_width: int, depth: int = 0) -> str | None:
    """Put aligned inside a complete outer delimiter pair."""
    if depth >= _MAX_RECURSION:
        return None

    parsed = _signed_outer_group(expr)
    if parsed is None:
        return None
    sign, opening, inner, closing = parsed

    rows = _additive_rows(inner, max_width)
    if rows is None or len(rows) < 2:
        return None

    rows = _refine_rows(rows, max_width, depth + 1)
    return f"{sign}{opening}{_rows_to_aligned(rows)}{closing}"


def _wrap_embedded_group(expr: str, max_width: int, depth: int = 0) -> str | None:
    """Wrap a long complete ``\\left...\\right`` group embedded in a product.

    Example input::

        \\bar u(p')\\,\\left[-\\left(A+B+C\\right)\\right]\\,u(p)

    The outer spinor factors remain untouched.  The complete square-bracket
    pair remains untouched.  Only the long expression *inside* that pair is
    reformatted.  If an aligned row still contains a long complete group, the
    same operation is applied recursively inside that group.
    """
    if depth >= _MAX_RECURSION:
        return None

    s = _base._compact(expr)
    i = 0
    while i < len(s):
        left = _base._left_delimiter_at(s, i)
        if left is None:
            i += 1
            continue

        opening_token, content_start = left
        end = _base._matching_left_right_end(s, i)
        if end is None:
            return None

        closing_token = _base._LEFT_RIGHT_PAIRS[opening_token]
        opening_source = r"\left" + opening_token
        closing_source = r"\right" + closing_token
        inner_end = end - len(closing_source)
        inner = s[content_start:inner_end].strip()

        if inner and _base._visible_len(inner) > max_width:
            # First handle a nested whole form such as -\left(long sum\right).
            wrapped_inner = _wrap_outer_group(inner, max_width, depth + 1)

            # Otherwise the group itself may directly contain a long sum.
            if wrapped_inner is None:
                rows = _additive_rows(inner, max_width)
                if rows is not None and len(rows) >= 2:
                    rows = _refine_rows(rows, max_width, depth + 1)
                    wrapped_inner = _rows_to_aligned(rows)

            # A direct additive split may have produced one or more rows that
            # still contain oversized nested groups.  The recursion above will
            # descend into those groups without ever separating left/right.
            if wrapped_inner is not None:
                prefix = s[:i]
                suffix = s[end:]
                candidate = (
                    prefix
                    + opening_source
                    + wrapped_inner
                    + closing_source
                    + suffix
                )

                # If the surrounding product is still long, try the next nested
                # group on a later recursive pass; do not split the product at an
                # unsafe arbitrary character boundary.
                return candidate

        # This complete pair could not be usefully wrapped.  Continue after it;
        # never inspect a split point inside the pair itself at this level.
        i = end

    return None


def _wrap_assignment(expr: str, max_width: int) -> str | None:
    assignment = _base._top_level_assignment(expr)
    if assignment is None:
        return None
    lhs, rhs = assignment

    # Prefer a complete outer group on the RHS.  This avoids nesting one
    # aligned environment inside another aligned environment just to show '='.
    wrapped_rhs = _wrap_outer_group(rhs, max_width)
    if wrapped_rhs is None:
        wrapped_rhs = _wrap_embedded_group(rhs, max_width)
    if wrapped_rhs is not None:
        return f"{lhs} = {wrapped_rhs}"

    rhs_rows = _additive_rows(rhs, max_width=max(20, max_width - _base._visible_len(lhs) - 4))
    if rhs_rows is None or len(rhs_rows) < 2:
        return None

    rhs_rows = _refine_rows(rhs_rows, max_width, 0)
    lines = [f"{lhs} &= {rhs_rows[0]}"]
    lines.extend(f"&\quad {row}" for row in rhs_rows[1:])
    return _rows_to_aligned(lines)


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

    embedded = _wrap_embedded_group(raw, max_width)
    if embedded is not None:
        return embedded

    rows = _additive_rows(raw, max_width)
    if rows is not None and len(rows) >= 2:
        rows = _refine_rows(rows, max_width, 0)
        return _rows_to_aligned(rows)

    # Deliberately leave an indivisible expression unchanged rather than
    # invent proxy symbols or split through a TeX group.
    return raw


def format_markdown_math_aligned(markdown: str, max_width: int = 92) -> str:
    """Wrap long ``$$ ... $$`` blocks with structurally safe aligned rows.

    This is presentation-only.  It never introduces proxy variables and never
    splits a ``\\left ... \\right`` pair across rows.  Oversized rows are
    recursively refined inside complete nested groups.  Expressions that cannot
    be split safely are left unchanged.
    """
    parts = markdown.split("$$")
    if len(parts) % 2 == 0:
        return markdown

    for i in range(1, len(parts), 2):
        parts[i] = "\n" + _format_display(parts[i], max_width) + "\n"
    return "$$".join(parts)


__all__ = ["format_markdown_math_aligned"]
