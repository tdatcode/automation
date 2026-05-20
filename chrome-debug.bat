@echo off
echo ========================================
echo   MO CHROME VOI REMOTE DEBUGGING
echo ========================================
echo.
echo Dang mo Chrome...
echo Port: 9222
echo User Data: C:\chrome-debug
echo.

"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\chrome-debug"

echo.
echo Chrome da dong.
pause
