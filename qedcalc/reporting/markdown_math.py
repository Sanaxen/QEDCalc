r"""Readable Markdown/LaTeX formatting for long display equations.

Phase 84 uses a structure-preserving rule: never insert ``\\`` directly into
an arbitrary TeX brace group. Long expressions are instead replaced, for
presentation only, by recursively defined local proxy symbols.

Recursive decomposition order:
1. whole fractions -> numerator / denominator proxies;
2. top-level sums and differences;
3. explicit top-level products (``\\times`` / ``\\cdot``);
4. implicit products, preferring original source-line boundaries and then safe
   top-level whitespace boundaries.

If a proxy definition is still too long, the same process is applied again.
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

_BINDING_COMMANDS = (r"\int", r"\iint", r"\iiint", r"\oint", r"\sum", r"\prod", r"\lim")


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
        if ch == "{": brace += 1
        elif ch == "}": brace = max(0, brace - 1)
        elif ch == "(": paren += 1
        elif ch == ")": paren = max(0, paren - 1)
        elif ch == "[": bracket += 1
        elif ch == "]": bracket = max(0, bracket - 1)
        elif brace == paren == bracket == 0 and ch in operators:
            prev = expr[:i].rstrip()
            if ch in "+-" and (not prev or prev[-1] in "=+-*/,("):
                i += 1
                continue
            found.append((i, ch))
        i += 1
    return found


def _source_line_product_split(expr: str) -> tuple[str, str, str] | None:
    """Split an implicit product at an original source newline near its middle."""
    lines = [line.strip() for line in expr.splitlines() if line.strip()]
    if len(lines) < 2:
        return None
    # Pick a balanced cut by visible width, not simply by line count.
    total = sum(_visible_len(line) for line in lines)
    running = 0
    best_index = 1
    best_distance = float("inf")
    for i in range(1, len(lines)):
        running += _visible_len(lines[i - 1])
        distance = abs(running - total / 2)
        if distance < best_distance:
            best_distance = distance
            best_index = i
    left = " ".join(lines[:best_index]).strip()
    right = " ".join(lines[best_index:]).strip()
    if left and right:
        return left, "", right
    return None


def _top_level_space_positions(expr: str) -> list[int]:
    """Find safe top-level whitespace boundaries for implicit multiplication."""
    positions: list[int] = []
    brace = paren = bracket = 0
    i = 0
    while i < len(expr):
        ch = expr[i]
        if ch == "\\":
            m = re.match(r"\\[A-Za-z]+", expr[i:])
            if m:
                i += len(m.group(0))
                continue
        if ch == "{": brace += 1
        elif ch == "}": brace = max(0, brace - 1)
        elif ch == "(": paren += 1
        elif ch == ")": paren = max(0, paren - 1)
        elif ch == "[": bracket += 1
        elif ch == "]": bracket = max(0, bracket - 1)
        elif ch.isspace() and brace == paren == bracket == 0:
            start = i
            while i < len(expr) and expr[i].isspace():
                i += 1
            left = expr[:start].rstrip()
            right = expr[i:].lstrip()
            if left and right:
                # Avoid separating a binding operator from its immediate measure.
                if not any(left.endswith(cmd) for cmd in _BINDING_COMMANDS):
                    if not right.startswith(("d^", r"\limits", "_", "^")):
                        positions.append(start)
            continue
        i += 1
    return positions


def _implicit_product_split(expr: str) -> tuple[str, str, str] | None:
    s = _compact(expr)
    positions = _top_level_space_positions(s)
    if not positions:
        return None
    midpoint = len(s) / 2
    pos = min(positions, key=lambda p: abs(p - midpoint))
    left = s[:pos].strip()
    right = s[pos:].strip()
    if left and right:
        return left, "", right
    return None


def _best_binary_split(expr: str, original_expr: str | None = None) -> tuple[str, str, str] | None:
    """Split near the middle, preferring algebraic then implicit-product boundaries."""
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

    if original_expr is not None:
        source_split = _source_line_product_split(original_expr)
        if source_split is not None:
            return source_split

    return _implicit_product_split(s)


def _proxy_name(base: str, path: tuple[int, ...]) -> str:
    indices = ",".join(str(x) for x in path)
    return rf"{base}_{{{indices}}}"


@dataclass
class _ProxyFormatter:
    max_width: int
    max_depth: int = 20

    def definition_blocks(self, base: str, path: tuple[int, ...], expr: str,
                          depth: int = 0) -> list[str]:
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

        split = _best_binary_split(rhs, expr)
        if split is not None:
            left, op, right = split
            l_name = _proxy_name(base, path + (1,))
            r_name = _proxy_name(base, path + (2,))
            join = f" {op} " if op else r"\,"
            root = rf"{name}={l_name}{join}{r_name}"
            blocks = [self._display(root)]
            blocks += self.definition_blocks(base, path + (1,), left, depth + 1)
            blocks += self.definition_blocks(base, path + (2,), right, depth + 1)
            return blocks

        return [self._display(direct)]

    @staticmethod
    def _display(expr: str) -> str:
        return f"$$\n{expr}\n$$"

    def fraction_blocks(self, sign: str, numerator: str, denominator: str,
                        index: int) -> str:
        blocks: list[str] = []
        blocks += self.definition_blocks("D", (index,), denominator)
        blocks += self.definition_blocks("N", (index,), numerator)
        d_name = _proxy_name("D", (index,))
        n_name = _proxy_name("N", (index,))
        blocks.append(self._display(rf"{sign}\frac{{{n_name}}}{{{d_name}}}"))
        return "\n\n".join(blocks)


def _safe_plain_wrap(expr: str, max_width: int) -> str:
    s = _compact(expr)
    if _visible_len(s) <= max_width:
        return f"$$\n{s}\n$$"
    if any(marker in s for marker in _STRUCTURED):
        return f"$$\n{expr.strip()}\n$$"

    formatter = _ProxyFormatter(max_width=max_width)
    split = _best_binary_split(s, expr)
    if split is None:
        return f"$$\n{s}\n$$"
    blocks = formatter.definition_blocks("E", (1,), expr)
    blocks.append(formatter._display(_proxy_name("E", (1,))))
    return "\n\n".join(blocks)


def format_markdown_math(text: str, max_width: int = 92) -> str:
    """Format display equations with recursive proxy decomposition."""
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
