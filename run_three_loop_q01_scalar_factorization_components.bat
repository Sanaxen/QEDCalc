@echo off
setlocal
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    set PY=.venv\Scripts\python.exe
) else (
    set PY=py
)

set "PYTHONPATH=%CD%;%PYTHONPATH%"
%PY% examples\three_loop_q01_scalar_factorization_components.py
if errorlevel 1 (
    echo Q01 explicit factorized component audit FAIL
    exit /b 1
)

echo Q01 explicit factorized component audit PASS
exit /b 0
