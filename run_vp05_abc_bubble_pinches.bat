@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_vp05_abc_bubble_pinches %*
exit /b %errorlevel%
