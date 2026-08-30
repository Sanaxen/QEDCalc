@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%CD%;%PYTHONPATH%"

if exist ".venv\Scripts\python.exe" (
    set PY=.venv\Scripts\python.exe
) else (
    set PY=py
)

echo QEDCalc Q01 one-step IBP frontier
%PY% examples\three_loop_q01_ibp_frontier.py
if errorlevel 1 (
    echo Q01 one-step IBP frontier FAIL
    exit /b 1
)

echo Q01 one-step IBP frontier PASS
exit /b 0
