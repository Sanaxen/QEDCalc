@echo off
setlocal
cd /d "%~dp0"
set "INPUT=output\three_loop_integral_family_audit\vp05_independent_prime_certificate_grid9.json"
if not exist "%INPUT%" (
 echo ERROR: Missing grid9 independent-prime trial JSON
 exit /b 2
)
echo [VP05] Check 30 finite-field rational cross-products for five kernel rows.
python -m examples.three_loop_sector203_grid9_kernel_cross_product
exit /b %ERRORLEVEL%
