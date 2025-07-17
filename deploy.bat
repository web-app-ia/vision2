@echo off
echo =================================
echo  Computer Vision App Deployment
echo =================================
echo.

echo Step 1: Building Windows executable...
call npm run build-win
if %errorlevel% neq 0 (
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo Step 2: Committing changes...
git add -A
git commit -m "Release version %1"

echo.
echo Step 3: Pushing to GitHub...
git push origin main

echo.
echo Step 4: Creating Git tag...
git tag -a v%1 -m "Version %1"
git push origin v%1

echo.
echo =================================
echo  Deployment completed successfully!
echo =================================
echo.
echo Your executable is located at: dist\Computer Vision App %1.exe
echo.
echo Next steps:
echo 1. Go to https://github.com/web-app-ia/vision2/releases
echo 2. Create a new release with tag v%1
echo 3. Upload the executable file
echo 4. The app will auto-update from this release
echo.
pause
