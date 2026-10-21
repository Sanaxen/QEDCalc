@echo off
setlocal
cd /d "%~dp0"
set "SRC=output\three_loop_integral_family_audit\vp05_independent_prime_certificate_grid9.json"
if not exist "%SRC%" (
 echo ERROR: Missing independent prime grid9 trial JSON
 exit /b 2
)
echo [VP05] Rank audit: 9-column degree-six monomials and five residual kernels.
python -m examples.three_loop_sector203_grid9_rank_audit
exit /b %ERRORLEVEL%
