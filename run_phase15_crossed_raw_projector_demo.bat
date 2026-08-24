@echo off
setlocal
set PYTHONPATH=%~dp0
if exist "%~dp0.venv\Scripts\python.exe" (
  "%~dp0.venv\Scripts\python.exe" "%~dp0examples\phase15_crossed_raw_projector_trial.py"
) else (
  python "%~dp0examples\phase15_crossed_raw_projector_trial.py"
)
endlocal
