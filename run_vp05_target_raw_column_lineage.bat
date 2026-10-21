@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_sector203_target_raw_column_lineage %*
exit /b %ERRORLEVEL%
