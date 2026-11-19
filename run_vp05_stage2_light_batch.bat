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
python -m examples.three_loop_vp05_stage2_light_batch plan --run-id "%~2"
exit /b %ERRORLEVEL%
:prepare
python -m examples.three_loop_vp05_stage2_light_batch prepare --run-id "%~2"
exit /b %ERRORLEVEL%
:audit
python -m examples.three_loop_vp05_stage2_light_batch audit --run-id "%~2"
exit /b %ERRORLEVEL%
:run
if not "%~3"=="EXECUTE_VP05_ISOLATED_LIGHT_BATCH" goto :usage
python -m examples.three_loop_vp05_stage2_light_batch execute --run-id "%~2" --acknowledge "%~3" --max-total-seconds 6000
exit /b %ERRORLEVEL%
:usage
echo Usage: %~nx0 plan^|prepare^|audit RUN_ID
echo        %~nx0 run RUN_ID EXECUTE_VP05_ISOLATED_LIGHT_BATCH
echo Isolated sequential sectors 78,101,116. Maximum 1800 sec each, 8 GiB swap stop.
echo Completed sectors are skipped on safe rerun; interrupted projects are never overwritten.
exit /b 2
