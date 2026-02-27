# 阶段 6：WebUI 开发报告

> 开始时间：2026-02-27
> 技术方案：Ant Design Pro + FastAPI

---

## ✅ 已完成内容

| 组件 | 状态 | 文件 | 说明 |
|------|------|------|------|
| **后端框架** | ✅ | `webui/backend/main.py` | FastAPI API 服务 |
| **前端框架** | ✅ | `webui/frontend/` | Ant Design Pro |
| **Dashboard** | ✅ | `src/pages/Dashboard/` | 系统总览页面 |
| **基础布局** | ✅ | `src/layouts/` | 导航布局 |
| **启动脚本** | ✅ | `start.sh` | 快速启动 |

---

## 🎨 技术架构

### 前端

```
React 18 + Ant Design Pro 5 + Umi 4
├── 组件库：Ant Design 5
├── 图表：ECharts
├── HTTP：Axios
├── 路由：Umi Router
└── 状态管理：Umi Model
```

### 后端

```
FastAPI + WebSocket
├── API 框架：FastAPI
├── WebSocket：实时推送
├── 数据验证：Pydantic
└── 文档：Swagger/OpenAPI
```

---

## 📁 项目结构

```
webui/
├── backend/
│   ├── main.py              # FastAPI 主应用
│   ├── requirements.txt     # Python 依赖
│   └── ...
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   └── Dashboard/   # Dashboard 页面
│   │   └── layouts/
│   │       └── BasicLayout  # 基础布局
│   ├── package.json
│   └── .umirc.ts
├── start.sh                 # 启动脚本
└── README.md
```

---

## 🚀 快速开始

### 方式 1：一键启动

```bash
cd webui
./start.sh
```

### 方式 2：分别启动

**后端：**
```bash
cd webui/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

**前端：**
```bash
cd webui/frontend
npm install
npm start
```

**访问：**
- 前端：http://localhost:3000
- 后端：http://localhost:8000
- API 文档：http://localhost:8000/docs

---

## 📊 核心功能

### 1. Dashboard（已完成 ✅）

**功能：**
- 系统健康状态卡片
- 告警统计（今日/本周）
- 自动修复统计
- 服务可用性
- 告警趋势图表
- 实时告警列表

**截图预览：**
```
┌─────────────────────────────────────────────────┐
│  SRE-NanoBot 智能运维平台                       │
├─────────────────────────────────────────────────┤
│  📊 系统总览                                    │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐               │
│  │告警 │ │故障 │ │修复 │ │可用 │               │
│  │ 12  │ │  2  │ │ 51  │ │99.9%│               │
│  └─────┘ └─────┘ └─────┘ └─────┘               │
│                                                 │
│  📈 告警趋势           📊 告警分布              │
│  [折线图]              [饼图]                   │
│                                                 │
│  🚨 实时告警                                    │
│  [告警列表表格]                                 │
└─────────────────────────────────────────────────┘
```

### 2. 告警中心（待开发）

**计划功能：**
- 告警列表（分页、筛选、排序）
- 告警详情查看
- 告警确认/分配/关闭
- 告警历史查询
- 告警规则管理

### 3. 故障管理（待开发）

**计划功能：**
- 故障列表
- 故障详情（时间线、根因、影响面）
- 故障处理流程
- 故障报告查看
- 改进措施跟踪

### 4. 预案管理（待开发）

**计划功能：**
- 预案列表
- 预案详情
- 预案执行历史
- 预案编辑器（可视化）
- 预案版本管理

### 5. 监控指标（待开发）

**计划功能：**
- K8s 集群指标
- 服务性能指标
- 资源使用趋势
- 自定义仪表板

### 6. 系统设置（待开发）

**计划功能：**
- Agent 配置
- 通知渠道配置
- 审批流程配置
- 用户权限管理

---

## 🔌 API 接口

### 已实现 API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/health` | 健康检查 |
| GET | `/api/dashboard/stats` | Dashboard 统计 |
| GET | `/api/alerts` | 告警列表 |
| GET | `/api/alerts/{id}` | 告警详情 |
| POST | `/api/alerts/{id}/acknowledge` | 确认告警 |
| GET | `/api/incidents` | 故障列表 |
| GET | `/api/incidents/{id}` | 故障详情 |
| GET | `/api/runbooks` | 预案列表 |
| GET | `/api/runbooks/{id}` | 预案详情 |
| POST | `/api/runbooks/{id}/execute` | 执行预案 |
| GET | `/api/metrics/cpu` | CPU 指标 |
| GET | `/api/metrics/memory` | 内存指标 |
| GET | `/api/metrics/alerts` | 告警指标 |
| WS | `/ws/alerts` | 告警 WebSocket |

### API 文档

访问：http://localhost:8000/docs

---

## 📈 开发进度

```
阶段 1：基础框架       ✅ 100%
  - 项目脚手架        ✅
  - API 后端框架       ✅
  - 前端基础布局       ✅
  - Dashboard 页面     ✅

阶段 2：核心页面       ⏳ 20%
  - Dashboard         ✅
  - 告警列表          ⏳
  - 故障列表          ⏳
  - 预案列表          ⏳

阶段 3：实时监控       ⏳ 0%
  - WebSocket 集成     ⏳
  - 实时告警推送       ⏳
  - 指标图表          ⏳

阶段 4：交互功能       ⏳ 0%
  - 告警确认          ⏳
  - 审批操作          ⏳
  - 预案执行          ⏳

阶段 5：优化部署       ⏳ 0%
  - 性能优化          ⏳
  - Docker 打包        ⏳
  - 文档完善          ⏳

总体进度：24% (1/5 阶段)
```

---

## 🎯 下一步计划

### 本周（2 天）

- [ ] 完成告警列表页面
- [ ] 完成故障列表页面
- [ ] 完成预案列表页面
- [ ] 连接真实 API

### 下周（3-4 天）

- [ ] WebSocket 实时推送
- [ ] 告警确认功能
- [ ] 预案执行功能
- [ ] 图表优化

### 第 3 周（2-3 天）

- [ ] 性能优化
- [ ] Docker 打包
- [ ] 文档完善
- [ ] 用户测试

---

## 🧪 测试

### 后端测试

```bash
cd webui/backend
source venv/bin/activate
pytest
```

### 前端测试

```bash
cd webui/frontend
npm test
```

---

## 📊 界面预览

### Dashboard
- ✅ 统计卡片（4 个）
- ✅ 告警趋势图
- ✅ 告警分布图
- ✅ 实时告警列表

### 告警中心（计划）
- 告警列表（带筛选）
- 告警详情页
- 告警确认/分配

### 故障管理（计划）
- 故障列表
- 故障详情（时间线）
- 故障报告

---

## 🐛 已知问题

1. **模拟数据**
   - 当前使用模拟数据
   - 需要连接真实 Agent

2. **WebSocket**
   - 基础框架已搭建
   - 需要实现实时推送逻辑

3. **认证授权**
   - 暂未实现
   - 计划添加 JWT 认证

---

## 📞 支持信息

### 文档

- 项目说明：`../webui/README.md`
- API 文档：http://localhost:8000/docs

### 启动

```bash
# 一键启动
./start.sh

# 单独启动后端
cd backend && uvicorn main:app --reload

# 单独启动前端
cd frontend && npm start
```

---

*报告生成时间：2026-02-27*
*版本：v1.0 (开发中)*
