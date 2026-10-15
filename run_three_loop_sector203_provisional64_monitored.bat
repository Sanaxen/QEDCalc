@echo off
setlocal EnableExtensions
cd /d "%~dp0"
if "%~1"=="" goto :usage
set "PROJECT=%~f1"
if not exist "%PROJECT%\provisional64_sector203_preflight.json" (
 echo ERROR: not a prepared provisional64 sector203 project.
 exit /b 2
)
if not exist "%PROJECT%\jobs.yaml" exit /b 2
if not exist "%PROJECT%\sector203_monitored_kira.py" exit /b 2
if exist "%PROJECT%\monitored_exit.json" (
 echo ERROR: refusing to rerun or overwrite finished monitored project.
 exit /b 2
)
if exist "%PROJECT%\monitored_kira.log" (
 echo ERROR: refusing to overwrite prior log.
 exit /b 2
)
echo Starting monitored Kira in isolated project:
echo %PROJECT%
echo Wall-time cap: disabled; swap warning: 150 GiB; stop: 170 GiB.
echo NOTE: time/swap stops terminate the Kira process; they do not establish master stability.
wsl.exe --cd "%PROJECT%" python3 sector203_monitored_kira.py --max-seconds 0 --warn-gib 150 --stop-gib 170
set "RC=%ERRORLEVEL%"
echo MONITOR_WSL_EXIT_CODE=%RC%
if exist "%PROJECT%\monitored_exit.json" type "%PROJECT%\monitored_exit.json"
exit /b %RC%
:usage
echo Usage: %~nx0 ^<full_or_relative_prepared_project_path^>
echo Explicit execution only. Prepare with python -m examples.three_loop_sector203_provisional64_stage_prepare r6s6d1
exit /b 2
