@echo off
setlocal
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" examples\phase22_crossed_v_bridge_trial.py
) else (
  python examples\phase22_crossed_v_bridge_trial.py
)
endlocal
