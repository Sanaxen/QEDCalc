"""Safety wrapper for Phase-84 Markdown math formatting.

The base formatter recursively introduces presentation-only proxy symbols for
long equations.  This wrapper replaces only its source-newline product splitter:
a source newline is eligible only when braces, ordinary delimiters, and
``\\left...\\right`` groups are all closed at that boundary.

This prevents a proxy split from separating ``\\left(`` from its matching
``\\right)`` or otherwise cutting through a TeX group.
"""
from __future__ import annotations

from . import markdown_math as _base


def _safe_source_line_product_split(expr: str) -> tuple[str, str, str] | None:
    """Split at a structurally top-level source newline nearest the midpoint."""
    if "\n" not in expr:
        return None

    brace = paren = bracket = 0
    lr_depth = 0
    candidates: list[int] = []
    i = 0

    while i < len(expr):
        left = _base._left_delimiter_at(expr, i)
        if left is not None:
            lr_depth += 1
            i = left[1]
            continue

        right = _base._right_delimiter_at(expr, i)
        if right is not None:
            lr_depth -= 1
            if lr_depth < 0:
                return None
            i = right[1]
            continue

        ch = expr[i]

        # Escaped literal braces are not grouping delimiters.
        if ch == "\\" and i + 1 < len(expr) and expr[i + 1] in "{}":
            i += 2
            continue

        if ch == "{":
            brace += 1
        elif ch == "}":
            brace -= 1
            if brace < 0:
                return None
        elif ch == "(":
            paren += 1
        elif ch == ")":
            paren -= 1
            if paren < 0:
                return None
        elif ch == "[":
            bracket += 1
        elif ch == "]":
            bracket -= 1
            if bracket < 0:
                return None
        elif ch == "\n" and brace == paren == bracket == lr_depth == 0:
            left_text = expr[:i].strip()
            right_text = expr[i + 1:].strip()
            if left_text and right_text:
                candidates.append(i)

        i += 1

    # Do not trust source-line splitting if the full expression is unbalanced.
    if brace != 0 or paren != 0 or bracket != 0 or lr_depth != 0:
        return None
    if not candidates:
        return None

    midpoint = len(expr) / 2
    pos = min(candidates, key=lambda p: abs(p - midpoint))
    left = _base._compact(expr[:pos])
    right = _base._compact(expr[pos + 1:])
    if not left or not right:
        return None
    return left, "", right


# The base formatter resolves this helper from its module globals at call time,
# so replacing it here safely changes recursive behavior without duplicating the
# full formatter implementation.
_base._source_line_product_split = _safe_source_line_product_split

format_markdown_math = _base.format_markdown_math

__all__ = ["format_markdown_math"]
