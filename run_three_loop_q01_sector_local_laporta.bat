@echo off
setlocal
cd /d "%~dp0"
set PYTHONPATH=%CD%

if exist ".venv\Scripts\python.exe" (
    set PY=.venv\Scripts\python.exe
) else (
    set PY=py
)

echo QEDCalc Q01 largest-sector local Laporta audit
%PY% examples\three_loop_q01_sector_local_laporta.py
if errorlevel 1 (
    echo Q01 largest-sector local Laporta audit FAIL
    exit /b 1
)

echo Q01 largest-sector local Laporta audit PASS
exit /b 0
