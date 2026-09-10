"""Inspect Kira 3.x FORM export structure before fixing a parser grammar."""
from __future__ import annotations

from collections import Counter
from pathlib import Path
import json
import re


_INTEGRAL_RE = re.compile(r"\b([A-Za-z_]\w*)\(([-+0-9, ]+)\)")


def inspect_kira_form_export(path: str | Path, *, sample_limit: int = 12) -> dict[str, object]:
    path = Path(path)
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    nonempty = [line for line in lines if line.strip()]

    prefix_counts: Counter[str] = Counter()
    for line in nonempty:
        s = line.lstrip()
        if s.startswith("*"):
            prefix = "comment"
        elif s.startswith("#"):
            prefix = "preprocessor"
        elif s.lower().startswith("id "):
            prefix = "id"
        elif s.lower().startswith("fill "):
            prefix = "fill"
        elif s.startswith("+"):
            prefix = "plus_continuation"
        elif s.startswith("-"):
            prefix = "minus_continuation"
        elif s.endswith(";"):
            prefix = "semicolon_line"
        else:
            prefix = "other"
        prefix_counts[prefix] += 1

    integral_tokens: list[str] = []
    seen: set[str] = set()
    for match in _INTEGRAL_RE.finditer(text):
        token = match.group(0)
        if token not in seen:
            seen.add(token)
            integral_tokens.append(token)
            if len(integral_tokens) >= sample_limit:
                break

    statement_samples: list[str] = []
    buf: list[str] = []
    for line in lines:
        if not line.strip() and not buf:
            continue
        buf.append(line.rstrip())
        if ";" in line:
            joined = "\n".join(buf).strip()
            if joined:
                statement_samples.append(joined[:1200])
            buf = []
            if len(statement_samples) >= sample_limit:
                break

    interesting_samples = []
    for line in nonempty:
        s = line.strip()
        if (
            "Q01_4line" in s
            or "num(" in s
            or s.lower().startswith("id ")
            or s.lower().startswith("fill ")
        ):
            interesting_samples.append(s[:1200])
            if len(interesting_samples) >= sample_limit:
                break

    return {
        "path": str(path),
        "size_bytes": path.stat().st_size,
        "line_count": len(lines),
        "nonempty_line_count": len(nonempty),
        "prefix_counts": dict(sorted(prefix_counts.items())),
        "semicolon_count": text.count(";"),
        "num_wrapper_count": text.count("num("),
        "q01_token_count": text.count("Q01_4line"),
        "integral_token_samples": integral_tokens,
        "interesting_line_samples": interesting_samples,
        "statement_samples": statement_samples,
    }


def write_inspection_json(path: str | Path, output: str | Path) -> dict[str, object]:
    result = inspect_kira_form_export(path)
    Path(output).write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8",
        newline="\n",
    )
    return result
