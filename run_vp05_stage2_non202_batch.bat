@echo off
setlocal EnableExtensions DisableDelayedExpansion
cd /d "%~dp0"
set "MODE=%~1"
set "ID=%~2"
if "%MODE%"=="" goto :usage
if "%ID%"=="" goto :usage
if /I "%MODE%"=="plan" goto :plan
if /I "%MODE%"=="prepare" goto :prepare
if /I "%MODE%"=="audit" goto :audit
if /I "%MODE%"=="run" goto :run
goto :usage
:plan
python -m examples.three_loop_vp05_stage2_non202_batch plan --run-id "%ID%"
exit /b %ERRORLEVEL%
:prepare
python -m examples.three_loop_vp05_stage2_non202_batch prepare --run-id "%ID%"
exit /b %ERRORLEVEL%
:audit
python -m examples.three_loop_vp05_stage2_non202_batch audit --run-id "%ID%"
exit /b %ERRORLEVEL%
:run
if not "%~3"=="EXECUTE_VP05_NO_SECTOR202_BATCH" goto :usage
python -m examples.three_loop_vp05_stage2_non202_batch run --run-id "%ID%" --acknowledge "%~3" --max-total-seconds 43200
exit /b %ERRORLEVEL%
:usage
echo Usage: %~nx0 plan^|prepare^|audit RUN_ID
echo        %~nx0 run RUN_ID EXECUTE_VP05_NO_SECTOR202_BATCH
echo Reuses saved next01 sector230, prepares and executes isolated 126,127,229,231,237.
echo Preserves sector206 and 234 RAM-stopped projects. 23 candidate integrals total.
echo Serial Kira: 90min/sector, 12h total, 18/22 GiB RAM warn/stop, 4/8 GiB swap.
echo Independent jobs may continue after guard stop ONLY when resource preflight passes.
echo Existing files are NEVER cleaned or overwritten; local master success is not global Stage-2 closure.
exit /b 2
