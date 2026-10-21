@echo off
setlocal
cd /d "%~dp0"
wsl -- python3 -m examples.three_loop_sector203_fermat_inventory %*
exit /b %ERRORLEVEL%
