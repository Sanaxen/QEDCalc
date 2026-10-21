@echo off
setlocal
cd /d "%~dp0"
set "ROOT=output\three_loop_integral_family_audit"
if not exist "%ROOT%\vp05_modular_certificate_assembled.json" (
 echo ERROR: Missing assembled modular certificate JSON
 exit /b 2
)
if not exist "%ROOT%\vp05_target_symbolic_compressed.equations.json" (
 echo ERROR: Missing compressed symbolic equation archive
 exit /b 2
)
echo [VP05] Independent prime 1001003, 70 training and 10 holdouts. No Fermat/Kira.
python -m examples.three_loop_sector203_independent_prime_certificate
exit /b %ERRORLEVEL%
