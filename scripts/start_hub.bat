@echo off
setlocal enabledelayedexpansion

title EduMesh AI Classroom Hub

echo ===================================================
echo               EduMesh AI Classroom Hub              
echo ===================================================

:: Check Python availability
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python 3 is not installed or not in PATH!
    echo Please install Python 3.9+ to run EduMesh AI Hub.
    pause
    exit /b 1
)

:: Ensure directories exist
if not exist "data" mkdir data
if not exist "config" mkdir config

:: Check configuration file
if not exist "config\infrastructure_config.json" (
    echo [INFO] Initializing default infrastructure_config.json...
    (
      echo {
      echo   "hub": { "host": "0.0.0.0", "port": 8000 },
      echo   "cache": { "similarity_threshold": 0.85, "require_approval": true },
      echo   "sync": { "enabled": true, "auto_install": false }
      echo }
    ) > config\infrastructure_config.json
)

echo [INFO] Starting EduMesh AI Classroom Hub backend service...
echo [INFO] Binding to host 0.0.0.0 on port 8000...
echo.

python -m backend.main

pause
