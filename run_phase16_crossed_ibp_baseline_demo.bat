@echo off
setlocal
set PYTHONPATH=%~dp0
if exist "%~dp0.venv\Scripts\python.exe" (
  "%~dp0.venv\Scripts\python.exe" "%~dp0examples\phase16_crossed_ibp_baseline_trial.py"
) else (
  python "%~dp0examples\phase16_crossed_ibp_baseline_trial.py"
)
endlocal
