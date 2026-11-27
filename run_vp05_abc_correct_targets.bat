@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_vp05_abc_correct_targets %*
exit /b %errorlevel%
