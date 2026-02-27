"""
Monitor Agent - 监控和告警 Agent
"""

from typing import Any, Optional
from .base import SREAgent, TaskResult
from datetime import datetime


class MonitorAgent(SREAgent):
    """监控和告警 Agent"""
    
    name = "monitor_agent"
    description = "负责监控指标查询、告警接收和分析"
    
    system_prompt = """
    你是 SRE 监控专家，负责：
    - Prometheus 指标查询
    - 告警接收和分析
    - 监控数据可视化
    - 异常检测
    
    工作原则：
    1. 快速响应告警
    2. 准确识别异常
    3. 提供详细上下文
    4. 关联相关指标
    """
    
    tools = [
        "prom_query",
        "prom_query_range",
        "prom_get_alerts",
        "prom_get_rules",
        "prom_get_targets",
        "prom_node_cpu_usage",
        "prom_node_memory_usage",
        "prom_pod_cpu_usage",
        "prom_pod_memory_usage",
        "prom_service_latency",
        "prom_service_error_rate"
    ]
    
    requires_approval = False
    
    # 告警级别定义
    SEVERITY_LEVELS = {
        "P0": {"color": "🔴", "priority": 1, "notify": ["phone", "im"]},
        "P1": {"color": "🟠", "priority": 2, "notify": ["im"]},
        "P2": {"color": "🟡", "priority": 3, "notify": ["im"]},
        "P3": {"color": "🔵", "priority": 4, "notify": ["log"]}
    }
    
    def __init__(self):
        super().__init__()
        self.mcp_client = None
        self.alert_handlers = {}
    
    async def initialize(self) -> None:
        """初始化 Monitor Agent"""
        await super().initialize()
        self.mcp_client = await self._init_mcp_client()
    
    async def _init_mcp_client(self):
        """初始化 MCP 客户端"""
        # TODO: 实现 MCP 客户端连接
        return None
    
    async def execute(self, task: dict) -> TaskResult:
        """执行监控任务"""
        action = task.get("action")
        params = task.get("params", {})
        
        # 验证参数
        is_valid, error = await self.validate(task)
        if not is_valid:
            return TaskResult(success=False, error=error)
        
        try:
            result = await self._execute_action(action, params)
            return TaskResult(
                success=True,
                output=result,
                metadata={
                    "action": action,
                    "params": params,
                    "timestamp": datetime.now().isoformat()
                }
            )
        except Exception as e:
            return TaskResult(
                success=False,
                error=str(e),
                metadata={
                    "action": action,
                    "params": params
                }
            )
    
    async def _execute_action(self, action: str, params: dict) -> Any:
        """执行具体操作"""
        
        action_map = {
            "query_metrics": self._query_metrics,
            "get_alerts": self._get_alerts,
            "analyze_alert": self._analyze_alert,
            "get_node_status": self._get_node_status,
            "get_pod_status": self._get_pod_status,
            "get_service_status": self._get_service_status,
            "receive_webhook": self._receive_webhook,
        }
        
        handler = action_map.get(action)
        if not handler:
            raise ValueError(f"未知操作：{action}")
        
        return await handler(params)
    
    async def _query_metrics(self, params: dict) -> str:
        """查询指标"""
        query = params.get("query")
        # TODO: 调用 MCP 工具
        return f"[MCP] prom_query query={query}"
    
    async def _get_alerts(self, params: dict) -> str:
        """获取告警列表"""
        state = params.get("state", "firing")
        # TODO: 调用 MCP 工具
        return f"[MCP] prom_get_alerts state={state}"
    
    async def _analyze_alert(self, params: dict) -> dict:
        """分析告警"""
        alert_name = params.get("alert_name")
        labels = params.get("labels", {})
        
        # 分析步骤
        analysis = {
            "alert_name": alert_name,
            "severity": self._get_severity(labels),
            "affected_services": self._extract_services(labels),
            "related_metrics": await self._get_related_metrics(alert_name, labels),
            "suggested_actions": self._get_suggested_actions(alert_name),
            "runbook_id": self._match_runbook(alert_name)
        }
        
        return analysis
    
    async def _get_related_metrics(self, alert_name: str, labels: dict) -> list:
        """获取相关指标"""
        # TODO: 查询相关指标
        return [
            {"name": "cpu_usage", "query": "up"},
            {"name": "memory_usage", "query": "up"},
            {"name": "error_rate", "query": "up"}
        ]
    
    def _get_severity(self, labels: dict) -> str:
        """获取告警级别"""
        severity = labels.get("severity", labels.get("level", "P2"))
        return severity.upper()
    
    def _extract_services(self, labels: dict) -> list:
        """提取受影响的服务"""
        services = []
        if "service" in labels:
            services.append(labels["service"])
        if "deployment" in labels:
            services.append(labels["deployment"])
        if "pod" in labels:
            services.append(labels["pod"])
        return services
    
    def _get_suggested_actions(self, alert_name: str) -> list:
        """获取建议操作"""
        action_map = {
            "PodCrashLooping": [
                "查看 Pod 日志",
                "检查 Pod 事件",
                "检查资源限制",
                "考虑重启 Deployment"
            ],
            "HighCPUUsage": [
                "检查 CPU 使用趋势",
                "识别占用 CPU 的进程",
                "考虑扩容或优化代码"
            ],
            "HighMemoryUsage": [
                "检查内存使用趋势",
                "检查是否有内存泄漏",
                "考虑增加内存限制或扩容"
            ],
            "ServiceUnavailable": [
                "检查服务状态",
                "检查依赖服务",
                "检查网络连通性",
                "查看错误日志"
            ],
            "HighErrorRate": [
                "检查错误日志",
                "分析错误类型",
                "检查依赖服务状态",
                "考虑回滚最近变更"
            ]
        }
        
        # 模糊匹配
        for key, actions in action_map.items():
            if key.lower() in alert_name.lower():
                return actions
        
        return ["查看相关指标", "分析告警上下文", "联系值班人员"]
    
    def _match_runbook(self, alert_name: str) -> Optional[str]:
        """匹配预案"""
        runbook_map = {
            "PodCrashLooping": "pod_restart",
            "HighCPUUsage": "scale_up_or_optimize",
            "HighMemoryUsage": "restart_or_scale",
            "ServiceUnavailable": "health_check_and_restart",
            "HighErrorRate": "rollback_or_fix"
        }
        
        for key, runbook in runbook_map.items():
            if key.lower() in alert_name.lower():
                return runbook
        
        return None
    
    async def _get_node_status(self, params: dict) -> str:
        """获取节点状态"""
        node = params.get("node")
        # TODO: 调用 MCP 工具
        if node:
            return f"[MCP] 检查节点 {node} 状态"
        return "[MCP] 检查所有节点状态"
    
    async def _get_pod_status(self, params: dict) -> str:
        """获取 Pod 状态"""
        namespace = params.get("namespace")
        pod = params.get("pod")
        # TODO: 调用 MCP 工具
        return f"[MCP] 检查 Pod namespace={namespace} pod={pod}"
    
    async def _get_service_status(self, params: dict) -> str:
        """获取服务状态"""
        service = params.get("service")
        # TODO: 调用 MCP 工具
        return f"[MCP] 检查服务 {service}"
    
    async def _receive_webhook(self, params: dict) -> dict:
        """接收告警 Webhook"""
        # 解析告警
        alerts = params.get("alerts", [])
        
        processed_alerts = []
        for alert in alerts:
            processed = await self._process_single_alert(alert)
            processed_alerts.append(processed)
        
        return {
            "received": len(alerts),
            "processed": len(processed_alerts),
            "alerts": processed_alerts
        }
    
    async def _process_single_alert(self, alert: dict) -> dict:
        """处理单个告警"""
        labels = alert.get("labels", {})
        annotations = alert.get("annotations", {})
        
        return {
            "name": labels.get("alertname", "Unknown"),
            "severity": self._get_severity(labels),
            "status": alert.get("status", "firing"),
            "starts_at": alert.get("startsAt"),
            "description": annotations.get("description", "N/A"),
            "summary": annotations.get("summary", "N/A"),
            "labels": labels,
            "affected_services": self._extract_services(labels),
            "suggested_actions": self._get_suggested_actions(labels.get("alertname", "")),
            "runbook_id": self._match_runbook(labels.get("alertname", ""))
        }
    
    async def validate(self, task: dict) -> tuple[bool, Optional[str]]:
        """验证任务参数"""
        action = task.get("action")
        params = task.get("params", {})
        
        if not action:
            return False, "缺少 action 参数"
        
        # 检查特定操作的必需参数
        if action == "query_metrics":
            if "query" not in params:
                return False, "缺少 query 参数"
        
        if action == "analyze_alert":
            if "alert_name" not in params:
                return False, "缺少 alert_name 参数"
        
        return True, None
    
    def register_alert_handler(self, alert_type: str, handler):
        """注册告警处理器"""
        self.alert_handlers[alert_type] = handler
    
    async def handle_alert(self, alert: dict) -> TaskResult:
        """处理告警（外部调用）"""
        try:
            # 1. 解析告警
            parsed = await self._process_single_alert(alert)
            
            # 2. 分析告警
            analysis = await self._analyze_alert({
                "alert_name": parsed["name"],
                "labels": parsed["labels"]
            })
            
            # 3. 合并结果
            result = {**parsed, **analysis}
            
            # 4. 调用注册的处理器
            alert_type = parsed["name"]
            if alert_type in self.alert_handlers:
                handler_result = await self.alert_handlers[alert_type](result)
                result["handler_result"] = handler_result
            
            return TaskResult(success=True, output=result)
        
        except Exception as e:
            return TaskResult(success=False, error=str(e))
    
    def get_status(self) -> dict:
        """获取 Agent 状态"""
        base_status = super().get_status()
        base_status.update({
            "mcp_connected": self.mcp_client is not None,
            "alert_handlers": list(self.alert_handlers.keys())
        })
        return base_status
