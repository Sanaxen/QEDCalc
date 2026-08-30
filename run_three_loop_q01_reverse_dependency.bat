@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%CD%;%PYTHONPATH%"

if exist ".venv\Scripts\python.exe" (
    set PY=.venv\Scripts\python.exe
) else (
    set PY=py
)

echo QEDCalc Q01 reverse one-hop dependency audit
%PY% examples\three_loop_q01_reverse_dependency.py
if errorlevel 1 (
    echo Q01 reverse one-hop dependency audit FAIL
    exit /b 1
)

echo Q01 reverse one-hop dependency audit PASS
exit /b 0
