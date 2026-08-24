@echo off
setlocal
cd /d %~dp0
if exist .venv\Scripts\python.exe (
  .venv\Scripts\python.exe examples\phase18_crossed_parametric_bridge_trial.py
) else (
  python examples\phase18_crossed_parametric_bridge_trial.py
)
endlocal
