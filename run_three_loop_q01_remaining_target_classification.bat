@echo off
setlocal
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    set PY=.venv\Scripts\python.exe
) else (
    set PY=py
)

set PYTHONPATH=%CD%;%PYTHONPATH%
echo QEDCalc Q01 remaining-target corrected classification
%PY% examples\three_loop_q01_remaining_target_classification.py
if errorlevel 1 (
    echo Q01 remaining-target corrected classification FAIL
    exit /b 1
)

echo Q01 remaining-target corrected classification PASS
exit /b 0
