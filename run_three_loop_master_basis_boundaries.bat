@echo off
setlocal EnableExtensions
cd /d "%~dp0"

if "%~1"=="" goto :usage
set "FAMILY=%~1"
set "BASELINE=%~2"
set "SOLVER=%~3"
if "%BASELINE%"=="" set "BASELINE=r8s3d0"
if "%SOLVER%"=="" set "SOLVER=firefly"

if /I not "%SOLVER%"=="ordinary" if /I not "%SOLVER%"=="firefly" (
  echo ERROR: solver must be ordinary or firefly.
  exit /b 2
)

for /f "tokens=1,2,3 delims=rsd" %%A in ("%BASELINE%") do (
  set /a R=%%A
  set /a S=%%B
  set /a D=%%C
)
if not defined R goto :usage
set /a RP1=R+1
set /a SP1=S+1
set /a DP1=D+1
set "SEED_R=r%RP1%s%S%d%D%"
set "SEED_S=r%R%s%SP1%d%D%"
set "SEED_D=r%R%s%S%d%DP1%"

echo QEDCalc generic master-basis one-axis boundaries
echo family: %FAMILY%
echo baseline: %BASELINE%
echo solver: %SOLVER%
echo boundaries: %SEED_R%, %SEED_S%, %SEED_D%

call "%~dp0run_three_loop_master_basis_seed.bat" "%FAMILY%" "%SEED_R%" "%SOLVER%"
if errorlevel 1 exit /b %ERRORLEVEL%

call "%~dp0run_three_loop_master_basis_seed.bat" "%FAMILY%" "%SEED_S%" "%SOLVER%"
if errorlevel 1 exit /b %ERRORLEVEL%

call "%~dp0run_three_loop_master_basis_seed.bat" "%FAMILY%" "%SEED_D%" "%SOLVER%"
if errorlevel 1 exit /b %ERRORLEVEL%

if not exist ".venv\Scripts\python.exe" (
  echo ERROR: .venv\Scripts\python.exe not found.
  exit /b 1
)

".venv\Scripts\python.exe" -m examples.three_loop_master_basis_boundary_audit --family "%FAMILY%" --baseline-seed "%BASELINE%" --solver "%SOLVER%"
set "ERR=%ERRORLEVEL%"
if not "%ERR%"=="0" exit /b %ERR%

endlocal
exit /b 0

:usage
echo Usage: %~nx0 FAMILY [BASELINE_SEED] [ordinary^|firefly]
echo Example: %~nx0 Q05_full r8s3d0 firefly
exit /b 2
