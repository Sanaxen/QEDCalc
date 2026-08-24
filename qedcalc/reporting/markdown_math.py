"""Readable Markdown/LaTeX formatting for long display equations.

The formatter changes presentation only. It never changes the mathematical
content and never asks SymPy to re-simplify an expression.

Policy:
- keep short display equations untouched;
- keep already structured environments (aligned, split, cases, matrix, etc.) untouched;
- wrap only long plain display blocks;
- place relation/arithmetic operators at the END of a line, never at the start;
- prefer breaks at top-level =, +, -, then \times / \cdot;
- fall back to source line boundaries for long factor chains.
"""
from __future__ import annotations

import re

_STRUCTURED = (
    r"\begin{aligned}",
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
    t = re.sub(r"\\[A-Za-z]+", "X", s)
    t = t.replace("{", "").replace("}", "")
    return len(t)


def _top_level_breaks(expr: str) -> list[int]:
    """Return safe break positions AFTER top-level operators."""
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


def _chunks_from_breaks(expr: str) -> list[str]:
    breaks = _top_level_breaks(expr)
    if not breaks:
        return [x.strip() for x in expr.splitlines() if x.strip()]
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


def _wrap_plain_display(expr: str, max_width: int) -> str:
    compact = " ".join(line.strip() for line in expr.splitlines() if line.strip())
    if _visible_len(compact) <= max_width:
        return expr.strip()
    if any(marker in compact for marker in _STRUCTURED):
        return expr.strip()

    chunks = _chunks_from_breaks(expr)
    lines = _pack(chunks, max_width)
    if len(lines) <= 1:
        raw_lines = [x.strip() for x in expr.splitlines() if x.strip()]
        if len(raw_lines) > 1:
            lines = _pack(raw_lines, max_width)
    if len(lines) <= 1:
        return expr.strip()

    rendered = [r"\begin{aligned}"]
    for i, line in enumerate(lines):
        suffix = r" \\" if i < len(lines) - 1 else ""
        rendered.append(f"& {line}{suffix}")
    rendered.append(r"\end{aligned}")
    return "\n".join(rendered)


def format_markdown_math(text: str, max_width: int = 92) -> str:
    """Wrap long plain $$...$$ blocks for GitHub/Markdown readability."""
    parts = text.split("$$")
    if len(parts) < 3:
        return text
    for i in range(1, len(parts), 2):
        parts[i] = "\n" + _wrap_plain_display(parts[i], max_width) + "\n"
    return "$$".join(parts)
