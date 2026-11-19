@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_vp05_stage2_sector202_stop_forensics %*
exit /b %ERRORLEVEL%
