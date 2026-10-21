@echo off
setlocal
cd /d "%~dp0"
set "INPUT=output\three_loop_integral_family_audit\vp05_same_prime_certificate_samples_grid_v3.json"
if not exist "%INPUT%" (
 echo ERROR: Missing VP05 grid-v3 certificate samples
 exit /b 2
)
echo [VP05] 39-point polynomial rank and rational kernel diagnostic; no Fermat/Kira.
python -m examples.three_loop_sector203_identifiability_diagnostic --samples "%INPUT%" --degree 3
exit /b %ERRORLEVEL%
