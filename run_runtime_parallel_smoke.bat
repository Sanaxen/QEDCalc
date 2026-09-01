@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" examples\runtime_parallel_smoke.py
) else (
  python examples\runtime_parallel_smoke.py
)
endlocal
