@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_vp05_saved_sector202_system_content
exit /b %ERRORLEVEL%
