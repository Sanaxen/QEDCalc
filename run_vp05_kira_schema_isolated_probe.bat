@echo off
setlocal
cd /d "%~dp0"
wsl -- python3 -m examples.three_loop_sector203_kira_schema_isolated_probe %*
exit /b %ERRORLEVEL%
