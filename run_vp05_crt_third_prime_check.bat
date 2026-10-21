@echo off
setlocal
cd /d "%~dp0"
set "CRT=output\three_loop_integral_family_audit\vp05_two_prime_crt_candidate_audit.json"
if not exist "%CRT%" (
 echo ERROR: Missing two-prime CRT candidate archive
 exit /b 2
)
echo [VP05] Check all CRT candidate coefficients at three fresh third-prime points.
python -m examples.three_loop_sector203_crt_third_prime_check
exit /b %ERRORLEVEL%
