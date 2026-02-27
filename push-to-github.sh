#!/bin/bash
# SRE-NanoBot 推送到 GitHub 脚本

set -e

echo "=================================================="
echo "  SRE-NanoBot 推送到 GitHub"
echo "=================================================="
echo ""

cd "$(dirname "$0")"

# 检查 Git
if ! command -v git &> /dev/null; then
    echo "❌ Git 未安装"
    exit 1
fi

# 初始化 Git 仓库（如果还没有）
if [ ! -d ".git" ]; then
    echo "初始化 Git 仓库..."
    git init
fi

# 添加所有文件
echo "添加文件..."
git add -A

# 提交
echo "提交更改..."
git commit -m "SRE-NanoBot 完整功能

- 4 个 Agent (K8s/Monitor/Incident/AutoFix)
- 2 个 MCP 服务器 (K8s/Prometheus)
- 15+ 标准运维预案
- 飞书通知集成
- WebUI (Ant Design Pro + FastAPI)
- 完整测试套件

阶段 1-5 完成，WebUI 开发中" || echo "没有更改需要提交"

# 设置分支名称
git branch -M main 2>/dev/null || true

# 添加远程仓库（如果还没有）
if ! git remote | grep -q origin; then
    echo "添加远程仓库..."
    git remote add origin https://github.com/bugtest/sre-nanobot.git
fi

# 推送
echo ""
echo "推送到 GitHub..."
echo "⚠️  需要 GitHub 认证"
echo ""
echo "请使用以下方式之一："
echo "1. 输入 GitHub 用户名和密码/PAT"
echo "2. 或者配置 SSH 密钥"
echo ""

# 尝试推送
git push -u origin main

echo ""
echo "✅ 推送成功！"
echo ""
echo "GitHub 仓库：https://github.com/bugtest/sre-nanobot"
echo ""
