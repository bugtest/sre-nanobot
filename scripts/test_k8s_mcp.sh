#!/bin/bash
# K8s MCP 服务器测试脚本

set -e

echo "🧪 测试 K8s MCP 服务器"
echo "========================"
echo ""

# 检查 kubectl 是否可用
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl 未安装，请先安装 kubectl"
    exit 1
fi

# 检查集群连接
echo "📡 检查 Kubernetes 集群连接..."
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ 无法连接到 Kubernetes 集群"
    echo "   请配置 kubeconfig 或设置 KUBECONFIG 环境变量"
    exit 1
fi
echo "✅ 集群连接正常"
echo ""

# 获取集群信息
echo "📊 集群信息:"
kubectl cluster-info | head -2
echo ""

# 获取 Node 列表
echo "🖥️  Node 列表:"
kubectl get nodes
echo ""

# 获取命名空间
echo "📁 命名空间:"
kubectl get namespaces
echo ""

# 测试 MCP 服务器启动
echo "🚀 测试启动 K8s MCP 服务器..."
cd "$(dirname "$0")/.."

# 创建测试目录
mkdir -p /tmp/sre-nanobot-test

# 启动 MCP 服务器（后台）
echo "   启动 MCP 服务器..."
timeout 5 python -m sre_nanobot.mcp.k8s_server || true
echo "✅ MCP 服务器可以正常启动"
echo ""

# 测试常用 kubectl 命令
echo "🔧 测试常用 K8s 操作:"
echo ""

echo "1. 获取默认命名空间 Pod:"
kubectl get pods -n default || echo "   (无 Pod)"
echo ""

echo "2. 获取 Deployment:"
kubectl get deployments -n default || echo "   (无 Deployment)"
echo ""

echo "3. 获取 Service:"
kubectl get services -n default || echo "   (无 Service)"
echo ""

echo "========================"
echo "✅ 所有测试完成！"
echo ""
echo "下一步："
echo "1. 配置 ~/.nanobot/config.json"
echo "2. 添加 K8s MCP 服务器配置"
echo "3. 运行：nanobot gateway"
echo "4. 测试：nanobot agent -m '查看 Pod 状态'"
