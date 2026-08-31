@echo off
setlocal
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    set PY=.venv\Scripts\python.exe
) else (
    set PY=py
)

set PYTHONPATH=%CD%;%PYTHONPATH%

%PY% examples\three_loop_q01_modp_4line_neighbor_rescue.py
if errorlevel 1 (
    echo Q01 4-line one-neighbor mod-p rescue FAIL
    exit /b 1
)

echo Q01 4-line one-neighbor mod-p rescue PASS
exit /b 0
