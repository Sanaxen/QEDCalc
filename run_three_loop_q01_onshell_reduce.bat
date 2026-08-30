@echo off
setlocal
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    set PY=.venv\Scripts\python.exe
) else (
    set PY=py
)

echo QEDCalc Q01 finite-q on-shell scalar reduction
%PY% examples\three_loop_q01_onshell_reduce.py
if errorlevel 1 (
    echo Q01 finite-q on-shell scalar reduction FAIL
    exit /b 1
)

echo Q01 finite-q on-shell scalar reduction PASS
exit /b 0
