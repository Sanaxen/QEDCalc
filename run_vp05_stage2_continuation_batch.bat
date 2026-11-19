@echo off
setlocal EnableExtensions DisableDelayedExpansion
cd /d "%~dp0"
if "%~1"=="" goto :usage
if "%~2"=="" goto :usage
if /I "%~1"=="plan" goto :plan
if /I "%~1"=="prepare" goto :prepare
if /I "%~1"=="audit" goto :audit
if /I "%~1"=="run" goto :run
goto :usage
:plan
python -m examples.three_loop_vp05_stage2_continuation_batch plan --run-id "%~2"
exit /b %ERRORLEVEL%
:prepare
python -m examples.three_loop_vp05_stage2_continuation_batch prepare --run-id "%~2"
exit /b %ERRORLEVEL%
:audit
python -m examples.three_loop_vp05_stage2_continuation_batch audit --run-id "%~2"
exit /b %ERRORLEVEL%
:run
if not "%~3"=="EXECUTE_VP05_ISOLATED_CONTINUATION_BATCH" goto :usage
python -m examples.three_loop_vp05_stage2_continuation_batch execute --run-id "%~2" --acknowledge "%~3" --max-total-seconds 43200
exit /b %ERRORLEVEL%
:usage
echo Usage: %~nx0 plan^|prepare^|audit RUN_ID
echo        %~nx0 run RUN_ID EXECUTE_VP05_ISOLATED_CONTINUATION_BATCH
echo Sequential sectors 205,206,79,109,234,230; 11 master candidates.
echo 90 min per sector; 12 hours total. RAM warn/stop 18/22 GiB, swap warn/stop 4/8 GiB.
echo Preserves original jobs and previously completed sectors; no implicit rerun of failed job.
exit /b 2
