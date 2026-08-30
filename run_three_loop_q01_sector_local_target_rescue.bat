@echo off
setlocal
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    set PY=.venv\Scripts\python.exe
) else (
    set PY=py
)

set PYTHONPATH=%CD%;%PYTHONPATH%
echo QEDCalc Q01 sector-local target rescue audit
%PY% examples\three_loop_q01_sector_local_target_rescue.py
if errorlevel 1 (
    echo Q01 sector-local target rescue audit FAIL
    exit /b 1
)

echo Q01 sector-local target rescue audit PASS
exit /b 0
