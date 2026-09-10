"""Small Windows-to-WSL bridge for the optional Kira backend."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PureWindowsPath
import re
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
    """Run WSL and decode Linux-side output explicitly as UTF-8."""
    return subprocess.run(
        args,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )


def _windows_path_to_wsl_mount(path: str) -> str:
    """Convert an absolute Windows drive path to WSL's /mnt/<drive>/ form.

    This conversion is intentionally performed in Python rather than by
    invoking ``wslpath``.  That avoids quoting/backslash issues when the path
    contains Japanese characters, spaces, or other non-ASCII text.
    """
    win = PureWindowsPath(path)
    drive = win.drive
    if not re.fullmatch(r"[A-Za-z]:", drive):
        raise ValueError(f"not an absolute Windows drive path: {path!r}")

    drive_letter = drive[0].lower()
    parts = win.parts[1:]
    suffix = "/".join(parts)
    return f"/mnt/{drive_letter}/{suffix}" if suffix else f"/mnt/{drive_letter}"


def wsl_path(path: str | Path) -> str:
    """Convert a Windows checkout path to the corresponding WSL mount path."""
    resolved = str(Path(path).resolve())
    try:
        return _windows_path_to_wsl_mount(resolved)
    except ValueError:
        # Fallback for unusual environments where the caller is not running
        # from a normal Windows drive path.
        exe = _wsl_executable()
        proc = _run_wsl_capture([exe, "wslpath", "-a", resolved])
        if proc.returncode != 0:
            details = _safe_text(proc.stderr) or _safe_text(proc.stdout)
            raise RuntimeError(
                f"wslpath failed: {details or 'no diagnostic output'}"
            )
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


def fermat_wsl_path() -> str:
    """Locate a Fermat executable inside the default WSL distribution.

    Kira is often launched by QEDCalc as a non-interactive WSL process.  In
    that mode Ubuntu's interactive ``~/.bashrc`` is not a reliable place to
    obtain FERMATPATH.  Detect Fermat explicitly and pass the path to Kira.

    Detection order:
      1. an already exported executable FERMATPATH;
      2. ``fer64`` available on PATH;
      3. the standard QEDCalc setup location ``~/fermat/Ferl7/fer64``.
    """
    exe = _wsl_executable()
    command = r'''
if [ -n "${FERMATPATH:-}" ] && [ -x "$FERMATPATH" ]; then
    printf '%s\n' "$FERMATPATH"
elif command -v fer64 >/dev/null 2>&1; then
    command -v fer64
elif [ -x "$HOME/fermat/Ferl7/fer64" ]; then
    printf '%s\n' "$HOME/fermat/Ferl7/fer64"
else
    exit 1
fi
'''.strip()
    proc = _run_wsl_capture([exe, "bash", "-lc", command])
    value = _safe_text(proc.stdout)
    if proc.returncode != 0 or not value:
        details = _safe_text(proc.stderr)
        raise RuntimeError(
            "Fermat was not found in WSL. Set FERMATPATH to an executable "
            "Fermat binary, put fer64 on PATH, or install it at "
            "$HOME/fermat/Ferl7/fer64. "
            f"Details: {details or 'no diagnostic output'}"
        )
    return value.splitlines()[0].strip()


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
    fermat_path = fermat_wsl_path()
    linux_dir = wsl_path(project)
    log_path = project / log_name
    exe = _wsl_executable()

    # WSL supports changing the Linux working directory directly.  Avoid a
    # bash wrapper for the actual Kira process, and pass FERMATPATH explicitly
    # so execution does not depend on interactive shell startup files.
    started = time.perf_counter()
    with log_path.open("w", encoding="utf-8", newline="\n") as log:
        log.write(f"Kira version/preflight:\n{version}\n")
        log.write(f"Fermat path: {fermat_path}\n")
        log.write(f"WSL project path: {linux_dir}\n\n")
        log.flush()
        proc = subprocess.run(
            [
                exe,
                "--cd",
                linux_dir,
                "env",
                f"FERMATPATH={fermat_path}",
                "kira",
                jobs_file,
            ],
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
