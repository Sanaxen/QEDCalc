@echo off
setlocal
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    set PY=.venv\Scripts\python.exe
) else (
    set PY=py
)

set PYTHONPATH=%CD%;%PYTHONPATH%

%PY% examples\three_loop_q01_modp_sector_descent_driver.py --source output\3loop_q01_modp_largest_5line_descent.json --output output\3loop_q01_modp_largest_4line_descent.json --sector auto
if errorlevel 1 (
    echo Q01 largest 4-line generic mod-p sector descent FAIL
    exit /b 1
)

echo Q01 largest 4-line generic mod-p sector descent PASS
exit /b 0
