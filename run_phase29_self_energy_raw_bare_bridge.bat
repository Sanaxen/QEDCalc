@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" examples\phase29_self_energy_raw_bare_bridge.py
) else (
  python examples\phase29_self_energy_raw_bare_bridge.py
)
endlocal
