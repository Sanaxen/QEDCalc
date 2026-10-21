@echo off
setlocal
cd /d "%~dp0"
set "CRT=output\three_loop_integral_family_audit\vp05_two_prime_crt_candidate_audit.json"
if not exist "%CRT%" (
 echo ERROR: Missing two-prime CRT candidate archive
 exit /b 2
)
echo [VP05] Bounded exact rational-function replay: five compressed IBP columns.
python -m examples.three_loop_sector203_exact_compressed_certificate_replay --max-columns 5 --max-input-terms 20000
exit /b %ERRORLEVEL%
