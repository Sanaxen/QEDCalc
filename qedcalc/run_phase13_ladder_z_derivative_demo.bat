@echo off
setlocal
cd /d "%~dp0"
if exist .venv\Scripts\python.exe (
  .venv\Scripts\python.exe examples\phase13_ladder_z_derivative_trial.py
) else (
  python examples\phase13_ladder_z_derivative_trial.py
)
endlocal
