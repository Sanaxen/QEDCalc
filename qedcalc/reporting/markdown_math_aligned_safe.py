r"""Safety wrapper for aligned Markdown math formatting.

The aligned formatter intentionally treats ``\frac{...}{...}`` as atomic so it
never inserts ``aligned`` into a numerator or denominator.  This wrapper handles
the remaining case where an entire fraction is still too wide: it rewrites only
the numerator and/or denominator with ``gathered`` rows, preserving the fraction
itself and avoiding presentation proxy symbols.
"""
from __future__ import annotations

from . import markdown_math as _base
from . import markdown_math_aligned as _aligned

_MAX_DEPTH = 10


def _rows_to_gathered(rows: list[str]) -> str:
    return "\\begin{gathered}\n" + " \\\\\n".join(rows) + "\n\\end{gathered}"


def _split_piece(expr: str, max_width: int, depth: int = 0) -> list[str] | None:
    """Split a fraction argument without inserting an aligned environment."""
    s = _base._compact(expr)
    if not s or _base._visible_len(s) <= max_width:
        return [s] if s else None
    if depth >= _MAX_DEPTH:
        return None

    rows = _aligned._additive_rows(s, max_width)
    if rows is None or len(rows) < 2:
        rows = _aligned._product_rows(s, max_width, depth + 1)
    if rows is None or len(rows) < 2:
        return None

    refined: list[str] = []
    changed = False
    for row in rows:
        if _base._visible_len(row) <= max_width:
            refined.append(row)
            continue
        sub = _split_piece(row, max_width, depth + 1)
        if sub is not None and len(sub) >= 2:
            refined.extend(sub)
            changed = True
        else:
            refined.append(row)

    if changed:
        return refined
    return rows


def _wrap_whole_fraction(expr: str, max_width: int) -> str | None:
    parsed = _base._whole_fraction(expr)
    if parsed is None:
        return None

    sign, numerator, denominator = parsed
    num_rows = _split_piece(numerator, max_width)
    den_rows = _split_piece(denominator, max_width)

    num_source = numerator
    den_source = denominator
    changed = False

    if num_rows is not None and len(num_rows) >= 2:
        num_source = _rows_to_gathered(num_rows)
        changed = True
    if den_rows is not None and len(den_rows) >= 2:
        den_source = _rows_to_gathered(den_rows)
        changed = True

    if not changed:
        return None

    return f"{sign}\\frac{{{num_source}}}{{{den_source}}}"


def _postprocess_long_whole_fractions(markdown: str, max_width: int) -> str:
    parts = markdown.split("$$")
    if len(parts) % 2 == 0:
        return markdown

    for i in range(1, len(parts), 2):
        block = parts[i].strip()
        if not block:
            continue

        # Do not touch a display already structured by the aligned formatter.
        if any(marker in block for marker in _base._STRUCTURED):
            continue
        if _base._visible_len(block) <= max_width:
            continue

        wrapped = _wrap_whole_fraction(block, max_width)
        if wrapped is not None:
            parts[i] = "\n" + wrapped + "\n"

    return "$$".join(parts)


def format_markdown_math_aligned(markdown: str, max_width: int = 92) -> str:
    """Format long display math without proxies or aligned inside fractions."""
    formatted = _aligned.format_markdown_math_aligned(markdown, max_width=max_width)
    return _postprocess_long_whole_fractions(formatted, max_width=max_width)


__all__ = ["format_markdown_math_aligned"]
