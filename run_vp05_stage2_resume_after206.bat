@echo off
setlocal EnableExtensions DisableDelayedExpansion
cd /d "%~dp0"
if /I "%~1"=="plan" goto :plan
if /I "%~1"=="audit" goto :audit
if /I "%~1"=="run" goto :run
goto :usage
:plan
python -m examples.three_loop_vp05_stage2_resume_after206 plan
exit /b %ERRORLEVEL%
:audit
python -m examples.three_loop_vp05_stage2_resume_after206 audit
exit /b %ERRORLEVEL%
:run
if not "%~2"=="PRESERVE_SECTOR206_RUN_REMAINING_FOUR" goto :usage
python -m examples.three_loop_vp05_stage2_resume_after206 run --acknowledge "%~2" --max-total-seconds 43200
exit /b %ERRORLEVEL%
:usage
echo Usage: %~nx0 plan^|audit
echo        %~nx0 run PRESERVE_SECTOR206_RUN_REMAINING_FOUR
echo Reuses next01. Keeps sector205 success and preserves failed sector206 untouched.
echo Runs only prepared 79,109,234,230 sequentially, stop on first guard/error.
echo Maximum 90 min per sector, 12 hours total. WSL RAM warn/stop 18/22 GiB, swap warn/stop 4/8 GiB.
exit /b 2
