@echo off
setlocal
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    set PY=.venv\Scripts\python.exe
) else (
    set PY=py
)

set PYTHONPATH=%CD%
%PY% examples\three_loop_q01_modp_4line_expanded48_free_columns.py
if errorlevel 1 (
    echo Q01 four-line expanded 48-block free-column audit FAIL
    exit /b 1
)

echo Q01 four-line expanded 48-block free-column audit PASS
exit /b 0
