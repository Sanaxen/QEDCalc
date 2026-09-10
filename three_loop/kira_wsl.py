"""Small Windows-to-WSL bridge for the optional Kira backend."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import subprocess
import time


@dataclass(frozen=True)
class KiraWSLRunResult:
    returncode: int
    wall_seconds: float
    linux_project_path: str
    version_text: str
    log_path: str


def _wsl_executable() -> str:
    exe = shutil.which("wsl.exe") or shutil.which("wsl")
    if not exe:
        raise RuntimeError("WSL executable was not found on PATH")
    return exe


def _safe_text(value: str | None) -> str:
    return value.strip() if value else ""


def _run_wsl_capture(args: list[str]) -> subprocess.CompletedProcess[str]:
    """Run WSL and decode its text output as UTF-8, never Windows cp932.

    Linux-side tools normally emit UTF-8.  On Japanese Windows, using
    ``text=True`` without an explicit encoding makes subprocess use cp932,
    which can fail before QEDCalc gets a chance to inspect stderr/stdout.
    ``errors='replace'`` keeps diagnostic output readable even if a tool emits
    an unexpected byte sequence.
    """
    return subprocess.run(
        args,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )


def wsl_path(path: str | Path) -> str:
    exe = _wsl_executable()
    resolved = str(Path(path).resolve())
    proc = _run_wsl_capture([exe, "wslpath", "-a", resolved])
    if proc.returncode != 0:
        details = _safe_text(proc.stderr) or _safe_text(proc.stdout)
        raise RuntimeError(f"wslpath failed: {details or 'no diagnostic output'}")
    value = _safe_text(proc.stdout)
    if not value:
        raise RuntimeError("wslpath returned an empty path")
    return value


def kira_wsl_version() -> str:
    exe = _wsl_executable()
    command = "command -v kira >/dev/null 2>&1 && kira --version"
    proc = _run_wsl_capture([exe, "bash", "-lc", command])
    stdout = _safe_text(proc.stdout)
    stderr = _safe_text(proc.stderr)
    if proc.returncode != 0:
        raise RuntimeError(
            "Kira was not found in the default WSL distribution. "
            "Install Kira in WSL or make 'kira' available on WSL PATH. "
            f"Details: {stderr or stdout or 'no diagnostic output'}"
        )
    return stdout or stderr or "Kira version output unavailable"


def run_kira_wsl(
    project_dir: str | Path,
    *,
    jobs_file: str = "jobs.yaml",
    log_name: str = "kira_run.log",
) -> KiraWSLRunResult:
    """Run Kira in WSL while keeping project files on the Windows checkout."""
    project = Path(project_dir).resolve()
    if not (project / jobs_file).is_file():
        raise FileNotFoundError(project / jobs_file)

    version = kira_wsl_version()
    linux_dir = wsl_path(project)
    log_path = project / log_name
    exe = _wsl_executable()

    # Pass the converted path as $1 instead of interpolating it into shell text.
    # This keeps spaces and non-ASCII Windows directory names safe.
    shell = 'cd -- "$1" && exec kira "$2"'
    started = time.perf_counter()
    with log_path.open("w", encoding="utf-8", newline="\n") as log:
        log.write(f"Kira version/preflight:\n{version}\n")
        log.write(f"WSL project path: {linux_dir}\n\n")
        log.flush()
        proc = subprocess.run(
            [exe, "bash", "-lc", shell, "qedcalc-kira", linux_dir, jobs_file],
            stdout=log,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    wall = time.perf_counter() - started
    return KiraWSLRunResult(
        returncode=int(proc.returncode),
        wall_seconds=wall,
        linux_project_path=linux_dir,
        version_text=version,
        log_path=str(log_path),
    )
