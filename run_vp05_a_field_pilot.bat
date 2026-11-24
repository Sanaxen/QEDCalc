@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_vp05_a_field_pilot %*
exit /b %errorlevel%
