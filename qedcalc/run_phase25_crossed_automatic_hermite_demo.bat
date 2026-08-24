@echo off
setlocal
cd /d "%~dp0"
if exist .venv\Scripts\python.exe (
  .venv\Scripts\python.exe examples\phase25_crossed_automatic_hermite_trial.py
) else (
  python examples\phase25_crossed_automatic_hermite_trial.py
)
endlocal
