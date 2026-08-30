@echo off
setlocal
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
  set "PY=.venv\Scripts\python.exe"
) else (
  set "PY=python"
)
set "PYTHONPATH=%CD%"
"%PY%" examples\phase26_crossed_independent_analytic_trial.py
exit /b %ERRORLEVEL%
