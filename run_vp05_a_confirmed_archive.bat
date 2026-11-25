@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_vp05_a_confirmed_archive
exit /b %errorlevel%
