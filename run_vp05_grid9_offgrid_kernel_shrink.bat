@echo off
setlocal
cd /d "%~dp0"
set "TRIAL=output\three_loop_integral_family_audit\vp05_independent_prime_certificate_grid9.json"
if not exist "%TRIAL%" (
 echo ERROR: Missing grid9 independent-prime trial
 exit /b 2
)
echo [VP05] Add 12 off-grid points to five residual kernels; keep ten holdouts.
python -m examples.three_loop_sector203_grid9_offgrid_kernel_shrink
exit /b %ERRORLEVEL%
