@echo off
setlocal
cd /d "%~dp0"
set "EQUATIONS=output\three_loop_integral_family_audit\vp05_target_symbolic_compressed.equations.json"
if not exist "%EQUATIONS%" (
  echo ERROR: Missing compressed VP05 equations: %EQUATIONS%
  echo Run the previously verified symbolic compression step first.
  exit /b 2
)
echo [VP05] 166-row Fermat resource preflight ONLY; no Fermat/Kira execution.
python -m examples.three_loop_sector203_fermat_gaussian_pilot ^
  --equations "%EQUATIONS%" ^
  --rows 166 ^
  --max-rows 320 ^
  --auto-points ^
  --preflight-only ^
  --prune-eliminated-pivots ^
  --sparse-array-rows ^
  --packed-sparse-maps ^
  --reuse-packed-maps ^
  --loop-control-rows ^
  --prune-dead-rows ^
  --verify-last-rows 1 ^
  --analyze-row-lifetimes
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" echo [VP05] PRE-FLIGHT FAILED: exit code %RC%
exit /b %RC%
