@echo off
setlocal
cd /d "%~dp0"
set "ROOT=output\three_loop_integral_family_audit"
if not exist "%ROOT%\vp05_same_prime_certificate_samples_grid_v4.json" (
 echo ERROR: Missing grid-v4 samples
 exit /b 2
)
if not exist "%ROOT%\vp05_certificate_degree5_trial_grid_v4.json" (
 echo ERROR: Missing degree5 trial
 exit /b 2
)
echo [VP05] Diagnose remaining eight degree5 kernels and trial degree6 where appropriate.
python -m examples.three_loop_sector203_certificate_degree6_residual
exit /b %ERRORLEVEL%
