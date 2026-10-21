@echo off
setlocal
cd /d "%~dp0"
set "EQUATIONS=output\three_loop_integral_family_audit\vp05_target_symbolic_compressed.equations.json"
if not exist "%EQUATIONS%" (
 echo ERROR: Missing compressed VP05 equations
 exit /b 2
)
echo [VP05] Independent 2D-grid modular certificates; no Fermat/Kira.
python -m examples.three_loop_sector203_same_prime_certificate_samples --equations "%EQUATIONS%" --grid-v2 --training 19 --holdouts 8 --max-attempts 120 --output output\three_loop_integral_family_audit\vp05_same_prime_certificate_samples_grid_v2.json
exit /b %ERRORLEVEL%
