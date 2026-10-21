@echo off
setlocal
cd /d "%~dp0"
set "ROOT=output\three_loop_integral_family_audit"
if not exist "%ROOT%\vp05_modular_certificate_assembled.json" (
 echo ERROR: Missing assembled modular certificate JSON
 exit /b 2
)
echo [VP05] Refit prime 1001003 on a 9-column grid with eight d-levels in training.
python -m examples.three_loop_sector203_independent_prime_certificate --columns 9 --output "%ROOT%\vp05_independent_prime_certificate_grid9.json"
exit /b %ERRORLEVEL%
