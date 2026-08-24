r"""Readable Markdown/LaTeX formatting for long display equations.

Phase 84 uses a structure-preserving rule: never insert ``\\`` directly into
an arbitrary TeX brace group.  Long expressions are instead replaced, for
presentation only, by recursively defined local proxy symbols.

Example::

    D_1 = denominator
    N_1 = N_{1,1} + N_{1,2}
    N_{1,1} = ...
    N_{1,2} = ...
    F = N_1 / D_1

If a proxy definition is still too long, the same decomposition is applied
again.  Whole fractions, top-level sums/differences, and explicit top-level
products (``\\times``/``\\cdot``) are decomposed recursively.  The original
mathematical token order is preserved.
"""
from __future__ import annotations

from dataclasses import dataclass
import re

_STRUCTURED = (
    r"\begin{aligned}", r"\begin{alignedat}", r"\begin{split}",
    r"\begin{cases}", r"\begin{array}", r"\begin{matrix}",
    r"\begin{pmatrix}", r"\begin{bmatrix}", r"\begin{gathered}",
    r"\begin{multline}",
)


def _visible_len(source: str) -> int:
    text = re.sub(r"\\[A-Za-z]+", "X", source)
    text = text.replace("{", "").replace("}", "")
    return len(text)


def _compact(expr: str) -> str:
    return " ".join(line.strip() for line in expr.splitlines() if line.strip())


def _read_braced(text: str, start: int) -> tuple[str, int] | None:
    if start >= len(text) or text[start] != "{":
        return None
    depth = 0
    begin = start + 1
    i = start
    while i < len(text):
        if text[i] == "\\" and i + 1 < len(text) and text[i + 1] in "{}":
            i += 2
            continue
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[begin:i], i + 1
            if depth < 0:
                return None
        i += 1
    return None


def _whole_fraction(expr: str) -> tuple[str, str, str] | None:
    """Parse an expression that is exactly optional-sign ``\\frac{N}{D}``."""
    s = _compact(expr)
    sign = ""
    if s.startswith("-"):
        sign = "-"
        s = s[1:].lstrip()
    if not s.startswith(r"\frac"):
        return None
    pos = len(r"\frac")
    while pos < len(s) and s[pos].isspace():
        pos += 1
    first = _read_braced(s, pos)
    if first is None:
        return None
    numerator, pos = first
    while pos < len(s) and s[pos].isspace():
        pos += 1
    second = _read_braced(s, pos)
    if second is None:
        return None
    denominator, pos = second
    if s[pos:].strip():
        return None
    return sign, numerator.strip(), denominator.strip()


def _top_level_ops(expr: str, operators: tuple[str, ...]) -> list[tuple[int, str]]:
    """Find safe top-level binary operator positions.

    Positions point to the beginning of the operator.  Braces, parentheses and
    brackets must all be balanced at the split point.
    """
    found: list[tuple[int, str]] = []
    brace = paren = bracket = 0
    i = 0
    while i < len(expr):
        ch = expr[i]
        if ch == "\\":
            m = re.match(r"\\[A-Za-z]+", expr[i:])
            if m:
                token = m.group(0)
                if brace == paren == bracket == 0 and token in operators:
                    found.append((i, token))
                i += len(token)
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
        elif brace == paren == bracket == 0 and ch in operators:
            prev = expr[:i].rstrip()
            # Do not split unary + or -.
            if ch in "+-" and (not prev or prev[-1] in "=+-*/,("):
                i += 1
                continue
            found.append((i, ch))
        i += 1
    return found


def _best_binary_split(expr: str) -> tuple[str, str, str] | None:
    """Split near the middle, preferring +/-, then explicit products."""
    s = _compact(expr)
    if not s:
        return None
    midpoint = len(s) / 2

    additive = _top_level_ops(s, ("+", "-"))
    if additive:
        pos, op = min(additive, key=lambda item: abs(item[0] - midpoint))
        left = s[:pos].strip()
        right = s[pos + len(op):].strip()
        if left and right:
            return left, op, right

    products = _top_level_ops(s, (r"\times", r"\cdot"))
    if products:
        pos, op = min(products, key=lambda item: abs(item[0] - midpoint))
        left = s[:pos].strip()
        right = s[pos + len(op):].strip()
        if left and right:
            return left, op, right
    return None


def _proxy_name(base: str, path: tuple[int, ...]) -> str:
    indices = ",".join(str(x) for x in path)
    return rf"{base}_{{{indices}}}"


@dataclass
class _ProxyFormatter:
    max_width: int
    max_depth: int = 16

    def definition_blocks(self, base: str, path: tuple[int, ...], expr: str,
                          depth: int = 0) -> list[str]:
        """Return display blocks for one recursively decomposed definition."""
        name = _proxy_name(base, path)
        rhs = _compact(expr)
        direct = rf"{name}={rhs}"
        if _visible_len(direct) <= self.max_width or depth >= self.max_depth:
            return [self._display(direct)]

        frac = _whole_fraction(rhs)
        if frac is not None:
            sign, numerator, denominator = frac
            n_name = _proxy_name(base, path + (1,))
            d_name = _proxy_name(base, path + (2,))
            root = rf"{name}={sign}\frac{{{n_name}}}{{{d_name}}}"
            blocks = [self._display(root)]
            blocks += self.definition_blocks(base, path + (1,), numerator, depth + 1)
            blocks += self.definition_blocks(base, path + (2,), denominator, depth + 1)
            return blocks

        split = _best_binary_split(rhs)
        if split is not None:
            left, op, right = split
            l_name = _proxy_name(base, path + (1,))
            r_name = _proxy_name(base, path + (2,))
            root = rf"{name}={l_name} {op} {r_name}"
            blocks = [self._display(root)]
            blocks += self.definition_blocks(base, path + (1,), left, depth + 1)
            blocks += self.definition_blocks(base, path + (2,), right, depth + 1)
            return blocks

        # No safe structural split is known.  Keep the mathematically valid
        # expression intact rather than risk corrupting TeX.  Validation reports
        # this as an unsplittable long definition instead of rewriting it.
        return [self._display(direct)]

    @staticmethod
    def _display(expr: str) -> str:
        return f"$$\n{expr}\n$$"

    def fraction_blocks(self, sign: str, numerator: str, denominator: str,
                        index: int) -> str:
        """Create recursive D_i/N_i definitions followed by their compact ratio."""
        blocks: list[str] = []
        # Denominator first, matching the human-readable convention requested.
        blocks += self.definition_blocks("D", (index,), denominator)
        blocks += self.definition_blocks("N", (index,), numerator)
        d_name = _proxy_name("D", (index,))
        n_name = _proxy_name("N", (index,))
        blocks.append(self._display(rf"{sign}\frac{{{n_name}}}{{{d_name}}}"))
        return "\n\n".join(blocks)


def _safe_plain_wrap(expr: str, max_width: int) -> str:
    """Wrap a non-fraction only when the split is structurally top-level."""
    s = _compact(expr)
    if _visible_len(s) <= max_width:
        return f"$$\n{s}\n$$"
    if any(marker in s for marker in _STRUCTURED):
        # Existing structured TeX is left unchanged; rewriting nested alignment
        # grammar is riskier than leaving a long but valid equation intact.
        return f"$$\n{expr.strip()}\n$$"

    split = _best_binary_split(s)
    if split is None:
        return f"$$\n{s}\n$$"

    formatter = _ProxyFormatter(max_width=max_width)
    # Generic long non-fractions use E_i proxies recursively.
    blocks = formatter.definition_blocks("E", (1,), s)
    blocks.append(formatter._display(_proxy_name("E", (1,))))
    return "\n\n".join(blocks)


def format_markdown_math(text: str, max_width: int = 92) -> str:
    """Format display equations with recursive proxy decomposition.

    A long whole-display fraction is rendered as recursive ``D_i`` and ``N_i``
    definitions followed by the compact ratio.  Proxy definitions are themselves
    recursively decomposed until they fit or no mathematically safe split is
    available.  No row break is injected inside arbitrary ``{...}`` groups.
    """
    parts = text.split("$$")
    if len(parts) < 3:
        return text

    formatter = _ProxyFormatter(max_width=max_width)
    out: list[str] = [parts[0]]
    fraction_index = 0
    for i in range(1, len(parts), 2):
        expr = parts[i]
        parsed = _whole_fraction(expr)
        if parsed is not None:
            sign, numerator, denominator = parsed
            if max(_visible_len(numerator), _visible_len(denominator)) > max_width:
                fraction_index += 1
                out.append(formatter.fraction_blocks(sign, numerator, denominator,
                                                     fraction_index))
            else:
                out.append(f"$$\n{expr.strip()}\n$$")
        else:
            out.append(_safe_plain_wrap(expr, max_width))
        if i + 1 < len(parts):
            out.append(parts[i + 1])
    return "".join(out)
