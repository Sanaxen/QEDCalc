@echo off
setlocal
cd /d "%~dp0"
echo [VP05] Diagnose target IDs from original witness metadata, without external Kira weight decoding.
python -m examples.three_loop_sector203_target_key_namespace_diagnostic
exit /b %ERRORLEVEL%
