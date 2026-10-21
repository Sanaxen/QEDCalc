@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_sector203_target_weight_codec_audit %*
exit /b %ERRORLEVEL%
