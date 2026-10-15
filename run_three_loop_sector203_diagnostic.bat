@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"
set "BASE=%CD%\output\kira_vp05_full_preferred_masters_r8s3d0_r7s6d2_sec203"
set "MODE=%~1"
if "%MODE%"=="" set "MODE=without_preferred"
if /I not "%MODE%"=="with_preferred" if /I not "%MODE%"=="without_preferred" (
 echo Usage: %~nx0 [with_preferred^|without_preferred]
 exit /b 2
)
set "PROJECT=%BASE%_diagnostic_%MODE%"
if not exist "%PROJECT%\jobs.yaml" (
 echo ERROR: diagnostic project absent: %PROJECT%
 echo Run the preparation step only if needed.
 exit /b 3
)
if exist "%PROJECT%\diagnostic_capture.log" (
 echo ERROR: diagnostic_capture.log already exists, refusing to overwrite.
 exit /b 4
)
echo QEDCalc sector 203 bounded diagnostic
echo mode: %MODE%
echo existing project: %PROJECT%
echo 90-second ceiling; no cleanup of existing result directories
wsl.exe --cd "%PROJECT%" bash -lc "export FERMATPATH=$HOME/fermat/Ferl7/fer64; timeout --signal=TERM --kill-after=5s 90s kira --integral_ordering=5 jobs.yaml > diagnostic_capture.log 2>&1; code=$?; printf 'KIRA_TIMEOUT_EXIT_CODE=%%s\n' \"$code\" >> diagnostic_capture.log; tail -n 35 diagnostic_capture.log; exit $code"
set "RESULT=!ERRORLEVEL!"
echo WSL_PROCESS_EXIT_CODE=!RESULT!
wsl.exe --status
echo Note: 124=timeout, 0=normal, 1=error; 137/other may be termination.
exit /b !RESULT!
