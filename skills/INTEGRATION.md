# Skills 集成指南

> 将 Skills 集成到 SRE-NanoBot

---

## 🎯 集成方式

### 1. 与 NanoBot 集成

编辑 `~/.nanobot/config.json`：

```json
{
  "skills": {
    "enabled": [
      "sre_alert_handler",
      "sre_incident_analyzer",
      "sre_runbook_executor"
    ],
    "sre_alert_handler": {
      "auto_approve_threshold": "P2",
      "notification_channel": "feishu"
    }
  }
}
```

### 2. 与 WebUI 集成

在 WebUI 中添加 Skills 管理页面：

```typescript
// 访问 Skills
const result = await axios.post('/api/skills/sre_alert_handler/execute', {
  alert: alertData
});
```

### 3. 与 Agent 集成

在 Agent 中调用 Skills：

```python
from skills.loader import SkillLoader

class SREAgent:
    def __init__(self):
        self.skill_loader = SkillLoader()
        self.skill_loader.load_config(config)
        self.skill_loader.load_all_skills()
    
    async def handle_alert(self, alert):
        # 使用 Skill 处理
        result = await self.skill_loader.execute_skill(
            'sre_alert_handler',
            alert=alert
        )
        return result
```

---

## 🔧 API 端点

### 执行 Skill

```http
POST /api/skills/{skill_name}/execute
Content-Type: application/json

{
  "alert": {...},
  "auto_approve": true
}
```

### 列出 Skills

```http
GET /api/skills

Response:
{
  "skills": [
    {
      "name": "sre_alert_handler",
      "version": "1.0.0",
      "description": "自动处理运维告警"
    }
  ]
}
```

### 获取 Skill 状态

```http
GET /api/skills/{skill_name}/status

Response:
{
  "name": "sre_alert_handler",
  "enabled": true,
  "config": {...}
}
```

---

## 📊 监控指标

### Prometheus 指标

```python
from prometheus_client import Counter, Histogram

# 定义指标
skill_execution_total = Counter(
    'skill_execution_total',
    'Total skill executions',
    ['skill_name', 'status']
)

skill_execution_duration = Histogram(
    'skill_execution_duration_seconds',
    'Skill execution duration',
    ['skill_name']
)
```

---

## 🆘 故障排查

### 常见问题

**Q: Skill 未加载**

A: 检查：
1. Skills 目录是否正确
2. config.json 中是否启用
3. handler.py 是否存在

**Q: 执行失败**

A: 检查日志：
```bash
tail -f logs/skill.sre_alert_handler.log
```

---

*最后更新：2026-02-27*
