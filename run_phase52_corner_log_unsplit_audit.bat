@echo off
setlocal
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
    set "PY=.venv\Scripts\python.exe"
) else (
    set "PY=python"
)
set "PYTHONPATH=%CD%"
"%PY%" examples\phase52_corner_log_unsplit_audit.py
endlocal
