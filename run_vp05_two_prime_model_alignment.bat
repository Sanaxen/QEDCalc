@echo off
setlocal
cd /d "%~dp0"
set "ROOT=output\three_loop_integral_family_audit"
if not exist "%ROOT%\vp05_modular_certificate_assembled.json" (
 echo ERROR: Missing first-prime assembled certificate
 exit /b 2
)
if not exist "%ROOT%\vp05_independent_prime_certificate_grid9.json" (
 echo ERROR: Missing second-prime grid9 trial
 exit /b 2
)
if not exist "%ROOT%\vp05_grid9_offgrid_kernel_shrink.json" (
 echo ERROR: Missing second-prime offgrid recovery
 exit /b 2
)
echo [VP05] Assemble and projectively align all 166 models over two primes.
python -m examples.three_loop_sector203_two_prime_model_alignment
exit /b %ERRORLEVEL%
