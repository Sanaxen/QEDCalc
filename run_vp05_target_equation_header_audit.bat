@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_sector203_target_equation_header_audit %*
exit /b %ERRORLEVEL%
