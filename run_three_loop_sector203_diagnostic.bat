@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
 echo ERROR: .venv\Scripts\python.exe missing
 exit /b 1
)
".venv\Scripts\python.exe" -m examples.three_loop_sector203_diagnostic
if errorlevel 1 exit /b %ERRORLEVEL%
set "BASE=%CD%\output\kira_vp05_full_preferred_masters_r8s3d0_r7s6d2_sec203"
for %%M in (with_preferred without_preferred) do (
 echo.
 echo === DIAGNOSTIC %%M; max 90 seconds ===
 wsl.exe --cd "%BASE%_diagnostic_%%M" bash -lc "set -o pipefail; export FERMATPATH=$HOME/fermat/Ferl7/fer64; timeout --signal=TERM --kill-after=5s 90s kira --integral_ordering=5 jobs.yaml 2>&1 | tee diagnostic.log"
 echo Exit code for %%M: !ERRORLEVEL!
)
echo.
echo Diagnostic logs are in *_diagnostic_with_preferred and *_diagnostic_without_preferred.
echo Exit code 124 means time limit, not proof of failure; inspect both logs.
exit /b 0
