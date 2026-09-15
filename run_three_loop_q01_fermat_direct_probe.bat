@echo off
setlocal
cd /d "%~dp0"

where wsl.exe >nul 2>&1
if errorlevel 1 (
  echo ERROR: wsl.exe was not found.
  pause
  exit /b 2
)

wsl.exe bash -lc "test -x $HOME/fermat/Ferl7/fer64"
if errorlevel 1 (
  echo ERROR: Fermat executable was not found or is not executable at $HOME/fermat/Ferl7/fer64.
  pause
  exit /b 4
)

echo.
echo QEDCalc direct Fermat rational-function probe
echo Expected exact result is 2*(d^2+z^2)/(d^2-z^2), up to algebraic formatting.
echo.

wsl.exe bash -lc "cd $HOME/fermat/Ferl7 && printf '%%s\n' '&(J=d);' '&(J=z);' 'q := (d+z)/(d-z) + (d-z)/(d+z);' 'q;' '&q' | ./fer64"
set "RC=%ERRORLEVEL%"

echo.
if "%RC%"=="0" (
  echo Fermat direct rational-function probe process completed.
) else (
  echo Fermat direct rational-function probe failed with error code %RC%.
)
pause
exit /b %RC%
