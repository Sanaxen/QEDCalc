@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_sector203_528_group_rowspace_probe %*
exit /b %ERRORLEVEL%
