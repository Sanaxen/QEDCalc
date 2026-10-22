@echo off
setlocal
cd /d "%~dp0"
set "REPORT=output\three_loop_integral_family_audit\vp05_original_528_exact_lineage_full166.json"
if exist "%REPORT%" (
  echo VP05_LINEAGE_FULL166_BLOCKED: report already exists: %REPORT%
  exit /b 2
)
python -m examples.three_loop_sector203_original_528_exact_lineage_audit --max-groups 166 --max-source-terms 20000 --output output/three_loop_integral_family_audit/vp05_original_528_exact_lineage_full166.json
exit /b %ERRORLEVEL%
