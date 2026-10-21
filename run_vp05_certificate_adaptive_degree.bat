@echo off
setlocal
cd /d "%~dp0"
set "SAMPLES=output\three_loop_integral_family_audit\vp05_same_prime_certificate_samples_grid_v2.json"
if not exist "%SAMPLES%" (
 echo ERROR: Missing VP05 grid-v2 sample archive: %SAMPLES%
 exit /b 2
)
echo [VP05] Adaptive certificate degrees 0..3; held-out finite-field checks only.
python -m examples.three_loop_sector203_certificate_adaptive_degree --samples "%SAMPLES%" --max-degree 3
exit /b %ERRORLEVEL%
