@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"
set "MODE=%~1"
if "%MODE%"=="" set "MODE=without_preferred"
if /I not "%MODE%"=="with_preferred" if /I not "%MODE%"=="without_preferred" (
 echo Usage: %~nx0 [with_preferred^|without_preferred]
 exit /b 2
)
set "PROJECT=%CD%\output\kira_vp05_full_preferred_masters_r8s3d0_r7s6d2_sec203_diagnostic_%MODE%"
if not exist "%PROJECT%\jobs.yaml" (
 echo ERROR: diagnostic project absent: %PROJECT%
 exit /b 3
)
if exist "%PROJECT%\diagnostic_exit_v2.txt" (
 echo ERROR: diagnostic_exit_v2.txt exists; refusing another run.
 exit /b 4
)
copy /Y "scripts\sector203_bounded_diagnostic.sh" "%PROJECT%\sector203_bounded_diagnostic.sh" >nul
if errorlevel 1 exit /b 5
echo QEDCalc isolated diagnostic: %MODE%
wsl.exe --cd "%PROJECT%" bash -c "sed -i 's/\r$//' sector203_bounded_diagnostic.sh && bash -n sector203_bounded_diagnostic.sh && bash ./sector203_bounded_diagnostic.sh"
set "WSL_RESULT=!ERRORLEVEL!"
echo WSL_PROCESS_EXIT_CODE=!WSL_RESULT!
if exist "%PROJECT%\diagnostic_exit_v2.txt" (
 set /p KIRA_RESULT=<"%PROJECT%\diagnostic_exit_v2.txt"
 echo KIRA_TIMEOUT_EXIT_CODE_FILE=!KIRA_RESULT!
) else (
 echo WARNING: Kira exit code file missing, possibly WSL failure.
)
exit /b !WSL_RESULT!
