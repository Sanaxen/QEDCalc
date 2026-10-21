@echo off
setlocal
cd /d "%~dp0"
set "EQUATIONS=output\three_loop_integral_family_audit\vp05_target_symbolic_compressed.equations.json"
if not exist "%EQUATIONS%" (
 echo ERROR: Missing VP05 compressed equations: %EQUATIONS%
 exit /b 2
)
echo [VP05] Same-prime modular certificate sampling; no Fermat/Kira.
python -m examples.three_loop_sector203_same_prime_certificate_samples --equations "%EQUATIONS%" --training 19 --holdouts 8 --max-attempts 120
exit /b %ERRORLEVEL%
