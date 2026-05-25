@echo off
REM ===================================================================
REM  DrSeba Healthcare Platform - Public Share via Serveo
REM ===================================================================
REM  This creates a temporary public URL to share with others
REM  No setup required - works with your local Django server!
REM ===================================================================

cls
echo.
echo ===================================================================
echo  📱 DrSeba Public Share Setup
echo ===================================================================
echo.
echo This tool will create a temporary public URL for your application.
echo.
echo Make sure your Django server is running on http://127.0.0.1:8000/
echo.
echo ===================================================================
echo.

echo 🚀 Creating public URL via Serveo...
echo.
echo Running: ssh -R 80:localhost:8000 serveo.net
echo.
echo Wait for the output - it will show your public URL!
echo.
pause

ssh -R 80:localhost:8000 serveo.net

pause
