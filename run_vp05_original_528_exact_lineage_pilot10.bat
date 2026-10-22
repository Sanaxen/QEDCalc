@echo off
setlocal
cd /d "%~dp0"
set "REPORT=output\three_loop_integral_family_audit\vp05_original_528_exact_lineage_pilot10.json"
if exist "%REPORT%" (
  echo VP05_LINEAGE_PILOT_BLOCKED: report already exists: %REPORT%
  exit /b 2
)
wsl -- python3 -m examples.three_loop_sector203_original_528_exact_lineage_audit --max-groups 10 --output output/three_loop_integral_family_audit/vp05_original_528_exact_lineage_pilot10.json
exit /b %ERRORLEVEL%
