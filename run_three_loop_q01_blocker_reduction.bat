@echo off
setlocal
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    set PY=.venv\Scripts\python.exe
) else (
    set PY=py
)
set "PYTHONPATH=%CD%;%PYTHONPATH%"

echo QEDCalc Q01 blocker-layer reducibility audit
%PY% examples\three_loop_q01_blocker_reduction.py
if errorlevel 1 (
    echo Q01 blocker-layer reducibility audit FAIL
    exit /b 1
)

echo Q01 blocker-layer reducibility audit PASS
exit /b 0
