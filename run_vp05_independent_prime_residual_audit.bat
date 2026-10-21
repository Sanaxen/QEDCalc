@echo off
setlocal
cd /d "%~dp0"
set "ROOT=output\three_loop_integral_family_audit"
if not exist "%ROOT%\vp05_independent_prime_certificate.json" (
 echo ERROR: Missing independent-prime fit JSON
 exit /b 2
)
echo [VP05] Classify second-prime unresolved rows by degree and nullity.
python -m examples.three_loop_sector203_independent_prime_residual_audit
exit /b %ERRORLEVEL%
