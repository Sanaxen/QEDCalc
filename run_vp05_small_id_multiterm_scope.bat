@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_sector203_small_id_multiterm_scope %*
exit /b %ERRORLEVEL%
