@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" examples\phase32_corner_raw_pair_bridge.py
) else (
  python examples\phase32_corner_raw_pair_bridge.py
)
endlocal
