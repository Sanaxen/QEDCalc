@echo off
setlocal
cd /d "%~dp0"
set "ROOT=output\three_loop_integral_family_audit"
if not exist "%ROOT%\vp05_certificate_degree6_residual_trial.json" (
 echo ERROR: Missing degree6 residual trial JSON
 exit /b 2
)
echo [VP05] Assemble 166 modular rational models and replay 71 sample points.
python -m examples.three_loop_sector203_modular_certificate_assemble
exit /b %ERRORLEVEL%
