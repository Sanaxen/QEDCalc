@echo off
setlocal
set PYTHONPATH=%~dp0
if exist "%~dp0.venv\Scripts\python.exe" (
  "%~dp0.venv\Scripts\python.exe" "%~dp0examples\phase14_ladder_finite_checkpoint_trial.py"
) else (
  python "%~dp0examples\phase14_ladder_finite_checkpoint_trial.py"
)
endlocal
