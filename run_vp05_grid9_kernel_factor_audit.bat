@echo off
setlocal
cd /d "%~dp0"
set "ROOT=output\three_loop_integral_family_audit"
if not exist "%ROOT%\vp05_independent_prime_certificate_grid9.json" (
 echo ERROR: Missing grid9 independent prime trial JSON
 exit /b 2
)
echo [VP05] Recompute 80 grid9 points and audit common factors for five residual rows.
python -m examples.three_loop_sector203_grid9_kernel_factor_audit
exit /b %ERRORLEVEL%
