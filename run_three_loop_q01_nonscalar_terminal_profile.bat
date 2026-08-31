@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%CD%;%PYTHONPATH%"

if exist ".venv\Scripts\python.exe" (
    set PY=.venv\Scripts\python.exe
) else (
    set PY=py
)

%PY% examples\three_loop_q01_nonscalar_terminal_profile.py
if errorlevel 1 (
    echo Q01 nonscalar symbolic terminal profile FAIL
    exit /b 1
)

echo Q01 nonscalar symbolic terminal profile PASS
exit /b 0
