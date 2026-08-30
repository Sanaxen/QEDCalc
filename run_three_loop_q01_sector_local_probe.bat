@echo off
setlocal
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    set PY=.venv\Scripts\python.exe
) else (
    set PY=py
)

set PYTHONPATH=%CD%;%PYTHONPATH%
echo QEDCalc Q01 generic-point sector-local Laporta probe audit
%PY% examples\three_loop_q01_sector_local_probe.py
if errorlevel 1 (
    echo Q01 generic-point sector-local Laporta probe audit FAIL
    exit /b 1
)

echo Q01 generic-point sector-local Laporta probe audit PASS
exit /b 0
