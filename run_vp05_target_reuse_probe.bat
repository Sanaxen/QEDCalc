@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_vp05_target_reuse_probe %*
exit /b %errorlevel%
