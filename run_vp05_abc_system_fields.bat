@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_vp05_abc_system_fields %*
exit /b %errorlevel%
