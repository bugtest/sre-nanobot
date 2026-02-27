"""
SRE-NanoBot WebUI Backend

FastAPI 后端服务
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import asyncio
import json
from datetime import datetime
from typing import List, Dict, Any
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建 FastAPI 应用
app = FastAPI(
    title="SRE-NanoBot API",
    description="智能运维管理平台 API",
    version="1.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境需要限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket 连接管理器
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket 连接成功，当前连接数：{len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket 断开连接，当前连接数：{len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """广播消息给所有连接"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"发送消息失败：{e}")

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """发送个人消息"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"发送个人消息失败：{e}")

manager = ConnectionManager()

# 模拟数据（实际应该从数据库或 Agent 获取）
mock_alerts = [
    {
        "id": "alert-001",
        "name": "PodCrashLooping",
        "severity": "P1",
        "status": "firing",
        "namespace": "production",
        "service": "api-service",
        "pod": "api-service-6d8f9c7b5-abc12",
        "description": "Pod 在 5 分钟内重启 5 次",
        "starts_at": "2026-02-27T10:00:00Z",
        "duration": "30 分钟"
    },
    {
        "id": "alert-002",
        "name": "HighCPUUsage",
        "severity": "P2",
        "status": "firing",
        "namespace": "production",
        "service": "api-service",
        "description": "CPU 使用率超过 85%",
        "starts_at": "2026-02-27T10:05:00Z",
        "duration": "25 分钟"
    },
    {
        "id": "alert-003",
        "name": "HighMemoryUsage",
        "severity": "P2",
        "status": "resolved",
        "namespace": "production",
        "service": "web-frontend",
        "description": "内存使用率超过 90%",
        "starts_at": "2026-02-27T09:00:00Z",
        "ends_at": "2026-02-27T09:30:00Z",
        "duration": "30 分钟"
    }
]

mock_incidents = [
    {
        "id": "INC-2026-02-27-001",
        "severity": "P1",
        "status": "investigating",
        "summary": "发生资源耗尽，影响 1 个服务",
        "root_cause": "内存限制过低导致 OOM",
        "affected_services": ["api-service"],
        "duration": "30 分钟",
        "user_impact": "10%",
        "created_at": "2026-02-27T10:00:00Z"
    },
    {
        "id": "INC-2026-02-26-001",
        "severity": "P2",
        "status": "resolved",
        "summary": "服务响应延迟过高",
        "root_cause": "数据库慢查询",
        "affected_services": ["api-service"],
        "duration": "1 小时",
        "user_impact": "5%",
        "created_at": "2026-02-26T14:00:00Z",
        "resolved_at": "2026-02-26T15:00:00Z"
    }
]

mock_runbooks = [
    {
        "id": "pod_restart",
        "name": "Pod 重启预案",
        "version": "1.0",
        "description": "重启故障 Pod",
        "severity": "low",
        "triggers": ["PodCrashLooping", "PodNotReady"],
        "execution_count": 15,
        "success_rate": 93.3
    },
    {
        "id": "scale_up",
        "name": "扩容预案",
        "version": "1.0",
        "description": "服务扩容",
        "severity": "low",
        "triggers": ["HighCPUUsage", "HighMemoryUsage"],
        "execution_count": 28,
        "success_rate": 96.4
    },
    {
        "id": "rollback",
        "name": "回滚预案",
        "version": "1.0",
        "description": "部署回滚",
        "severity": "medium",
        "triggers": ["DeploymentFailed", "HighErrorRate"],
        "execution_count": 8,
        "success_rate": 87.5
    }
]

# ─────────────────────────────────────────────────────
# API 路由
# ─────────────────────────────────────────────────────

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "SRE-NanoBot API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """获取 Dashboard 统计数据"""
    return {
        "alerts": {
            "total": 12,
            "firing": 5,
            "resolved": 7,
            "p0": 0,
            "p1": 2,
            "p2": 8,
            "p3": 2
        },
        "incidents": {
            "total": 2,
            "investigating": 1,
            "resolved": 1
        },
        "autofix": {
            "total_executions": 51,
            "success": 48,
            "failed": 3,
            "success_rate": 94.1
        },
        "availability": {
            "today": 99.9,
            "this_week": 99.95,
            "this_month": 99.9
        }
    }

@app.get("/api/alerts")
async def get_alerts(
    status: str = None,
    severity: str = None,
    limit: int = 50
):
    """获取告警列表"""
    alerts = mock_alerts
    
    # 过滤
    if status:
        alerts = [a for a in alerts if a["status"] == status]
    if severity:
        alerts = [a for a in alerts if a["severity"] == severity]
    
    # 排序
    alerts = sorted(alerts, key=lambda x: x["starts_at"], reverse=True)
    
    # 限制数量
    return {"alerts": alerts[:limit], "total": len(alerts)}

@app.get("/api/alerts/{alert_id}")
async def get_alert(alert_id: str):
    """获取告警详情"""
    for alert in mock_alerts:
        if alert["id"] == alert_id:
            return alert
    return {"error": "告警不存在"}

@app.post("/api/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str):
    """确认告警"""
    return {
        "success": True,
        "message": f"告警 {alert_id} 已确认"
    }

@app.get("/api/incidents")
async def get_incidents(
    status: str = None,
    severity: str = None,
    limit: int = 50
):
    """获取故障列表"""
    incidents = mock_incidents
    
    if status:
        incidents = [i for i in incidents if i["status"] == status]
    if severity:
        incidents = [i for i in incidents if i["severity"] == severity]
    
    incidents = sorted(incidents, key=lambda x: x["created_at"], reverse=True)
    
    return {"incidents": incidents[:limit], "total": len(incidents)}

@app.get("/api/incidents/{incident_id}")
async def get_incident(incident_id: str):
    """获取故障详情"""
    for incident in mock_incidents:
        if incident["id"] == incident_id:
            return incident
    return {"error": "故障不存在"}

@app.get("/api/runbooks")
async def get_runbooks():
    """获取预案列表"""
    return {"runbooks": mock_runbooks, "total": len(mock_runbooks)}

@app.get("/api/runbooks/{runbook_id}")
async def get_runbook(runbook_id: str):
    """获取预案详情"""
    for runbook in mock_runbooks:
        if runbook["id"] == runbook_id:
            return runbook
    return {"error": "预案不存在"}

@app.post("/api/runbooks/{runbook_id}/execute")
async def execute_runbook(runbook_id: str, params: dict = None):
    """执行预案"""
    return {
        "success": True,
        "message": f"预案 {runbook_id} 执行成功",
        "execution_id": "exec-" + datetime.now().strftime("%Y%m%d%H%M%S")
    }

@app.get("/api/metrics/cpu")
async def get_cpu_metrics():
    """获取 CPU 指标"""
    return {
        "current": 45.2,
        "trend": [42, 43, 45, 48, 45, 42, 40, 38, 42, 45],
        "unit": "%"
    }

@app.get("/api/metrics/memory")
async def get_memory_metrics():
    """获取内存指标"""
    return {
        "current": 62.8,
        "trend": [58, 60, 62, 65, 63, 60, 58, 57, 60, 62],
        "unit": "%"
    }

@app.get("/api/metrics/alerts")
async def get_alert_metrics():
    """获取告警指标"""
    return {
        "last_7_days": [5, 8, 3, 12, 7, 9, 5],
        "by_severity": {
            "P0": 0,
            "P1": 8,
            "P2": 25,
            "P3": 16
        }
    }

# ─────────────────────────────────────────────────────
# WebSocket 路由
# ─────────────────────────────────────────────────────

@app.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    """告警实时推送"""
    await manager.connect(websocket)
    try:
        while True:
            # 保持连接
            data = await websocket.receive_text()
            # 可以处理客户端消息
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# ─────────────────────────────────────────────────────
# 主入口
# ─────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
