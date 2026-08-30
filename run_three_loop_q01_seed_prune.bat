@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%CD%;%PYTHONPATH%"

if exist ".venv\Scripts\python.exe" (
    set PY=.venv\Scripts\python.exe
) else (
    set PY=py
)

echo QEDCalc Q01 bounded Laporta seed pruning
%PY% examples\three_loop_q01_seed_prune.py
if errorlevel 1 (
    echo Q01 bounded Laporta seed pruning FAIL
    exit /b 1
)

echo Q01 bounded Laporta seed pruning PASS
exit /b 0
