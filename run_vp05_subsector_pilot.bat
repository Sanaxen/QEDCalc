@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_vp05_subsector_pilot %*
exit /b %errorlevel%
