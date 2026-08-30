@echo off
setlocal
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    set PY=.venv\Scripts\python.exe
) else (
    set PY=py
)

set "PYTHONPATH=%CD%;%PYTHONPATH%"

echo QEDCalc Q01 scalar-to-integral-index mapping
%PY% examples\three_loop_q01_integral_map.py
if errorlevel 1 (
    echo Q01 scalar-to-integral-index mapping FAIL
    exit /b 1
)

echo Q01 scalar-to-integral-index mapping PASS
exit /b 0
