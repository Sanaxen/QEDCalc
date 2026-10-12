@echo off
setlocal EnableExtensions
cd /d "%~dp0"

if "%~1"=="" goto :usage
if "%~2"=="" goto :usage
set "FAMILY=%~1"
set "FILTER=%~2"
set "TABLE=%~3"
set "ROWS=%~4"
if "%TABLE%"=="" set "TABLE=EQUATION"
if "%ROWS%"=="" set "ROWS=5"

if not exist ".venv\Scripts\python.exe" (
  echo ERROR: .venv\Scripts\python.exe not found.
  exit /b 1
)

".venv\Scripts\python.exe" -m examples.three_loop_kira_db_inspect ^
  --family "%FAMILY%" ^
  --project-filter "%FILTER%" ^
  --table "%TABLE%" ^
  --sample-rows "%ROWS%"

exit /b %ERRORLEVEL%

:usage
echo Usage: %~nx0 FAMILY PROJECT_FILTER [TABLE] [SAMPLE_ROWS]
echo Example: %~nx0 VP05_full candidate_closure_r8s3d0_r8s5d2 EQUATION 5
exit /b 2
