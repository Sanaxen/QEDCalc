@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"
if "%~1"=="" goto usage
if "%~2"=="" goto usage
if not exist ".venv\Scripts\python.exe" exit /b 2
".venv\Scripts\python.exe" -m examples.three_loop_sector203_single_target %~1 %~2
if errorlevel 1 exit /b !ERRORLEVEL!
set "PROJECT=%CD%\output\kira_vp05_full_preferred_masters_r8s3d0_r7s6d2_sec203_single_t%~1_%~2"
copy /Y "scripts\sector203_bounded_diagnostic.sh" "%PROJECT%\sector203_bounded_diagnostic.sh" >nul
if errorlevel 1 exit /b 3
wsl.exe --cd "%PROJECT%" bash -c "sed -i 's/\r$//' sector203_bounded_diagnostic.sh && bash -n sector203_bounded_diagnostic.sh && bash ./sector203_bounded_diagnostic.sh"
set "RESULT=!ERRORLEVEL!"
echo WSL_PROCESS_EXIT_CODE=!RESULT!
if exist "%PROJECT%\diagnostic_exit_v2.txt" (
 set /p KIRA_RESULT=<"%PROJECT%\diagnostic_exit_v2.txt"
 echo KIRA_TIMEOUT_EXIT_CODE_FILE=!KIRA_RESULT!
)
exit /b !RESULT!
:usage
echo Usage: %~nx0 TARGET_INDEX[1-4] SEED[r5s6d0^|r6s6d1^|r7s6d2]
exit /b 2
