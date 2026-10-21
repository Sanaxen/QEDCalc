@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_sector203_528_scalar_probe %*
exit /b %ERRORLEVEL%
