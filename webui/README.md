# SRE-NanoBot WebUI

> 基于 Ant Design Pro + FastAPI 的智能运维管理平台

---

## 🚀 快速开始

### 后端启动

```bash
cd webui/backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 前端启动

```bash
cd webui/frontend
npm install
npm start
```

访问：http://localhost:3000

---

## 🛠️ 技术栈

### 前端
- React 18
- Ant Design Pro 5
- Umi 4
- ECharts
- WebSocket

### 后端
- FastAPI
- SQLAlchemy
- WebSocket
- Pydantic

---

## 📁 项目结构

```
webui/
├── backend/
│   ├── main.py              # FastAPI 主应用
│   ├── api/                 # API 路由
│   │   ├── alerts.py        # 告警 API
│   │   ├── incidents.py     # 故障 API
│   │   ├── runbooks.py      # 预案 API
│   │   └── metrics.py       # 指标 API
│   ├── models/              # 数据模型
│   ├── schemas/             # Pydantic 模型
│   └── websocket/           # WebSocket 处理
└── frontend/
    ├── src/
    │   ├── pages/           # 页面
    │   │   ├── Dashboard/   # Dashboard
    │   │   ├── Alerts/      # 告警管理
    │   │   ├── Incidents/   # 故障管理
    │   │   └── Runbooks/    # 预案管理
    │   ├── components/      # 组件
    │   └── services/        # API 服务
    └── package.json
```

---

## 📊 功能模块

- ✅ Dashboard（系统总览）
- ✅ 告警中心（实时告警）
- ✅ 故障管理（故障处理）
- ✅ 预案管理（预案执行）
- ✅ 监控指标（图表展示）
- ✅ 系统设置（配置管理）

---

## 🔐 默认账号

- 用户名：`admin`
- 密码：`admin123`

---

*版本：v1.0*
*最后更新：2026-02-27*
