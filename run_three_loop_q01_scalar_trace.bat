@echo off
setlocal
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    set PY=.venv\Scripts\python.exe
) else (
    set PY=py
)

echo QEDCalc Q01 scalar trace reduction
%PY% run_three_loop_q01_scalar_trace.py
if errorlevel 1 (
    echo Q01 scalar trace reduction FAIL
    exit /b 1
)

echo Q01 scalar trace reduction PASS
exit /b 0
