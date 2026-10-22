@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_vp05_global_saved_system_locator
exit /b %ERRORLEVEL%
