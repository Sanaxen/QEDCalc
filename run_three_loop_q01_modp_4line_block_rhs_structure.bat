@echo off
setlocal
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    set PY=.venv\Scripts\python.exe
) else (
    set PY=py
)

set PYTHONPATH=%CD%;%PYTHONPATH%

%PY% examples\three_loop_q01_modp_4line_block_rhs_structure.py
if errorlevel 1 (
    echo Q01 four-line block RHS structure FAIL
    exit /b 1
)

echo Q01 four-line block RHS structure PASS
exit /b 0
