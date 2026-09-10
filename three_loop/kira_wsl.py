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


def wsl_path(path: str | Path) -> str:
    exe = _wsl_executable()
    resolved = str(Path(path).resolve())
    proc = subprocess.run(
        [exe, "wslpath", "-a", resolved],
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"wslpath failed: {proc.stderr.strip() or proc.stdout.strip()}")
    value = proc.stdout.strip()
    if not value:
        raise RuntimeError("wslpath returned an empty path")
    return value


def kira_wsl_version() -> str:
    exe = _wsl_executable()
    command = "command -v kira >/dev/null 2>&1 && kira --version"
    proc = subprocess.run(
        [exe, "bash", "-lc", command],
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            "Kira was not found in the default WSL distribution. "
            "Install Kira in WSL or make 'kira' available on WSL PATH. "
            f"Details: {proc.stderr.strip() or proc.stdout.strip()}"
        )
    return (proc.stdout.strip() or proc.stderr.strip()).strip()


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
