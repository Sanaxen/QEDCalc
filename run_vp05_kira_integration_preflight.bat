@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_sector203_kira_integration_preflight %*
exit /b %ERRORLEVEL%
