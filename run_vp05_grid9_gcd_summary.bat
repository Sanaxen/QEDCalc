@echo off
setlocal
cd /d "%~dp0"
set "SOURCE=output\three_loop_integral_family_audit\vp05_grid9_kernel_factor_audit.json"
if not exist "%SOURCE%" (
 echo ERROR: Missing grid9 factor audit JSON
 exit /b 2
)
echo [VP05] Summarize five-row kernel GCD degrees and reduced basis bounds.
python -m examples.three_loop_sector203_grid9_gcd_summary
exit /b %ERRORLEVEL%
