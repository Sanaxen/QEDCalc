@echo off
setlocal
cd /d "%~dp0"
if "%~1"=="" (
 echo Usage: %~nx0 ^<path-to-external-pyred_weight.py^>
 exit /b 2
)
python -m examples.three_loop_vp05_sector202_target_id_bridge --codec-file "%~1"
exit /b %ERRORLEVEL%
