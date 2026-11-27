@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_vp05_residual_moments %*
exit /b %errorlevel%
