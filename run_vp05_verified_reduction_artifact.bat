@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_sector203_verified_reduction_artifact
exit /b %ERRORLEVEL%
