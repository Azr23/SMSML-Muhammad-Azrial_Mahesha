@echo off
echo ===================================================
echo Starting Model Serving API & Prometheus Exporter...
echo ===================================================

echo 1. Launching FastAPI Model Serving (Port 8000)...
start "FastAPI Model Serving" cmd /k python 7.inference.py

echo Waiting for FastAPI to load the model...
timeout /t 3 >nul

echo 2. Launching Prometheus Exporter (Port 8001)...
start "Prometheus Exporter" cmd /k python 3.prometheus_exporter.py

echo ===================================================
echo Both servers are running in separate windows!
echo - Check the FastAPI terminal for the serving log screenshot.
echo - Do not close the terminals while taking screenshots.
echo ===================================================
pause
