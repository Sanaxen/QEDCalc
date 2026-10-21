@echo off
setlocal
cd /d "%~dp0"
set "INPUT=output\three_loop_integral_family_audit\vp05_two_prime_model_alignment.json"
if not exist "%INPUT%" (
 echo ERROR: Missing two-prime model alignment JSON
 exit /b 2
)
echo [VP05] CRT reconstruction feasibility for 166 aligned certificate rows; no Fermat/Kira.
python -m examples.three_loop_sector203_two_prime_crt_audit
exit /b %ERRORLEVEL%
