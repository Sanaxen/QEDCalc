@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" examples\phase30_self_energy_renormalized_outer_bridge.py
) else (
  python examples\phase30_self_energy_renormalized_outer_bridge.py
)
endlocal
