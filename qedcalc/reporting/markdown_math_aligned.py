r"""Safe aligned-style wrapping for long Markdown display equations.

This formatter keeps the original mathematical symbols.  It wraps long sums
and products only at structurally safe boundaries and never separates a
``\\left ... \\right`` pair or a TeX brace group across rows.

For sums, the continuation operator is kept at the end of the preceding row.
For products, original top-level source-line boundaries are preferred; if the
source is one physical line, safe top-level product boundaries are used.
Nested complete groups are refined recursively when a row is still too long.
"""
from __future__ import annotations

from . import markdown_math as _base

_MAX_RECURSION = 16


def _additive_parts(expr: str) -> list[tuple[str, str | None]] | None:
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

        rows.append(f"{current} {{}}{op}")
        current = next_term

    rows.append(current)
    return rows


def _rows_to_aligned(rows: list[str]) -> str:
    return "\\begin{aligned}\n" + " \\\\\n".join(rows) + "\n\\end{aligned}"


def _signed_outer_group(expr: str):
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


def _safe_source_chunks(expr: str) -> list[str] | None:
    """Split only at source newlines where every TeX grouping depth is zero."""
    if "\n" not in expr:
        return None

    brace = paren = bracket = 0
    lr_depth = 0
    boundaries: list[int] = []
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
            boundaries.append(i)

        i += 1

    if brace != 0 or paren != 0 or bracket != 0 or lr_depth != 0:
        return None
    if not boundaries:
        return None

    chunks: list[str] = []
    start = 0
    for pos in boundaries:
        chunk = _base._compact(expr[start:pos])
        if chunk:
            chunks.append(chunk)
        start = pos + 1
    tail = _base._compact(expr[start:])
    if tail:
        chunks.append(tail)

    return chunks if len(chunks) >= 2 else None


def _pack_product_chunks(chunks: list[str], max_width: int) -> list[str]:
    """Pack complete factors/chunks into rows without changing their order."""
    rows: list[str] = []
    current = ""

    for chunk in chunks:
        if not current:
            current = chunk
            continue

        candidate = f"{current} {chunk}"
        if _base._visible_len(candidate) <= max_width:
            current = candidate
        else:
            rows.append(current)
            current = chunk

    if current:
        rows.append(current)
    return rows


def _binary_product_rows(expr: str, max_width: int, depth: int) -> list[str] | None:
    """Recursively split a one-line product at safe top-level product boundaries."""
    if depth >= _MAX_RECURSION:
        return None

    s = _base._compact(expr)
    if _base._visible_len(s) <= max_width:
        return [s]

    split = _base._best_binary_split(s, original_expr=None)
    if split is None:
        return None

    left, op, right = split
    left_rows = _binary_product_rows(left, max_width, depth + 1) or [left]
    right_rows = _binary_product_rows(right, max_width, depth + 1) or [right]

    if op:
        left_rows[-1] = f"{left_rows[-1]} {{}}{op}"

    return left_rows + right_rows


def _product_rows(expr: str, max_width: int, depth: int = 0) -> list[str] | None:
    """Return safe rows for a long product, preferring original source lines."""
    if depth >= _MAX_RECURSION:
        return None

    source_chunks = _safe_source_chunks(expr)
    if source_chunks is not None:
        rows = _pack_product_chunks(source_chunks, max_width)
        expanded: list[str] = []
        for row in rows:
            if _base._visible_len(row) <= max_width:
                expanded.append(row)
                continue
            sub = _binary_product_rows(row, max_width, depth + 1)
            expanded.extend(sub if sub is not None else [row])
        return expanded if len(expanded) >= 2 else None

    rows = _binary_product_rows(expr, max_width, depth + 1)
    return rows if rows is not None and len(rows) >= 2 else None


def _refine_rows(rows: list[str], max_width: int, depth: int) -> list[str]:
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
        if wrapped is not None:
            refined.append(wrapped)
            continue

        product = _product_rows(row, max_width, depth + 1)
        if product is not None:
            refined.extend(product)
        else:
            refined.append(row)

    return refined


def _wrap_outer_group(expr: str, max_width: int, depth: int = 0) -> str | None:
    if depth >= _MAX_RECURSION:
        return None

    parsed = _signed_outer_group(expr)
    if parsed is None:
        return None
    sign, opening, inner, closing = parsed

    rows = _additive_rows(inner, max_width)
    if rows is None or len(rows) < 2:
        rows = _product_rows(inner, max_width, depth + 1)
    if rows is None or len(rows) < 2:
        return None

    rows = _refine_rows(rows, max_width, depth + 1)
    return f"{sign}{opening}{_rows_to_aligned(rows)}{closing}"


def _wrap_embedded_group(expr: str, max_width: int, depth: int = 0) -> str | None:
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
            wrapped_inner = _wrap_outer_group(inner, max_width, depth + 1)

            if wrapped_inner is None:
                rows = _additive_rows(inner, max_width)
                if rows is None or len(rows) < 2:
                    rows = _product_rows(inner, max_width, depth + 1)
                if rows is not None and len(rows) >= 2:
                    rows = _refine_rows(rows, max_width, depth + 1)
                    wrapped_inner = _rows_to_aligned(rows)

            if wrapped_inner is not None:
                return (
                    s[:i]
                    + opening_source
                    + wrapped_inner
                    + closing_source
                    + s[end:]
                )

        i = end

    return None


def _wrap_assignment(expr: str, max_width: int) -> str | None:
    assignment = _base._top_level_assignment(expr)
    if assignment is None:
        return None
    lhs, rhs = assignment

    wrapped_rhs = _wrap_outer_group(rhs, max_width)
    if wrapped_rhs is None:
        wrapped_rhs = _wrap_embedded_group(rhs, max_width)
    if wrapped_rhs is not None:
        return f"{lhs} = {wrapped_rhs}"

    rhs_width = max(20, max_width - _base._visible_len(lhs) - 4)
    rhs_rows = _additive_rows(rhs, rhs_width)
    if rhs_rows is None or len(rhs_rows) < 2:
        rhs_rows = _product_rows(rhs, rhs_width)
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
    if rows is None or len(rows) < 2:
        rows = _product_rows(raw, max_width)
    if rows is not None and len(rows) >= 2:
        rows = _refine_rows(rows, max_width, 0)
        return _rows_to_aligned(rows)

    return raw


def format_markdown_math_aligned(markdown: str, max_width: int = 92) -> str:
    """Wrap long ``$$ ... $$`` blocks without proxy variables.

    Long sums and products are split only at safe structural boundaries.
    ``\\left ... \\right`` pairs and TeX brace groups are never separated.
    Expressions with no safe split remain unchanged.
    """
    parts = markdown.split("$$")
    if len(parts) % 2 == 0:
        return markdown

    for i in range(1, len(parts), 2):
        parts[i] = "\n" + _format_display(parts[i], max_width) + "\n"
    return "$$".join(parts)


__all__ = ["format_markdown_math_aligned"]
