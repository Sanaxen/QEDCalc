@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" examples\phase34_corner_raw_projector.py
) else (
  python examples\phase34_corner_raw_projector.py
)
endlocal
