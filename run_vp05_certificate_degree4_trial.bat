@echo off
setlocal
cd /d "%~dp0"
set "ROOT=output\three_loop_integral_family_audit"
if not exist "%ROOT%\vp05_same_prime_certificate_samples_grid_v3.json" (
 echo ERROR: Missing grid-v3 samples
 exit /b 2
)
if not exist "%ROOT%\vp05_certificate_adaptive_degree_grid_v3.json" (
 echo ERROR: Missing grid-v3 adaptive results
 exit /b 2
)
echo [VP05] Degree-(4,4) 72 unresolved coefficients; held-out modular trial only.
python -m examples.three_loop_sector203_certificate_degree4_trial
exit /b %ERRORLEVEL%
