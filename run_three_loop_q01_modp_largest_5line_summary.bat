@echo off
setlocal
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    set PY=.venv\Scripts\python.exe
) else (
    set PY=py
)

set PYTHONPATH=%CD%;%PYTHONPATH%
%PY% examples\three_loop_q01_modp_largest_5line_summary.py
if errorlevel 1 (
    echo Q01 largest 5-line saved descent summary FAIL
    exit /b 1
)

exit /b 0
