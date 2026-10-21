@echo off
setlocal
cd /d "%~dp0"
set "ROOT=output\three_loop_integral_family_audit"
if not exist "%ROOT%\vp05_certificate_adaptive_degree.json" (
 echo ERROR: Missing grid-v2 adaptive JSON
 exit /b 2
)
if not exist "%ROOT%\vp05_certificate_adaptive_degree_grid_v3.json" (
 echo ERROR: Missing grid-v3 adaptive JSON
 exit /b 2
)
echo [VP05] Compare grid-v2/v3 coefficient outcomes and (3,3) rank; no Fermat/Kira.
python -m examples.three_loop_sector203_adaptive_grid_comparison
exit /b %ERRORLEVEL%
