@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_vp05_sec77_exact_retry %*
exit /b %errorlevel%
