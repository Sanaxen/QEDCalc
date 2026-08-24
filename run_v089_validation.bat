@echo off
setlocal
cd /d %~dp0
echo QEDCalc v0.89 validation
python examples\phase82_seven_diagram_release_audit_stdlib.py
if errorlevel 1 exit /b 1
echo v0.89 validation PASS
endlocal
