@echo off
setlocal
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    set PY=.venv\Scripts\python.exe
) else (
    set PY=py
)

set PYTHONPATH=%CD%;%PYTHONPATH%

%PY% examples\three_loop_q01_modp_4line_remaining9_profile.py
if errorlevel 1 (
    echo Q01 4-line remaining-nine structural profile FAIL
    exit /b 1
)

echo Q01 4-line remaining-nine structural profile PASS
exit /b 0
