@echo off
setlocal EnableExtensions
cd /d "%~dp0"

if "%~1"=="" goto :usage
set "FAMILY=%~1"
set "CONTAINS=%~2"

if not exist ".venv\Scripts\python.exe" (
  echo ERROR: .venv\Scripts\python.exe not found.
  exit /b 1
)

if "%CONTAINS%"=="" (
  ".venv\Scripts\python.exe" -m examples.three_loop_kira_reduction_artifact_audit ^
    --family "%FAMILY%"
) else (
  ".venv\Scripts\python.exe" -m examples.three_loop_kira_reduction_artifact_audit ^
    --family "%FAMILY%" ^
    --contains "%CONTAINS%"
)

exit /b %ERRORLEVEL%

:usage
echo Usage: %~nx0 FAMILY [NAME_FILTER]
echo Example: %~nx0 VP05_full r8s5d2
exit /b 2
