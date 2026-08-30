@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%CD%;%PYTHONPATH%"

if exist ".venv\Scripts\python.exe" (
    set PY=.venv\Scripts\python.exe
) else (
    set PY=py
)

echo QEDCalc Q01 local 15-equation blocker elimination audit
%PY% examples\three_loop_q01_local_block_elimination.py
if errorlevel 1 (
    echo Q01 local blocker elimination audit FAIL
    exit /b 1
)

echo Q01 local blocker elimination audit PASS
exit /b 0
