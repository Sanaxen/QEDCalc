@echo off
setlocal
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    set PY=.venv\Scripts\python.exe
) else (
    set PY=py
)

set "PYTHONPATH=%CD%;%PYTHONPATH%"
%PY% examples\three_loop_q01_master_candidate_manifest.py
if errorlevel 1 (
    echo Q01 master candidate manifest FAIL
    exit /b 1
)

echo Q01 master candidate manifest PASS
exit /b 0
