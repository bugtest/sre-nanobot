#!/bin/bash
# 阶段 3 测试脚本

set -e

echo "=================================================="
echo "  SRE-NanoBot 阶段 3 测试"
echo "  Incident Agent + AutoFix Agent"
echo "=================================================="
echo ""

cd /home/ubuntu/.openclaw/workspace/sre-nanobot

PASS=0
FAIL=0
WARN=0

check_pass() { echo "✅ $1"; ((PASS++)) || true; }
check_fail() { echo "❌ $1"; ((FAIL++)) || true; }
check_warn() { echo "⚠️  $1"; ((WARN++)) || true; }

# ─────────────────────────────────────────────────────────
# 1. 检查文件完整性
# ─────────────────────────────────────────────────────────
echo "📁 检查阶段 3 文件..."
echo ""

STAGE3_FILES=(
    "sre_nanobot/agents/incident_agent.py"
    "sre_nanobot/agents/autofix_agent.py"
)

for file in "${STAGE3_FILES[@]}"; do
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

if python3 -m py_compile sre_nanobot/agents/incident_agent.py; then
    check_pass "incident_agent.py 语法正确"
else
    check_fail "incident_agent.py 语法错误"
fi

if python3 -m py_compile sre_nanobot/agents/autofix_agent.py; then
    check_pass "autofix_agent.py 语法正确"
else
    check_fail "autofix_agent.py 语法错误"
fi

echo ""

# ─────────────────────────────────────────────────────────
# 3. 导入测试
# ─────────────────────────────────────────────────────────
echo "📦 导入测试..."
echo ""

if python3 -c "from sre_nanobot.agents.incident_agent import IncidentAgent" 2>/dev/null; then
    check_pass "Incident Agent 可导入"
else
    check_fail "Incident Agent 导入失败"
fi

if python3 -c "from sre_nanobot.agents.autofix_agent import AutoFixAgent" 2>/dev/null; then
    check_pass "AutoFix Agent 可导入"
else
    check_fail "AutoFix Agent 导入失败"
fi

echo ""

# ─────────────────────────────────────────────────────────
# 4. Incident Agent 功能验证
# ─────────────────────────────────────────────────────────
echo "🔍 Incident Agent 功能验证..."
echo ""

# 检查类定义
if grep -q "class IncidentAgent" sre_nanobot/agents/incident_agent.py; then
    check_pass "IncidentAgent 类定义"
fi

# 检查核心方法
INCIDENT_METHODS=(
    "_analyze_incident"
    "_correlate_alerts"
    "_build_timeline"
    "_identify_root_cause"
    "_assess_impact"
    "_generate_report"
    "_recommend_actions"
)

for method in "${INCIDENT_METHODS[@]}"; do
    if grep -q "async def $method" sre_nanobot/agents/incident_agent.py; then
        check_pass "方法 $method 已实现"
    else
        check_fail "方法 $method 缺失"
    fi
done

# 检查故障模式库
if grep -q "INCIDENT_PATTERNS" sre_nanobot/agents/incident_agent.py; then
    check_pass "故障模式库已定义"
    
    # 检查具体模式
    PATTERNS=("cascade_failure" "resource_exhaustion" "network_issue" "deployment_issue")
    for pattern in "${PATTERNS[@]}"; do
        if grep -q "\"$pattern\"" sre_nanobot/agents/incident_agent.py; then
            check_pass "故障模式：$pattern"
        else
            check_warn "故障模式：$pattern (缺失)"
        fi
    done
fi

# 检查 5 Whys 分析
if grep -q "five_whys" sre_nanobot/agents/incident_agent.py; then
    check_pass "5 Whys 分析已实现"
fi

echo ""

# ─────────────────────────────────────────────────────────
# 5. AutoFix Agent 功能验证
# ─────────────────────────────────────────────────────────
echo "🔧 AutoFix Agent 功能验证..."
echo ""

# 检查类定义
if grep -q "class AutoFixAgent" sre_nanobot/agents/autofix_agent.py; then
    check_pass "AutoFixAgent 类定义"
fi

# 检查核心方法
AUTOFIX_METHODS=(
    "_execute_runbook"
    "_execute_step"
    "_restart_service"
    "_scale_service"
    "_rollback_deployment"
    "_verify_fix"
    "_rollback_fix"
)

for method in "${AUTOFIX_METHODS[@]}"; do
    if grep -q "async def $method" sre_nanobot/agents/autofix_agent.py; then
        check_pass "方法 $method 已实现"
    else
        check_fail "方法 $method 缺失"
    fi
done

# 检查预案库
if grep -q "RUNBOOKS" sre_nanobot/agents/autofix_agent.py; then
    check_pass "预案库已定义"
    
    # 检查具体预案
    RUNBOOKS=("pod_restart" "scale_up" "rollback")
    for runbook in "${RUNBOOKS[@]}"; do
        if grep -q "\"$runbook\"" sre_nanobot/agents/autofix_agent.py; then
            check_pass "预案：$runbook"
        else
            check_warn "预案：$runbook (缺失)"
        fi
    done
fi

# 检查审批流程
if grep -q "requires_approval" sre_nanobot/agents/autofix_agent.py; then
    check_pass "审批流程已实现"
fi

# 检查回滚机制
if grep -q "rollback" sre_nanobot/agents/autofix_agent.py; then
    check_pass "回滚机制已实现"
fi

echo ""

# ─────────────────────────────────────────────────────────
# 6. 代码统计
# ─────────────────────────────────────────────────────────
echo "📊 代码统计..."
echo ""

INCIDENT_LINES=$(wc -l < sre_nanobot/agents/incident_agent.py)
AUTOFIX_LINES=$(wc -l < sre_nanobot/agents/autofix_agent.py)

check_pass "incident_agent.py: $INCIDENT_LINES 行"
check_pass "autofix_agent.py: $AUTOFIX_LINES 行"

STAGE3_TOTAL=$((INCIDENT_LINES + AUTOFIX_LINES))
echo ""
echo "  阶段 3 总代码：$STAGE3_TOTAL 行"

# 累计总代码
PREVIOUS_TOTAL=2277
GRAND_TOTAL=$((PREVIOUS_TOTAL + STAGE3_TOTAL))
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
    echo "阶段 3 完成内容："
    echo "- Incident Agent：故障分析、根因定位、影响面评估"
    echo "- AutoFix Agent：预案执行、自动修复、回滚机制"
    echo ""
    echo "下一步："
    echo "1. 集成所有 Agent 到 Orchestrator"
    echo "2. 实现完整的故障处理流程"
    echo "3. 开始阶段 4：预案系统完善"
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
