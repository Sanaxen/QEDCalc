@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_sector203_exact_prefix_smoke %*
exit /b %ERRORLEVEL%
