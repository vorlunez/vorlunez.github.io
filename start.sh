#!/bin/bash

cd "$(dirname "$0")"

echo "📦 安装依赖..."
pip3 install -r requirements.txt -q

echo "🚀 启动博客..."
echo "访问地址: http://localhost:5000"
echo ""

python3 app.py
