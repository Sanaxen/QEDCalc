@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_sector203_small_weight_role_audit %*
exit /b %ERRORLEVEL%
