@echo off
setlocal
cd /d "%~dp0"
set "EQUATIONS=output\three_loop_integral_family_audit\vp05_target_symbolic_compressed.equations.json"
if not exist "%EQUATIONS%" (
 echo ERROR: Missing compressed VP05 input: %EQUATIONS%
 exit /b 2
)
echo [VP05] Dual certificate feasibility audit ONLY. No Fermat/Kira.
python -m examples.three_loop_sector203_dual_certificate_preflight --equations "%EQUATIONS%"
exit /b %ERRORLEVEL%
