@echo off
setlocal
cd /d "%~dp0"
set "SAMPLES=output\three_loop_integral_family_audit\vp05_same_prime_certificate_samples.json"
if not exist "%SAMPLES%" (
 echo ERROR: Missing same-prime VP05 samples: %SAMPLES%
 echo Run run_vp05_same_prime_certificate_samples.bat first.
 exit /b 2
)
echo [VP05] Rational interpolation trial and reserved holdout checks ONLY; no Fermat/Kira.
python -m examples.three_loop_sector203_certificate_interpolation_trial --samples "%SAMPLES%" --degree 3
exit /b %ERRORLEVEL%
