@echo off
setlocal
cd /d %~dp0

echo QEDCalc Phase 84 full two-loop process report
python examples\phase84_full_process_validation.py
if errorlevel 1 (
    echo Phase 84 validation FAIL
    exit /b 1
)

echo Phase 84 validation PASS
endlocal
