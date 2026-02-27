#!/bin/bash
# SRE-NanoBot WebUI 快速启动脚本

set -e

echo "=================================================="
echo "  SRE-NanoBot WebUI 启动脚本"
echo "=================================================="
echo ""

cd "$(dirname "$0")"

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装"
    exit 1
fi

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装"
    exit 1
fi

echo "✅ 环境检查通过"
echo ""

# 启动后端
echo "🚀 启动后端服务..."
cd backend

if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -q -r requirements.txt

# 后台启动后端
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "✅ 后端服务已启动 (PID: $BACKEND_PID)"
echo ""

# 启动前端
cd ../frontend
echo "🚀 启动前端服务..."

if [ ! -d "node_modules" ]; then
    echo "安装前端依赖（这可能需要几分钟）..."
    npm install
fi

npm start &
FRONTEND_PID=$!
echo "✅ 前端服务已启动 (PID: $FRONTEND_PID)"
echo ""

echo "=================================================="
echo "  WebUI 已启动！"
echo "=================================================="
echo ""
echo "📡 后端 API: http://localhost:8000"
echo "🌐 前端页面：http://localhost:3000"
echo "📖 API 文档：http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

# 等待进程
wait
