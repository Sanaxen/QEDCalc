@echo off
setlocal
cd /d "%~dp0"
set "ADAPTIVE=output\three_loop_integral_family_audit\vp05_certificate_adaptive_degree.json"
if not exist "%ADAPTIVE%" (
 echo ERROR: Missing adaptive-degree results: %ADAPTIVE%
 exit /b 2
)
echo [VP05] Classify unresolved adaptive fits; no Fermat/Kira.
python -m examples.three_loop_sector203_adaptive_unresolved_diagnostic
exit /b %ERRORLEVEL%
