@echo off
setlocal EnableExtensions DisableDelayedExpansion
cd /d "%~dp0"
set "MODE=%~1"
set "RUN_ID=%~2"
if "%MODE%"=="" goto :usage
if "%RUN_ID%"=="" goto :usage
if /I "%MODE%"=="plan" goto :plan
if /I "%MODE%"=="prepare" goto :prepare
if /I "%MODE%"=="check" goto :check
if /I "%MODE%"=="audit" goto :audit
if /I "%MODE%"=="run" goto :run
goto :usage

:plan
python -m examples.three_loop_vp05_stage2_small_pilot plan --run-id "%RUN_ID%"
exit /b %ERRORLEVEL%

:prepare
python -m examples.three_loop_vp05_stage2_small_pilot prepare --run-id "%RUN_ID%"
exit /b %ERRORLEVEL%

:check
python -m examples.three_loop_vp05_stage2_small_pilot check --run-id "%RUN_ID%"
exit /b %ERRORLEVEL%

:audit
python -m examples.three_loop_vp05_stage2_small_pilot audit --run-id "%RUN_ID%"
exit /b %ERRORLEVEL%

:run
if not "%~3"=="EXECUTE_ISOLATED_R8S5D3_SECTOR73" (
  echo ERROR: explicit execution acknowledgement required.
  goto :usage
)
python -m examples.three_loop_vp05_stage2_small_pilot check --run-id "%RUN_ID%"
if errorlevel 1 exit /b %ERRORLEVEL%
set "PROJECT=%CD%\output\vp05_stage2_pilot_r8s5d3_sec73_%RUN_ID%"
echo Guarded single-sector pilot: %PROJECT%
echo 30 minute ceiling, swap warning 4 GiB, stop 8 GiB; isolated directory only.
wsl.exe --cd "%PROJECT%" python3 sector203_monitored_kira.py --max-seconds 1800 --warn-gib 4 --stop-gib 8 --interval 5
set "RUN_ERROR=%ERRORLEVEL%"
python -m examples.three_loop_vp05_stage2_small_pilot audit --run-id "%RUN_ID%"
exit /b %RUN_ERROR%

:usage
echo Usage: %~nx0 plan^|prepare^|check^|audit RUN_ID
echo   or: %~nx0 run RUN_ID EXECUTE_ISOLATED_R8S5D3_SECTOR73
echo Plan is strictly read-only; prepare creates an isolated new project only.
echo Run launches guarded Kira only with the exact execution acknowledgement.
exit /b 2
