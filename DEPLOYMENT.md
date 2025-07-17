# Computer Vision App - Deployment Guide

## Overview
This application is set up with automatic updates from GitHub releases. The app will check for updates automatically and notify users when a new version is available.

## Repository
- **GitHub Repository**: https://github.com/web-app-ia/vision2
- **Auto-updater**: Configured to check for releases on GitHub

## Building the Application

### Prerequisites
- Node.js installed
- npm dependencies installed (`npm install`)

### Building Executable
```bash
npm run build-win
```

This will create a portable Windows executable in the `dist` folder.

## Deployment Process

### Method 1: Using the Deploy Script
1. Update the version in `package.json`
2. Run the deploy script:
   ```bash
   deploy.bat 1.0.2
   ```
3. Follow the instructions to create a GitHub release

### Method 2: Manual Process
1. Update version in `package.json`
2. Build the executable:
   ```bash
   npm run build-win
   ```
3. Commit and push changes:
   ```bash
   git add .
   git commit -m "Release version 1.0.2"
   git push origin main
   ```
4. Create a git tag:
   ```bash
   git tag -a v1.0.2 -m "Version 1.0.2"
   git push origin v1.0.2
   ```
5. Create a GitHub release with the tag and upload the executable

## Auto-Update Process

The application automatically:
1. Checks for updates on startup
2. Notifies users when updates are available
3. Downloads and installs updates automatically
4. Users can also manually check for updates via the "Help" menu

## File Structure
- `src/main.js` - Main Electron process with auto-updater configuration
- `package.json` - Version and repository configuration
- `dist/` - Built executables
- `deploy.bat` - Deployment automation script

## Configuration
The auto-updater is configured to:
- Check GitHub releases for the `web-app-ia/vision2` repository
- Download and install updates automatically
- Show progress to users during the update process

## Important Notes
- The application must be signed for auto-updates to work on some systems
- GitHub releases must include the executable file
- Version numbers should follow semantic versioning (e.g., 1.0.0, 1.0.1, 1.1.0)
