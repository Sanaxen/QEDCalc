@echo off
setlocal
cd /d "%~dp0"
set "BASE=output\three_loop_integral_family_audit\vp05_same_prime_certificate_samples_grid_v2.json"
if not exist "%BASE%" (
 echo ERROR: Missing grid-v2 sample archive
 exit /b 2
)
echo [VP05] Add 20 independent same-prime training points; preserve 8 holdouts.
python -m examples.three_loop_sector203_certificate_extend_training --extra-training 20
if errorlevel 1 exit /b %ERRORLEVEL%
echo [VP05] Refit adaptive degrees with extended training; no Fermat/Kira.
python -m examples.three_loop_sector203_certificate_adaptive_degree --samples output\three_loop_integral_family_audit\vp05_same_prime_certificate_samples_grid_v3.json --output output\three_loop_integral_family_audit\vp05_certificate_adaptive_degree_grid_v3.json --max-degree 3
exit /b %ERRORLEVEL%
