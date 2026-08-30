@echo off
setlocal
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    set PY=.venv\Scripts\python.exe
) else (
    set PY=py
)

set "PYTHONPATH=%CD%;%PYTHONPATH%"
echo QEDCalc Q01 Laporta demand profile
%PY% examples\three_loop_q01_laporta_profile.py
if errorlevel 1 (
    echo Q01 Laporta demand profile FAIL
    exit /b 1
)

echo Q01 Laporta demand profile PASS
exit /b 0
