# SRE 告警处理技能

> 自动处理运维告警

---

## 📚 功能描述

自动接收、分析和处理运维告警，支持：

- ✅ 告警自动分类
- ✅ 根因智能分析
- ✅ 预案自动匹配
- ✅ 审批流程集成
- ✅ 飞书通知

---

## 🎯 触发条件

- 收到 P0/P1/P2 级别告警
- Prometheus Alertmanager Webhook
- 手动触发

---

## 📥 输入参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `alert` | dict | ✅ | 告警对象 |
| `auto_approve` | bool | ❌ | 是否自动审批（默认 false） |
| `notification` | bool | ❌ | 是否发送通知（默认 true） |

### Alert 对象结构

```json
{
  "name": "PodCrashLooping",
  "severity": "P1",
  "namespace": "production",
  "pod": "api-service-abc12",
  "description": "Pod 重启次数过多"
}
```

---

## 📤 输出

```json
{
  "success": true,
  "alert_id": "ALT-001",
  "status": "processing",
  "analysis": {
    "root_cause": "内存耗尽",
    "confidence": 0.85,
    "affected_services": ["api-service"]
  },
  "action": {
    "runbook": "pod_restart",
    "approved": true,
    "executed": true
  },
  "notification": {
    "sent": true,
    "channel": "feishu"
  }
}
```

---

## 🚀 使用示例

### CLI 方式

```bash
# 处理告警
nanobot skill sre_alert_handler \
  --alert '{"name":"PodCrashLooping","severity":"P1"}'

# 自动审批 P2 及以下告警
nanobot skill sre_alert_handler \
  --alert '{"name":"HighCPU","severity":"P2"}' \
  --auto_approve true
```

### API 方式

```bash
curl -X POST http://localhost:8000/api/skills/sre_alert_handler/execute \
  -H "Content-Type: application/json" \
  -d '{
    "alert": {
      "name": "PodCrashLooping",
      "severity": "P1"
    },
    "auto_approve": false
  }'
```

### Python 方式

```python
from skills.loader import SkillLoader

loader = SkillLoader()
loader.load_skill('sre_alert_handler')

result = await loader.execute_skill(
    'sre_alert_handler',
    alert={'name': 'PodCrashLooping', 'severity': 'P1'}
)
```

---

## ⚙️ 配置说明

```yaml
# skills/sre_alert_handler/config.yaml

name: sre_alert_handler
version: 1.0
enabled: true

# 自动审批配置
auto_approve:
  enabled: true
  max_severity: "P2"  # P2 及以下自动审批

# 通知配置
notification:
  enabled: true
  channel: "feishu"
  on_start: true     # 开始时通知
  on_complete: true  # 完成时通知
  on_error: true     # 错误时通知

# 告警处理配置
processing:
  timeout: 300       # 超时时间（秒）
  retry_count: 3     # 重试次数
  retry_interval: 10 # 重试间隔（秒）
```

---

## 🔄 处理流程

```
1. 接收告警
   ↓
2. 验证告警有效性
   ↓
3. 分析告警根因
   ↓
4. 匹配处理预案
   ↓
5. 请求审批（如需要）
   ↓
6. 执行预案
   ↓
7. 验证结果
   ↓
8. 发送通知
```

---

## 📊 处理策略

### P0 告警

- ✅ 立即通知（电话 + 飞书）
- ✅ 自动分析
- ❌ 不自动执行（需人工审批）

### P1 告警

- ✅ 立即通知（飞书）
- ✅ 自动分析
- ⚠️ 自动执行（配置决定）

### P2 告警

- ✅ 通知（飞书）
- ✅ 自动分析
- ✅ 自动执行

### P3 告警

- ⚠️ 记录日志
- ✅ 自动分析
- ✅ 自动执行

---

## 🛡️ 安全机制

### 审批机制

- P0 告警：必须人工审批
- P1 告警：可配置自动审批
- P2 及以下：默认自动审批

### 执行限制

- 生产环境操作需审批
- 大规模变更需多级审批
- 所有操作记录审计日志

### 回滚机制

- 执行失败自动回滚
- 超时自动中止
- 异常及时通知

---

## 📈 监控指标

| 指标 | 说明 |
|------|------|
| `skill.alert_handler.total` | 处理告警总数 |
| `skill.alert_handler.success` | 成功处理数 |
| `skill.alert_handler.failed` | 失败数 |
| `skill.alert_handler.duration` | 平均处理时长 |
| `skill.alert_handler.auto_approved` | 自动审批数 |

---

## 🆘 故障排查

### 常见问题

**Q: Skill 未加载**

A: 检查配置文件中是否启用：
```json
{
  "skills": {
    "enabled": ["sre_alert_handler"]
  }
}
```

**Q: 告警处理失败**

A: 检查日志：
```bash
tail -f logs/skill.sre_alert_handler.log
```

**Q: 通知未发送**

A: 检查飞书配置和 Webhook URL

---

## 📞 支持

- **文档：** 查看 Skills README
- **问题：** GitHub Issues
- **日志：** `logs/skill.sre_alert_handler.log`

---

*版本：1.0*
*最后更新：2026-02-27*
