@echo off
setlocal
cd /d "%~dp0"
set "ROOT=output\three_loop_integral_family_audit"
if not exist "%ROOT%\vp05_same_prime_certificate_samples_grid_v3.json" (
 echo ERROR: Missing grid-v3 certificate sample archive
 exit /b 2
)
if not exist "%ROOT%\vp05_certificate_degree4_trial.json" (
 echo ERROR: Missing degree4 trial archive
 exit /b 2
)
echo [VP05] Extend 39 training to 63; preserve original 8 holdouts.
python -m examples.three_loop_sector203_certificate_extend_training --base "%ROOT%\vp05_same_prime_certificate_samples_grid_v3.json" --output "%ROOT%\vp05_same_prime_certificate_samples_grid_v4.json" --extra-training 24 --z-base 31 --z-step 43 --d-base 59 --d-step 71 --columns 11
if errorlevel 1 exit /b %ERRORLEVEL%
echo [VP05] Trial degree5 on 53 remaining rows; recheck previous 113 on 24 new points.
python -m examples.three_loop_sector203_certificate_degree5_trial
exit /b %ERRORLEVEL%
