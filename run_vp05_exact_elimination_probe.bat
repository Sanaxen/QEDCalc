@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_sector203_exact_elimination_probe %*
exit /b %ERRORLEVEL%
