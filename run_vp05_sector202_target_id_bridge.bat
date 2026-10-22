@echo off
setlocal
cd /d "%~dp0"
set "CODEC=%~1"
if "%CODEC%"=="" set "CODEC=%~dp0output\tools\pyred_weight.py"
if not exist "%CODEC%" (
  echo ERROR: Kira weight codec not found: %CODEC%
  exit /b 2
)
python -m examples.three_loop_vp05_sector202_target_id_bridge --codec-file "%CODEC%"
exit /b %ERRORLEVEL%
