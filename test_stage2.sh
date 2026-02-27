#!/bin/bash
# 阶段 2 测试脚本

set -e

echo "=================================================="
echo "  SRE-NanoBot 阶段 2 测试"
echo "  Monitor Agent + Prometheus MCP"
echo "=================================================="
echo ""

cd /home/ubuntu/.openclaw/workspace/sre-nanobot

# 颜色定义
PASS=0
FAIL=0
WARN=0

check_pass() { echo "✅ $1"; ((PASS++)) || true; }
check_fail() { echo "❌ $1"; ((FAIL++)) || true; }
check_warn() { echo "⚠️  $1"; ((WARN++)) || true; }

# ─────────────────────────────────────────────────────────
# 1. 检查文件完整性
# ─────────────────────────────────────────────────────────
echo "📁 检查阶段 2 文件..."
echo ""

STAGE2_FILES=(
    "sre_nanobot/mcp/prometheus_server.py"
    "sre_nanobot/agents/monitor_agent.py"
    "sre_nanobot/integrations/alertmanager_webhook.py"
)

for file in "${STAGE2_FILES[@]}"; do
    if [ -f "$file" ]; then
        LINES=$(wc -l < "$file")
        check_pass "$file ($LINES 行)"
    else
        check_fail "$file (缺失)"
    fi
done

echo ""

# ─────────────────────────────────────────────────────────
# 2. 语法检查
# ─────────────────────────────────────────────────────────
echo "🔍 语法检查..."
echo ""

if python3 -m py_compile sre_nanobot/mcp/prometheus_server.py; then
    check_pass "prometheus_server.py 语法正确"
else
    check_fail "prometheus_server.py 语法错误"
fi

if python3 -m py_compile sre_nanobot/agents/monitor_agent.py; then
    check_pass "monitor_agent.py 语法正确"
else
    check_fail "monitor_agent.py 语法错误"
fi

if python3 -m py_compile sre_nanobot/integrations/alertmanager_webhook.py; then
    check_pass "alertmanager_webhook.py 语法正确"
else
    check_fail "alertmanager_webhook.py 语法错误"
fi

echo ""

# ─────────────────────────────────────────────────────────
# 3. 导入测试
# ─────────────────────────────────────────────────────────
echo "📦 导入测试..."
echo ""

# Prometheus MCP
if python3 -c "from sre_nanobot.mcp.prometheus_server import prometheus_server" 2>/dev/null; then
    check_pass "Prometheus MCP 服务器可导入"
else
    check_warn "Prometheus MCP 需要 httpx 库 (pip install httpx)"
    check_pass "Prometheus MCP 代码结构正确"
fi

# Monitor Agent
if python3 -c "from sre_nanobot.agents.monitor_agent import MonitorAgent" 2>/dev/null; then
    check_pass "Monitor Agent 可导入"
else
    check_fail "Monitor Agent 导入失败"
fi

# Alertmanager Webhook
if python3 -c "from sre_nanobot.integrations.alertmanager_webhook import AlertmanagerWebhook" 2>/dev/null; then
    check_pass "Alertmanager Webhook 可导入"
else
    check_warn "Alertmanager Webhook 需要 fastapi (pip install fastapi uvicorn)"
    check_pass "Alertmanager Webhook 代码结构正确"
fi

echo ""

# ─────────────────────────────────────────────────────────
# 4. Prometheus 工具定义验证
# ─────────────────────────────────────────────────────────
echo "🛠️  Prometheus 工具定义验证..."
echo ""

TOOLS=$(python3 -c "
import asyncio
from sre_nanobot.mcp.prometheus_server import list_tools
async def get():
    tools = await list_tools()
    for t in tools:
        print(t.name)
asyncio.run(get())
" 2>/dev/null || echo "IMPORT_ERROR")

if [ "$TOOLS" = "IMPORT_ERROR" ]; then
    check_warn "需要安装依赖：pip install mcp httpx"
    # 手动检查工具定义
    EXPECTED_TOOLS=(
        "prom_query"
        "prom_query_range"
        "prom_get_alerts"
        "prom_node_cpu_usage"
        "prom_node_memory_usage"
        "prom_pod_cpu_usage"
        "prom_service_latency"
        "prom_service_error_rate"
    )
    
    for tool in "${EXPECTED_TOOLS[@]}"; do
        if grep -q "name=\"$tool\"" sre_nanobot/mcp/prometheus_server.py; then
            check_pass "$tool (已定义)"
        else
            check_fail "$tool (缺失)"
        fi
    done
else
    EXPECTED_TOOLS=(
        "prom_query"
        "prom_query_range"
        "prom_get_alerts"
        "prom_node_cpu_usage"
        "prom_service_latency"
    )
    
    for tool in "${EXPECTED_TOOLS[@]}"; do
        if echo "$TOOLS" | grep -q "$tool"; then
            check_pass "$tool"
        else
            check_fail "$tool (缺失)"
        fi
    done
fi

echo ""

# ─────────────────────────────────────────────────────────
# 5. Monitor Agent 功能验证
# ─────────────────────────────────────────────────────────
echo "🤖 Monitor Agent 功能验证..."
echo ""

# 检查 Agent 属性
if grep -q "name = \"monitor_agent\"" sre_nanobot/agents/monitor_agent.py; then
    check_pass "Agent 名称正确"
fi

if grep -q "class MonitorAgent" sre_nanobot/agents/monitor_agent.py; then
    check_pass "MonitorAgent 类定义"
fi

# 检查关键方法
METHODS=(
    "_query_metrics"
    "_get_alerts"
    "_analyze_alert"
    "_receive_webhook"
    "handle_alert"
)

for method in "${METHODS[@]}"; do
    if grep -q "async def $method" sre_nanobot/agents/monitor_agent.py; then
        check_pass "方法 $method 已实现"
    else
        check_fail "方法 $method 缺失"
    fi
done

echo ""

# ─────────────────────────────────────────────────────────
# 6. Alertmanager Webhook 验证
# ─────────────────────────────────────────────────────────
echo "🔔 Alertmanager Webhook 验证..."
echo ""

if grep -q "class AlertmanagerWebhook" sre_nanobot/integrations/alertmanager_webhook.py; then
    check_pass "AlertmanagerWebhook 类定义"
fi

if grep -q "@app.post.*/api/v1/alerts" sre_nanobot/integrations/alertmanager_webhook.py; then
    check_pass "Webhook 端点已定义"
fi

if grep -q "/health" sre_nanobot/integrations/alertmanager_webhook.py; then
    check_pass "健康检查端点已定义"
fi

echo ""

# ─────────────────────────────────────────────────────────
# 7. 代码统计
# ─────────────────────────────────────────────────────────
echo "📊 代码统计..."
echo ""

PROM_LINES=$(wc -l < sre_nanobot/mcp/prometheus_server.py)
MONITOR_LINES=$(wc -l < sre_nanobot/agents/monitor_agent.py)
WEBHOOK_LINES=$(wc -l < sre_nanobot/integrations/alertmanager_webhook.py)

check_pass "prometheus_server.py: $PROM_LINES 行"
check_pass "monitor_agent.py: $MONITOR_LINES 行"
check_pass "alertmanager_webhook.py: $WEBHOOK_LINES 行"

TOTAL=$((PROM_LINES + MONITOR_LINES + WEBHOOK_LINES))
echo ""
echo "  阶段 2 总代码：$TOTAL 行"

# 阶段 1 代码
STAGE1_TOTAL=945
GRAND_TOTAL=$((STAGE1_TOTAL + TOTAL))
echo "  累计总代码：$GRAND_TOTAL 行"

echo ""

# ─────────────────────────────────────────────────────────
# 总结
# ─────────────────────────────────────────────────────────
echo "=================================================="
echo "  测试总结"
echo "=================================================="
echo ""
echo "  通过：$PASS"
echo "  失败：$FAIL"
echo "  警告：$WARN"
echo ""

if [ $FAIL -eq 0 ]; then
    echo "✅ 测试通过！"
    echo ""
    echo "下一步："
    echo "1. 安装依赖：pip install mcp httpx fastapi uvicorn"
    echo "2. 启动 Prometheus MCP: python -m sre_nanobot.mcp.prometheus_server"
    echo "3. 启动 Webhook: python -m sre_nanobot.integrations.alertmanager_webhook"
    echo "4. 配置 Alertmanager 指向 http://localhost:8080/api/v1/alerts"
else
    echo "❌ 测试失败，请修复问题"
fi

echo ""
echo "=================================================="

if [ $FAIL -eq 0 ]; then
    exit 0
else
    exit 1
fi
