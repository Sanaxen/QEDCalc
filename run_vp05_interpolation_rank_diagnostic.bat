@echo off
setlocal
cd /d "%~dp0"
set "SAMPLES=output\three_loop_integral_family_audit\vp05_same_prime_certificate_samples.json"
if not exist "%SAMPLES%" (
 echo ERROR: Missing same-prime VP05 samples: %SAMPLES%
 exit /b 2
)
echo [VP05] Diagnose interpolation rank and nonunique kernels; no Fermat/Kira.
python -m examples.three_loop_sector203_interpolation_rank_diagnostic --samples "%SAMPLES%" --degree 3
exit /b %ERRORLEVEL%
