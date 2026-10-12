@echo off
setlocal EnableExtensions
cd /d "%~dp0"

if "%~1"=="" goto :usage
set "FILTER=%~1"
set "TABLE=%~2"
set "ROWS=%~3"
if "%TABLE%"=="" set "TABLE=EQUATION"
if "%ROWS%"=="" set "ROWS=5"

if not exist ".venv\Scripts\python.exe" (
  echo ERROR: .venv\Scripts\python.exe not found.
  exit /b 1
)

".venv\Scripts\python.exe" -m examples.three_loop_kira_db_inspect ^
  --project-filter "%FILTER%" ^
  --table "%TABLE%" ^
  --sample-rows "%ROWS%"

exit /b %ERRORLEVEL%

:usage
echo Usage: %~nx0 PROJECT_FILTER [TABLE] [SAMPLE_ROWS]
echo Example: %~nx0 candidate_closure_r8s3d0_r8s5d2 EQUATION 5
exit /b 2
