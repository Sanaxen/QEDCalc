@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_vp05_independent_ibp %*
exit /b %errorlevel%
