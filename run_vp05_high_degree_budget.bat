@echo off
setlocal
cd /d "%~dp0"
set "SAMPLES=output\three_loop_integral_family_audit\vp05_same_prime_certificate_samples_grid_v3.json"
if not exist "%SAMPLES%" (
 echo ERROR: Missing grid-v3 VP05 certificate samples
 exit /b 2
)
echo [VP05] Higher-degree interpolation budget/rank preflight ONLY; no Fermat/Kira.
python -m examples.three_loop_sector203_high_degree_budget --samples "%SAMPLES%" --max-degree 6
exit /b %ERRORLEVEL%
