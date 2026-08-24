@echo off
setlocal
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" examples\phase21_crossed_px_generation_trial.py
) else (
  python examples\phase21_crossed_px_generation_trial.py
)
endlocal
