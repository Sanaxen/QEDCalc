@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_vp05_203_exact_lift %*
exit /b %errorlevel%
