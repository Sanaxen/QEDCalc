@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" examples\phase31_self_energy_raw_to_final.py
) else (
  python examples\phase31_self_energy_raw_to_final.py
)
endlocal
