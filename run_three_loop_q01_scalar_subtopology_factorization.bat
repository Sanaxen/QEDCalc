@echo off
setlocal
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    set PY=.venv\Scripts\python.exe
) else (
    set PY=py
)

set PYTHONPATH=%CD%
%PY% examples\three_loop_q01_scalar_subtopology_factorization.py
if errorlevel 1 (
    echo Q01 scalar-subtopology factorization audit FAIL
    exit /b 1
)

echo Q01 scalar-subtopology factorization audit PASS
exit /b 0
