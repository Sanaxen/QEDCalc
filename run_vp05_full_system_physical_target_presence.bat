@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_sector203_full_system_physical_target_presence %*
exit /b %ERRORLEVEL%
