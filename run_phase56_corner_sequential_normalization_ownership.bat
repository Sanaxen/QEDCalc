@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" examples\phase56_corner_sequential_normalization_ownership.py
) else (
  python examples\phase56_corner_sequential_normalization_ownership.py
)
endlocal
