@echo off
setlocal
cd /d "%~dp0"
wsl -- python3 -m examples.three_loop_sector203_existing_equation_reuse_audit %*
exit /b %ERRORLEVEL%
