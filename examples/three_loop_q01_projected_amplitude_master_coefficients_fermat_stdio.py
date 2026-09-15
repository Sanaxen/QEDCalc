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

    # Fermat prints one prompt block per command.  The final evaluated q block is
    # immediately followed by an 'Elapsed CPU time:' line.  Capture all such
    # blocks and take the final non-command/status block.
    blocks = re.findall(r">\s*(.*?)\n\s*Elapsed CPU time:", proc.stdout, flags=re.S)
    candidates: list[str] = []
    for block in blocks:
        cleaned = " ".join(line.strip() for line in block.splitlines() if line.strip())
        if not cleaned:
            continue
        if cleaned.startswith("Change of polynomial variable:"):
            continue
        candidates.append(cleaned)
    if not candidates:
        raise RuntimeError(
            "Could not parse Fermat result from direct stdout. Tail:\n" + proc.stdout[-4000:]
        )

    result = candidates[-1]
    return result


impl._run_fermat_sum = _run_fermat_sum_stdio

if __name__ == "__main__":
    impl.main()
