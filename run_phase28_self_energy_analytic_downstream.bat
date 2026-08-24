@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" examples\phase28_self_energy_analytic_downstream.py
) else (
  python examples\phase28_self_energy_analytic_downstream.py
)
endlocal
