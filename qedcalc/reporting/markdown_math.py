r"""Readable Markdown/LaTeX formatting for long display equations.

The formatter changes presentation only. It never changes the mathematical
content and never asks SymPy to re-simplify an expression.

Policy:
- keep short display equations untouched;
- wrap long plain display blocks in ``aligned``;
- also inspect rows of an existing ``aligned`` environment and reflow rows that
  are still too long;
- place relation/arithmetic operators at the END of a line, never at the start;
- prefer breaks after top-level ``=``, ``+``, ``-``, ``\times`` and ``\cdot``;
- for long product chains, whitespace is a safe presentation-only fallback.
"""
from __future__ import annotations

import re

_STRUCTURED_OTHER = (
    r"\begin{alignedat}",
    r"\begin{split}",
    r"\begin{cases}",
    r"\begin{array}",
    r"\begin{matrix}",
    r"\begin{pmatrix}",
    r"\begin{bmatrix}",
    r"\begin{gathered}",
    r"\begin{multline}",
)


def _visible_len(s: str) -> int:
    """Cheap proxy for rendered width; only used to decide whether to wrap."""
    t = re.sub(r"\\[A-Za-z]+", "X", s)
    t = t.replace("{", "").replace("}", "")
    return len(t)


def _top_level_breaks(expr: str) -> list[int]:
    """Return presentation-safe break positions immediately AFTER operators."""
    out: list[int] = []
    brace = paren = bracket = 0
    i = 0
    while i < len(expr):
        ch = expr[i]
        if ch == "\\":
            m = re.match(r"\\[A-Za-z]+", expr[i:])
            if m:
                token = m.group(0)
                end = i + len(token)
                if brace == paren == bracket == 0 and token in (r"\times", r"\cdot"):
                    out.append(end)
                i = end
                continue
        if ch == "{":
            brace += 1
        elif ch == "}":
            brace = max(0, brace - 1)
        elif ch == "(":
            paren += 1
        elif ch == ")":
            paren = max(0, paren - 1)
        elif ch == "[":
            bracket += 1
        elif ch == "]":
            bracket = max(0, bracket - 1)
        elif brace == paren == bracket == 0 and ch in "=+-":
            prev = expr[:i].rstrip()
            if prev and prev[-1] not in "=+-*/,(":
                out.append(i + 1)
        i += 1
    return sorted(set(out))


def _operator_chunks(expr: str) -> list[str]:
    breaks = _top_level_breaks(expr)
    if not breaks:
        return []
    chunks: list[str] = []
    start = 0
    for end in breaks:
        piece = expr[start:end].strip()
        if piece:
            chunks.append(piece)
        start = end
    tail = expr[start:].strip()
    if tail:
        chunks.append(tail)
    return chunks


def _whitespace_chunks(expr: str) -> list[str]:
    # Whitespace has no mathematical effect in ordinary LaTeX math mode. This
    # fallback is therefore suitable for long noncommutative factor chains.
    return [x for x in re.split(r"\s+", expr.strip()) if x]


def _hard_chunks(expr: str, max_width: int) -> list[str]:
    """Last-resort break for a single token-like LaTeX string.

    Prefer boundaries after closing braces/parentheses. This is display-only and
    does not insert an arithmetic operator or alter token order.
    """
    if _visible_len(expr) <= max_width:
        return [expr]
    pieces = re.split(r"(?<=[}\)])(?=\\|[A-Za-z0-9])", expr)
    if len(pieces) <= 1:
        return [expr]
    return [p for p in pieces if p]


def _pack(chunks: list[str], max_width: int) -> list[str]:
    if not chunks:
        return []
    lines: list[str] = []
    cur = chunks[0]
    for chunk in chunks[1:]:
        candidate = f"{cur} {chunk}".strip()
        if _visible_len(candidate) <= max_width:
            cur = candidate
        else:
            lines.append(cur.rstrip())
            cur = chunk.lstrip()
    lines.append(cur.rstrip())
    return lines


def _wrap_expression(expr: str, max_width: int) -> list[str]:
    compact = " ".join(line.strip() for line in expr.splitlines() if line.strip())
    if _visible_len(compact) <= max_width:
        return [compact]

    chunks = _operator_chunks(compact)
    if not chunks:
        chunks = _whitespace_chunks(expr)
    lines = _pack(chunks, max_width)

    # If a single huge token remains, try structural brace/parenthesis boundaries.
    expanded: list[str] = []
    for line in lines:
        if _visible_len(line) > max_width:
            expanded.extend(_pack(_hard_chunks(line, max_width), max_width))
        else:
            expanded.append(line)
    return expanded


def _strip_row_syntax(line: str) -> tuple[str, bool, str]:
    """Return (math body, had_row_break, indentation/alignment prefix)."""
    s = line.rstrip()
    had_break = s.endswith(r"\\")
    if had_break:
        s = s[:-2].rstrip()
    prefix = ""
    stripped = s.lstrip()
    indent = s[: len(s) - len(stripped)]
    if stripped.startswith("&"):
        prefix = indent + "& "
        stripped = stripped[1:].lstrip()
    else:
        prefix = indent
    return stripped, had_break, prefix


def _reflow_aligned(expr: str, max_width: int) -> str:
    """Reflow overlong rows in an existing aligned environment."""
    out: list[str] = []
    inside = False
    for line in expr.strip().splitlines():
        stripped = line.strip()
        if stripped.startswith(r"\begin{aligned}"):
            inside = True
            out.append(line)
            continue
        if stripped.startswith(r"\end{aligned}"):
            inside = False
            out.append(line)
            continue
        if not inside or not stripped:
            out.append(line)
            continue

        body, had_break, prefix = _strip_row_syntax(line)
        wrapped = _wrap_expression(body, max_width)
        if len(wrapped) == 1:
            out.append(prefix + wrapped[0] + (r" \\" if had_break else ""))
            continue

        for i, row in enumerate(wrapped):
            # Every intermediate row must break. The last row keeps the original
            # row-break status so surrounding aligned semantics are preserved.
            needs_break = i < len(wrapped) - 1 or had_break
            out.append(prefix + row + (r" \\" if needs_break else ""))
    return "\n".join(out)


def _wrap_plain_display(expr: str, max_width: int) -> str:
    compact = " ".join(line.strip() for line in expr.splitlines() if line.strip())
    if _visible_len(compact) <= max_width:
        return expr.strip()

    if r"\begin{aligned}" in expr:
        return _reflow_aligned(expr, max_width)

    # Other structured environments are left untouched because blindly inserting
    # rows into cases/matrices/split can alter their LaTeX grammar.
    if any(marker in compact for marker in _STRUCTURED_OTHER):
        return expr.strip()

    lines = _wrap_expression(expr, max_width)
    if len(lines) <= 1:
        return expr.strip()

    rendered = [r"\begin{aligned}"]
    for i, line in enumerate(lines):
        suffix = r" \\" if i < len(lines) - 1 else ""
        rendered.append(f"& {line}{suffix}")
    rendered.append(r"\end{aligned}")
    return "\n".join(rendered)


def format_markdown_math(text: str, max_width: int = 92) -> str:
    """Wrap long plain or aligned ``$$...$$`` blocks for readability."""
    parts = text.split("$$")
    if len(parts) < 3:
        return text
    for i in range(1, len(parts), 2):
        parts[i] = "\n" + _wrap_plain_display(parts[i], max_width) + "\n"
    return "$$".join(parts)
