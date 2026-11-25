@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_vp05_remaining_safe_batch %*
exit /b %errorlevel%
