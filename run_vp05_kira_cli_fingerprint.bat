@echo off
setlocal
cd /d "%~dp0"
wsl -- python3 -m examples.three_loop_sector203_kira_cli_fingerprint %*
exit /b %ERRORLEVEL%
