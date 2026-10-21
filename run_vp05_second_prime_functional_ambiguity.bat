@echo off
setlocal
cd /d "%~dp0"
set "ROOT=output\three_loop_integral_family_audit"
if not exist "%ROOT%\vp05_independent_prime_certificate.json" (
 echo ERROR: Missing independent-prime certificate JSON
 exit /b 2
)
echo [VP05] Replay 80 independent-prime points and audit 8 ambiguous kernels.
python -m examples.three_loop_sector203_second_prime_functional_ambiguity
exit /b %ERRORLEVEL%
