@echo off
setlocal
cd /d "%~dp0"
if exist .venv\Scripts\python.exe (
  .venv\Scripts\python.exe examples\phase23_crossed_u_tq_bridge_trial.py
) else (
  python examples\phase23_crossed_u_tq_bridge_trial.py
)
endlocal
