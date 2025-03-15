Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# 进入虚拟环境目录
Push-Location -Path ".\travel_companion_system\venv\Scripts"

# 激活虚拟环境
.\Activate.ps1

# 回到项目目录
Pop-Location

# 启动uvicorn,开启热重载
.\travel_companion_system\venv\Scripts\python.exe -m uvicorn travel_companion_system.app.main:app --reload --host 127.0.0.1 --port 8001