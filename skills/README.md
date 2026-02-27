# SRE Skills

> SRE-NanoBot 技能包

---

## 📚 Skills 是什么

Skills 是 SRE-NanoBot 的**业务逻辑扩展包**，用于：

- ✅ 封装复杂业务逻辑
- ✅ 实现自动化工作流
- ✅ 快速响应新需求
- ✅ 分享和复用最佳实践

---

## 🎯 Skills vs MCP

| 特性 | MCP | Skills |
|------|------|--------|
| **定位** | 标准化工具 | 业务逻辑 |
| **场景** | 外部工具集成 | 工作流自动化 |
| **开发** | Python | Markdown + Python |
| **加载** | 启动时 | 热加载 |
| **示例** | K8s API, Prometheus | 告警处理，故障分析 |

**两者关系：** 互补而非替代

---

## 📁 Skills 目录结构

```
skills/
├── README.md                    # 本文件
├── loader.py                    # Skills 加载器
├── base.py                      # Skills 基类
├── sre_alert_handler/           # 告警处理技能
│   ├── SKILL.md                # 技能说明
│   ├── handler.py              # 处理逻辑
│   └── config.yaml             # 配置
├── sre_incident_analyzer/       # 故障分析技能
└── sre_runbook_executor/        # 预案执行技能
```

---

## 🚀 快速开始

### 1. 启用 Skills

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

### 2. 使用 Skills

**CLI 方式：**
```bash
# 使用告警处理技能
nanobot skill sre_alert_handler --alert "PodCrashLooping"

# 使用故障分析技能
nanobot skill sre_incident_analyzer --incident "INC-001"
```

**WebUI 方式：**
访问 Skills 管理页面（开发中）

### 3. 开发 Skills

参考 [开发指南](./开发指南.md)

---

## 📦 内置 Skills

### P0 优先级

| Skill | 功能 | 状态 |
|-------|------|------|
| `sre_alert_handler` | 告警自动处理 | ✅ |
| `sre_incident_analyzer` | 故障智能分析 | ✅ |
| `sre_runbook_executor` | 预案自动执行 | ✅ |

### P1 优先级

| Skill | 功能 | 状态 |
|-------|------|------|
| `sre_daily_report` | 日报自动生成 | ⏳ |
| `sre_morning_check` | 晨检自动化 | ⏳ |
| `sre_change_validator` | 变更验证 | ⏳ |

---

## 🔧 开发指南

### 1. 创建 Skill 目录

```bash
cd skills
mkdir my_new_skill
cd my_new_skill
```

### 2. 创建 SKILL.md

```markdown
# My New Skill

## 功能描述
[简短描述技能功能]

## 触发条件
- [条件 1]
- [条件 2]

## 输入参数
- param1: 描述
- param2: 描述

## 输出
- 返回值描述

## 使用示例
```bash
nanobot skill my_new_skill --param1 value1
```
```

### 3. 创建 handler.py

```python
from skills.base import BaseSkill

class MyNewSkill(BaseSkill):
    name = "my_new_skill"
    description = "技能描述"
    
    async def execute(self, **kwargs):
        # 实现逻辑
        return {"success": True, "result": "..."}
```

### 4. 创建配置

```yaml
# config.yaml
name: my_new_skill
version: 1.0
enabled: true
parameters:
  param1:
    type: string
    required: true
  param2:
    type: int
    default: 10
```

---

## 📊 Skill 生命周期

```
加载 → 初始化 → 执行 → 清理
  ↓        ↓        ↓       ↓
验证    配置     业务    释放
配置    加载     逻辑    资源
```

---

## 🎯 最佳实践

### 1. 单一职责

每个 Skill 只负责一个明确的功能

```python
# ✅ 好的设计
class AlertHandler:  # 只处理告警
    pass

class IncidentAnalyzer:  # 只分析故障
    pass

# ❌ 不好的设计
class SREMaster:  # 什么都做
    pass
```

### 2. 配置驱动

使用配置文件而非硬编码

```python
# ✅ 好的设计
config = self.load_config()
threshold = config.get('threshold', 5)

# ❌ 不好的设计
threshold = 5  # 硬编码
```

### 3. 错误处理

完善的错误处理和日志记录

```python
try:
    result = await self.process()
except Exception as e:
    self.logger.error(f"处理失败：{e}")
    return {"success": False, "error": str(e)}
```

### 4. 文档完善

每个 Skill 都要有完整的文档

- SKILL.md（功能说明）
- 代码注释
- 使用示例
- 配置说明

---

## 📞 支持

- **文档：** 查看 [开发指南](./开发指南.md)
- **示例：** 参考内置 Skills
- **问题：** GitHub Issues

---

*最后更新：2026-02-27*
