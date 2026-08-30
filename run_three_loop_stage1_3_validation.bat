@echo off
setlocal
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    set PY=.venv\Scripts\python.exe
) else (
    set PY=py
)

echo QEDCalc three-loop stages 1-3 validation
%PY% -m pytest -q tests\test_three_loop_stage1_3.py tests\test_three_loop_onshell.py
if errorlevel 1 (
    echo Three-loop stages 1-3 validation FAIL
    exit /b 1
)

echo Three-loop stages 1-3 validation PASS
exit /b 0
