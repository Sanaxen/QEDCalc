@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" examples\phase78_crossed_end_to_end_checkpoint.py
) else (
  python examples\phase78_crossed_end_to_end_checkpoint.py
)
endlocal
