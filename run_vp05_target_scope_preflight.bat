@echo off
setlocal
cd /d "%~dp0"
set "EQUATIONS=output\three_loop_integral_family_audit\vp05_target_symbolic_compressed.equations.json"
if not exist "%EQUATIONS%" (
  echo ERROR: Missing VP05 compressed symbolic equations: %EQUATIONS%
  exit /b 2
)
echo [VP05] Target-only dependency scope preflight; no Fermat/Kira.
python -m examples.three_loop_sector203_target_scope_preflight --equations "%EQUATIONS%" --output output\three_loop_integral_family_audit\vp05_target_scope_preflight.json
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" echo [VP05] Target scope preflight failed: %RC%
exit /b %RC%
