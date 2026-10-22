@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_vp05_sector202_observed_codec
exit /b %ERRORLEVEL%
