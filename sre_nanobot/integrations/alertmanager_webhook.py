"""
Alertmanager Webhook 接收器

接收 Prometheus Alertmanager 发送的告警 Webhook
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────
# 数据模型
# ─────────────────────────────────────────────────────────────

class AlertLabel(BaseModel):
    """告警标签"""
    alertname: str
    severity: Optional[str] = None
    instance: Optional[str] = None
    job: Optional[str] = None
    namespace: Optional[str] = None
    pod: Optional[str] = None
    service: Optional[str] = None
    additional_labels: Dict[str, str] = {}


class AlertAnnotation(BaseModel):
    """告警注解"""
    summary: Optional[str] = None
    description: Optional[str] = None
    runbook_url: Optional[str] = None


class Alert(BaseModel):
    """告警对象"""
    status: str  # firing or resolved
    labels: Dict[str, str]
    annotations: Dict[str, str]
    startsAt: datetime
    endsAt: Optional[datetime] = None
    generatorURL: Optional[str] = None
    fingerprint: str


class AlertGroup(BaseModel):
    """告警组"""
    status: str
    receiver: str
    groupKey: str
    groupLabels: Dict[str, str]
    commonLabels: Dict[str, str]
    commonAnnotations: Dict[str, str]
    externalURL: str
    version: str
    alerts: List[Alert]


# ─────────────────────────────────────────────────────────────
# Webhook 处理器
# ─────────────────────────────────────────────────────────────

class AlertmanagerWebhook:
    """Alertmanager Webhook 处理器"""
    
    def __init__(self):
        self.alert_handlers = []
        self.app = FastAPI(title="SRE Alert Webhook")
        self._setup_routes()
    
    def _setup_routes(self):
        """设置路由"""
        
        @self.app.post("/api/v1/alerts")
        async def receive_alerts(alert_group: AlertGroup):
            """接收告警"""
            logger.info(f"收到告警组：{alert_group.groupKey}")
            logger.info(f"告警数量：{len(alert_group.alerts)}")
            logger.info(f"状态：{alert_group.status}")
            
            # 处理每个告警
            results = []
            for alert in alert_group.alerts:
                result = await self._process_alert(alert, alert_group)
                results.append(result)
            
            return {
                "status": "success",
                "received": len(alert_group.alerts),
                "processed": len(results)
            }
        
        @self.app.get("/health")
        async def health_check():
            """健康检查"""
            return {"status": "healthy"}
        
        @self.app.get("/metrics")
        async def get_metrics():
            """获取统计信息"""
            return {
                "handlers": len(self.alert_handlers),
                "status": "running"
            }
    
    async def _process_alert(self, alert: Alert, group: AlertGroup) -> dict:
        """处理单个告警"""
        
        # 提取关键信息
        alert_info = {
            "name": alert.labels.get("alertname", "Unknown"),
            "status": alert.status,
            "severity": alert.labels.get("severity", "P2"),
            "instance": alert.labels.get("instance", "N/A"),
            "namespace": alert.labels.get("namespace", "N/A"),
            "pod": alert.labels.get("pod", "N/A"),
            "service": alert.labels.get("service", "N/A"),
            "summary": alert.annotations.get("summary", "N/A"),
            "description": alert.annotations.get("description", "N/A"),
            "starts_at": alert.startsAt.isoformat(),
            "fingerprint": alert.fingerprint
        }
        
        logger.info(f"处理告警：{alert_info['name']} - {alert_info['severity']}")
        
        # 调用注册的处理器
        results = []
        for handler in self.alert_handlers:
            try:
                result = await handler(alert_info, group)
                results.append(result)
            except Exception as e:
                logger.error(f"告警处理器错误：{e}")
                results.append({"error": str(e)})
        
        return {
            "alert": alert_info,
            "handlers": results
        }
    
    def register_handler(self, handler):
        """注册告警处理器"""
        self.alert_handlers.append(handler)
        logger.info(f"注册告警处理器：{handler.__name__}")
    
    def run(self, host: str = "0.0.0.0", port: int = 8080):
        """运行 Webhook 服务器"""
        import uvicorn
        uvicorn.run(self.app, host=host, port=port)


# ─────────────────────────────────────────────────────────────
# 示例处理器
# ─────────────────────────────────────────────────────────────

async def log_alert_handler(alert: dict, group: AlertGroup) -> dict:
    """日志记录处理器"""
    logger.info(f"""
═══════════════════════════════════════════════════════════
告警详情:
  名称：{alert['name']}
  状态：{alert['status']}
  级别：{alert['severity']}
  实例：{alert['instance']}
  命名空间：{alert['namespace']}
  摘要：{alert['summary']}
  开始时间：{alert['starts_at']}
═══════════════════════════════════════════════════════════
""")
    return {"action": "logged"}


async def notify_handler(alert: dict, group: AlertGroup) -> dict:
    """通知处理器（示例）"""
    # TODO: 集成飞书/钉钉通知
    severity = alert['severity']
    
    if severity in ["P0", "P1"]:
        # 高级别告警需要立即通知
        logger.warning(f"🚨 高级别告警：{alert['name']} - 需要立即处理")
        # await send_feishu_notification(alert)
        # await send_dingtalk_notification(alert)
    
    return {"action": "notified", "severity": severity}


# ─────────────────────────────────────────────────────────────
# 主入口
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    webhook = AlertmanagerWebhook()
    
    # 注册处理器
    webhook.register_handler(log_alert_handler)
    webhook.register_handler(notify_handler)
    
    # 启动服务
    print("🚀 启动 Alertmanager Webhook 服务器...")
    print("📡 Webhook 地址：http://localhost:8080/api/v1/alerts")
    print("❤️  健康检查：http://localhost:8080/health")
    
    webhook.run()
