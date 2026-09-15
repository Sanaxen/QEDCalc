"""Patch the Q01 Fermat coefficient backend to use direct Fermat stdio.

The first Fermat backend attempted to redirect output from inside Fermat.  On the
user's Fermat 7.9b environment this can stall before the self-test completes.
This wrapper keeps the validated synthesis implementation but replaces only the
Fermat invocation/output parser with the same direct stdin/stdout mode that was
confirmed by the standalone probe.
"""
from __future__ import annotations

import re
import subprocess

import examples.three_loop_q01_projected_amplitude_master_coefficients_fermat as impl


_STATUS_PREFIX_RE = re.compile(
    r"^(?:Elapsed CPU time:\s*[0-9.]+\s*>\s*)+",
    flags=re.I,
)


def _clean_candidate(block: str) -> str:
    cleaned = " ".join(line.strip() for line in block.splitlines() if line.strip())
    # Fermat 7.9b sometimes emits the previous timing line and next prompt in
    # the same regex block, e.g. "Elapsed CPU time: 0.000 > <expression>".
    # Remove any such status/prompt prefix before interpreting the result.
    previous = None
    while cleaned != previous:
        previous = cleaned
        cleaned = _STATUS_PREFIX_RE.sub("", cleaned).strip()
        if cleaned.startswith(">"):
            cleaned = cleaned[1:].strip()
    return cleaned


def _run_fermat_sum_stdio(parts: list[str], symbols: set[str]) -> str:
    if not parts:
        return "0"

    lines: list[str] = []
    for symbol in sorted(symbols):
        if not symbol.replace("_", "").isalnum() or symbol[0].isdigit():
            raise RuntimeError(f"Fermat backend does not support symbol name safely: {symbol!r}")
        lines.append(f"&(J={symbol});")
    lines.extend(
        [
            "q := " + "+".join(f"({part})" for part in parts) + ";",
            "q;",
            "&q",
        ]
    )
    script = "\n".join(lines) + "\n"

    proc = subprocess.run(
        ["wsl.exe", "bash", "-lc", "cd $HOME/fermat/Ferl7 && ./fer64"],
        input=script,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            "Fermat failed with exit code "
            f"{proc.returncode}. stdout={proc.stdout[-4000:]!r} stderr={proc.stderr[-4000:]!r}"
        )

    # Fermat prints one prompt block per command.  Capture every prompt-to-timing
    # block and choose the last actual algebraic result after stripping status
    # chatter.  This deliberately tolerates the Fermat 7.9b prompt/timing layout
    # observed on the user's WSL installation.
    blocks = re.findall(r">\s*(.*?)\n\s*Elapsed CPU time:", proc.stdout, flags=re.S)
    candidates: list[str] = []
    for block in blocks:
        cleaned = _clean_candidate(block)
        if not cleaned:
            continue
        if cleaned.startswith("Change of polynomial variable:"):
            continue
        if cleaned.lower().startswith("elapsed cpu time:"):
            continue
        candidates.append(cleaned)
    if not candidates:
        raise RuntimeError(
            "Could not parse Fermat result from direct stdout. Tail:\n" + proc.stdout[-4000:]
        )

    return candidates[-1]


impl._run_fermat_sum = _run_fermat_sum_stdio

if __name__ == "__main__":
    impl.main()
