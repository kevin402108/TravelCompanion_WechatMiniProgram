@echo off
cd C:\Users\30773\WeChatProjects\travel_companion_system
python.exe -m uvicorn backEnd.app.main:app --reload --host 0.0.0.0 --port 8001
