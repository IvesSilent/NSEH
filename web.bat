@echo off
echo Starting the web-application of NSEH Framework...
start /B python app.py
timeout /T 5
start http://127.0.0.1:5000/