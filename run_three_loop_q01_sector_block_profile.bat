@echo off
setlocal
cd /d "%~dp0"
set PYTHONPATH=%CD%;%PYTHONPATH%

if exist ".venv\Scripts\python.exe" (
    set PY=.venv\Scripts\python.exe
) else (
    set PY=py
)

echo QEDCalc Q01 sector-wise blocker distribution profile
%PY% examples\three_loop_q01_sector_block_profile.py
if errorlevel 1 (
    echo Q01 sector-wise blocker distribution profile FAIL
    exit /b 1
)

echo Q01 sector-wise blocker distribution profile PASS
exit /b 0
