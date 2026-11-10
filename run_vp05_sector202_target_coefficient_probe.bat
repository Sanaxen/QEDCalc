@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_vp05_sector202_target_coefficient_probe %*
exit /b %ERRORLEVEL%
