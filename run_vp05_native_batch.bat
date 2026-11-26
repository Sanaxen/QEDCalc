@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_vp05_native_batch %*
exit /b %errorlevel%
