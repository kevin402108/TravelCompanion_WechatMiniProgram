#!/bin/bash

script_name=$(basename "$0")

chmod +x "$script_name"

# 激活虚拟环境
source./venv/bin/activate

# 启动uvicorn，开启热重载
uvicorn travel_campanion_system.app.main:app --reload --host 0.0.0.0 --port 8001 &