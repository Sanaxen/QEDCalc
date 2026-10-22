@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_sector203_stage2_history
exit /b %ERRORLEVEL%
