@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" examples\phase55_corner_local_finite_ownership.py
) else (
  python examples\phase55_corner_local_finite_ownership.py
)
endlocal
