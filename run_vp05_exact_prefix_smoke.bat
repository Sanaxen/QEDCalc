@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_sector203_exact_prefix_smoke --rows 6 %*
exit /b %ERRORLEVEL%
