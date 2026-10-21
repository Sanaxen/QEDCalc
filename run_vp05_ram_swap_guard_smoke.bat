@echo off
setlocal
cd /d "%~dp0"
wsl -- python3 -m examples.three_loop_sector203_ram_swap_guard_smoke %*
exit /b %ERRORLEVEL%
