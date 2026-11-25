@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_vp05_safe_stop_forensics
exit /b %errorlevel%
