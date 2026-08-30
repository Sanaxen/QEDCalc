@echo off
setlocal
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    set PY=.venv\Scripts\python.exe
) else (
    set PY=py
)

set "PYTHONPATH=%CD%;%PYTHONPATH%"

echo QEDCalc Q01 dependency-driven IBP pivot audit
%PY% examples\three_loop_q01_dependency_audit.py
if errorlevel 1 (
    echo Q01 dependency-driven IBP pivot audit FAIL
    exit /b 1
)

echo Q01 dependency-driven IBP pivot audit PASS
exit /b 0
