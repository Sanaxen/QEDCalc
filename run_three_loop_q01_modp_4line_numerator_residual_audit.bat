@echo off
setlocal
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    set PY=.venv\Scripts\python.exe
) else (
    set PY=py
)

set PYTHONPATH=%CD%;%PYTHONPATH%

%PY% examples\three_loop_q01_modp_4line_numerator_residual_audit.py
if errorlevel 1 (
    echo Q01 four-line numerator residual pivot audit FAIL
    exit /b 1
)

echo Q01 four-line numerator residual pivot audit PASS
exit /b 0
