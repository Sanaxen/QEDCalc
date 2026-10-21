@echo off
setlocal
cd /d "%~dp0"
set "SAMPLES=output\three_loop_integral_family_audit\vp05_same_prime_certificate_samples_grid_v2.json"
if not exist "%SAMPLES%" (
 echo ERROR: Missing 2D-grid samples. Run run_vp05_same_prime_certificate_grid_v2.bat first.
 exit /b 2
)
echo [VP05] Independent-grid interpolation rank diagnostic; no Fermat/Kira.
python -m examples.three_loop_sector203_interpolation_rank_diagnostic --samples "%SAMPLES%" --degree 3 --output output\three_loop_integral_family_audit\vp05_interpolation_rank_grid_v2.json
if errorlevel 1 exit /b %ERRORLEVEL%
echo [VP05] Independent-grid rational interpolation trial and holdouts.
python -m examples.three_loop_sector203_certificate_interpolation_trial --samples "%SAMPLES%" --degree 3 --output output\three_loop_integral_family_audit\vp05_certificate_interpolation_grid_v2.json
exit /b %ERRORLEVEL%
