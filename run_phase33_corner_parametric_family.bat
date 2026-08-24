@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" examples\phase33_corner_parametric_family.py
) else (
  python examples\phase33_corner_parametric_family.py
)
endlocal
