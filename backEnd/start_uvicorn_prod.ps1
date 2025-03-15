# 进入虚拟环境目录
Push-Location -Path ".\travel_companion_system\venv\Scripts"

# 激活虚拟环境
.\Activate.ps1

# 回到项目目录
Pop-Location

# 启动uvicorn
python -m uvicorn travel_companion_system.app.main:app --host 0.0.0.0 --port 8001