@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"
if "%~1"=="" goto :usage
if "%~2"=="" goto :usage
if not exist ".venv\Scripts\python.exe" exit /b 2
for /f %%I in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmssfff"') do set "RUN_ID=%%I"
if not defined RUN_ID exit /b 3
".venv\Scripts\python.exe" -m examples.three_loop_sector203_monitored_prepare %~1 %~2 --run-id !RUN_ID!
if errorlevel 1 exit /b !ERRORLEVEL!
set "PROJECT=%CD%\output\kira_vp05_full_preferred_masters_r8s3d0_r7s6d2_sec203_monitored_t%~1_%~2_!RUN_ID!"
echo Monitored Kira project: !PROJECT!
echo Max 1800 sec, warn swap 210 GiB, stop swap 220 GiB.
wsl.exe --cd "!PROJECT!" python3 sector203_monitored_kira.py --max-seconds 1800 --warn-gib 210 --stop-gib 220
set "RESULT=!ERRORLEVEL!"
echo MONITOR_WSL_EXIT_CODE=!RESULT!
if exist "!PROJECT!\monitored_exit.json" type "!PROJECT!\monitored_exit.json"
exit /b !RESULT!
:usage
echo Usage: %~nx0 TARGET_INDEX[1-4] SEED[r5s6d0^|r6s6d1^|r7s6d2]
exit /b 2
