@echo off
setlocal
cd /d "%~dp0"
set "ROOT=output\three_loop_integral_family_audit"
if not exist "%ROOT%\vp05_certificate_degree4_trial.json" (
 echo ERROR: Missing degree-4 trial archive
 exit /b 2
)
if not exist "%ROOT%\vp05_same_prime_certificate_samples_grid_v3.json" (
 echo ERROR: Missing grid-v3 training archive
 exit /b 2
)
echo [VP05] Classify degree-(4,4) kernel nullity for 72 targeted coefficients.
python -m examples.three_loop_sector203_degree4_kernel_diagnostic
exit /b %ERRORLEVEL%
