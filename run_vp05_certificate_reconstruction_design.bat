@echo off
setlocal
cd /d "%~dp0"
set "SAMPLES=output\three_loop_integral_family_audit\vp05_compressed_certificate_samples.json"
if not exist "%SAMPLES%" (
 echo ERROR: Missing compressed certificate samples: %SAMPLES%
 exit /b 2
)
echo [VP05] Design same-prime rational reconstruction grids ONLY; no Fermat/Kira.
python -m examples.three_loop_sector203_certificate_reconstruction_design --samples "%SAMPLES%"
exit /b %ERRORLEVEL%
