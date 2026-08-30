@echo off
setlocal
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    set PY=.venv\Scripts\python.exe
) else (
    set PY=py
)

set "PYTHONPATH=%CD%;%PYTHONPATH%"

echo QEDCalc Q01 finite-q p-q external-basis reduction
%PY% examples\three_loop_q01_pq_basis_reduce.py
if errorlevel 1 (
    echo Q01 finite-q p-q external-basis reduction FAIL
    exit /b 1
)

echo Q01 finite-q p-q external-basis reduction PASS
exit /b 0
