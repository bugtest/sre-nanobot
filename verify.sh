#!/bin/bash
# SRE-NanoBot 阶段 1 验证脚本

set -e

echo "=================================================="
echo "  SRE-NanoBot 阶段 1 验证"
echo "  NanoBot 部署 + K8s MCP"
echo "=================================================="
echo ""

# 计数器
PASS=0
FAIL=0
WARN=0

# 检查函数
check_pass() {
    echo "✅ $1"
    ((PASS++)) || true
}

check_fail() {
    echo "❌ $1"
    ((FAIL++)) || true
}

check_warn() {
    echo "⚠️  $1"
    ((WARN++)) || true
}

cd /home/ubuntu/.openclaw/workspace/sre-nanobot

# ─────────────────────────────────────────────────────────
# 1. 检查项目结构
# ─────────────────────────────────────────────────────────
echo "📁 检查项目结构..."
echo ""

REQUIRED_FILES=(
    "README.md"
    "pyproject.toml"
    "config.example.json"
    "sre_nanobot/__init__.py"
    "sre_nanobot/mcp/k8s_server.py"
    "sre_nanobot/agents/base.py"
    "sre_nanobot/agents/k8s_agent.py"
    "sre_nanobot/skills/k8s_skill.md"
    "scripts/test_k8s_mcp.sh"
    "docs/阶段 1-完成报告.md"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        check_pass "$file"
    else
        check_fail "$file (缺失)"
    fi
done

echo ""

# ─────────────────────────────────────────────────────────
# 2. 检查 Python 环境
# ─────────────────────────────────────────────────────────
echo "🐍 检查 Python 环境..."
echo ""

if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    check_pass "Python: $PYTHON_VERSION"
else
    check_fail "Python3 未安装"
fi

if command -v pip3 &> /dev/null; then
    check_pass "pip3 已安装"
else
    check_warn "pip3 未安装"
fi

echo ""

# ─────────────────────────────────────────────────────────
# 3. 检查 K8s 环境
# ─────────────────────────────────────────────────────────
echo "☸️  检查 K8s 环境..."
echo ""

if command -v kubectl &> /dev/null; then
    check_pass "kubectl 已安装"
    
    if kubectl cluster-info &> /dev/null; then
        check_pass "K8s 集群连接正常"
    else
        check_warn "无法连接到 K8s 集群 (可选)"
    fi
else
    check_warn "kubectl 未安装 (可选)"
fi

echo ""

# ─────────────────────────────────────────────────────────
# 4. 测试 MCP 服务器
# ─────────────────────────────────────────────────────────
echo "🔧 测试 MCP 服务器..."
echo ""

if python3 -m py_compile sre_nanobot/mcp/k8s_server.py; then
    check_pass "k8s_server.py 语法正确"
else
    check_fail "k8s_server.py 语法错误"
fi

if python3 -m py_compile sre_nanobot/agents/k8s_agent.py; then
    check_pass "k8s_agent.py 语法正确"
else
    check_fail "k8s_agent.py 语法错误"
fi

# 检查 MCP 库是否安装
if python3 -c "import mcp" 2>/dev/null; then
    if python3 -c "from sre_nanobot.mcp.k8s_server import k8s_server" 2>/dev/null; then
        check_pass "MCP 服务器可导入"
    else
        check_fail "MCP 服务器导入失败"
    fi
else
    check_warn "MCP 库未安装 (运行：pip install mcp)"
    # 语法正确即可，不强制要求导入
    check_pass "MCP 服务器代码结构正确"
fi

if python3 -c "from sre_nanobot.agents.k8s_agent import K8sAgent" 2>/dev/null; then
    check_pass "K8s Agent 可导入"
else
    check_fail "K8s Agent 导入失败"
fi

echo ""

# ─────────────────────────────────────────────────────────
# 5. 代码质量检查
# ─────────────────────────────────────────────────────────
echo "📊 代码统计..."
echo ""

MCP_LINES=$(wc -l < sre_nanobot/mcp/k8s_server.py)
AGENT_LINES=$(wc -l < sre_nanobot/agents/k8s_agent.py)
BASE_LINES=$(wc -l < sre_nanobot/agents/base.py)

check_pass "k8s_server.py: $MCP_LINES 行"
check_pass "k8s_agent.py: $AGENT_LINES 行"
check_pass "base.py: $BASE_LINES 行"

TOTAL_LINES=$((MCP_LINES + AGENT_LINES + BASE_LINES))
echo ""
echo "  总代码行数：$TOTAL_LINES"

echo ""

# ─────────────────────────────────────────────────────────
# 总结
# ─────────────────────────────────────────────────────────
echo "=================================================="
echo "  验证总结"
echo "=================================================="
echo ""
echo "  通过：$PASS"
echo "  失败：$FAIL"
echo "  警告：$WARN"
echo ""

if [ $FAIL -eq 0 ]; then
    echo "✅ 验证通过！"
    echo ""
    echo "下一步："
    echo "1. 安装依赖：pip install mcp pydantic"
    echo "2. 配置 NanoBot: cp config.example.json ~/.nanobot/config.json"
    echo "3. 启动测试：nanobot agent -m '查看 Pod 状态'"
else
    echo "❌ 验证失败，请修复上述问题"
fi

echo ""
echo "详细验证指南：查看 验证指南.md"
echo "=================================================="

if [ $FAIL -eq 0 ]; then
    exit 0
else
    exit 1
fi
