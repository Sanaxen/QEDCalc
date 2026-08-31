@echo off
setlocal
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    set PY=.venv\Scripts\python.exe
) else (
    set PY=py
)

set PYTHONPATH=%CD%;%PYTHONPATH%
%PY% examples\three_loop_q01_modp_largest_6line_descent.py
if errorlevel 1 (
    echo Q01 largest 6-line mod-p sector descent FAIL
    exit /b 1
)

echo Q01 largest 6-line mod-p sector descent PASS
exit /b 0
