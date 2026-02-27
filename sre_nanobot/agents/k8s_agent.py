"""
K8s Agent - Kubernetes 集群管理 Agent
"""

from typing import Any, Optional
from .base import SREAgent, TaskResult
import json


class K8sAgent(SREAgent):
    """Kubernetes 管理 Agent"""
    
    name = "k8s_agent"
    description = "负责 Kubernetes 集群操作，包括 Pod/Deployment 管理、扩缩容、日志查看等"
    
    system_prompt = """
    你是 K8s 运维专家，负责 Kubernetes 集群的日常操作。
    
    职责：
    - Pod/Deployment 状态查看
    - 服务重启、扩缩容
    - 日志查看和故障排查
    - 资源使用监控
    
    操作原则：
    1. 生产环境操作前必须确认影响范围
    2. 重启/扩缩容需要说明原因
    3. 优先使用只读操作诊断问题
    4. 发现异常及时报告
    
    安全边界：
    - ✅ 允许：查看、日志、描述
    - ⚠️ 审批：生产重启、扩缩容>10
    - ❌ 禁止：删除、修改配置、访问 kube-system
    """
    
    tools = [
        "kubectl_get_pods",
        "kubectl_get_deployments",
        "kubectl_get_services",
        "kubectl_get_events",
        "kubectl_get_nodes",
        "kubectl_get_logs",
        "kubectl_describe_pod",
        "kubectl_describe_node",
        "kubectl_restart_deployment",
        "kubectl_scale_deployment",
        "kubectl_get_resource_usage"
    ]
    
    requires_approval = True
    approval_level = "medium"
    
    # 生产环境命名空间列表
    production_namespaces = ["production", "prod", "live"]
    
    # 需要审批的操作
    sensitive_actions = ["restart", "scale"]
    
    def __init__(self):
        super().__init__()
        self.mcp_client = None
    
    async def initialize(self) -> None:
        """初始化 K8s Agent"""
        await super().initialize()
        # 这里可以初始化 MCP 客户端连接
        self.mcp_client = await self._init_mcp_client()
    
    async def _init_mcp_client(self):
        """初始化 MCP 客户端"""
        # TODO: 实现 MCP 客户端连接
        # 这里会连接到 k8s MCP 服务器
        return None
    
    async def execute(self, task: dict) -> TaskResult:
        """
        执行 K8s 任务
        
        Args:
            task: {
                "action": "get_pods" | "restart" | "scale" | ...,
                "params": {...}
            }
        
        Returns:
            TaskResult
        """
        action = task.get("action")
        params = task.get("params", {})
        
        # 验证参数
        is_valid, error = await self.validate(task)
        if not is_valid:
            return TaskResult(success=False, error=error)
        
        # 检查是否需要审批
        if self._needs_approval(action, params):
            approval = await self._request_approval(action, params)
            if not approval:
                return TaskResult(
                    success=False,
                    error="操作未获得审批"
                )
        
        # 执行操作
        try:
            result = await self._execute_action(action, params)
            return TaskResult(
                success=True,
                output=result,
                metadata={
                    "action": action,
                    "params": params
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
        
        # TODO: 通过 MCP 客户端调用工具
        # 这里是伪代码示例
        
        action_map = {
            "get_pods": self._get_pods,
            "get_deployments": self._get_deployments,
            "get_services": self._get_services,
            "get_events": self._get_events,
            "get_nodes": self._get_nodes,
            "get_logs": self._get_logs,
            "describe_pod": self._describe_pod,
            "describe_node": self._describe_node,
            "restart_deployment": self._restart_deployment,
            "scale_deployment": self._scale_deployment,
            "get_resource_usage": self._get_resource_usage,
        }
        
        handler = action_map.get(action)
        if not handler:
            raise ValueError(f"未知操作：{action}")
        
        return await handler(params)
    
    async def _get_pods(self, params: dict) -> str:
        """获取 Pod 列表"""
        namespace = params.get("namespace", "default")
        label_selector = params.get("label_selector")
        
        # TODO: 调用 MCP 工具
        return f"[MCP] get_pods namespace={namespace} selector={label_selector}"
    
    async def _get_deployments(self, params: dict) -> str:
        """获取 Deployment 列表"""
        namespace = params.get("namespace", "default")
        # TODO: 调用 MCP 工具
        return f"[MCP] get_deployments namespace={namespace}"
    
    async def _get_services(self, params: dict) -> str:
        """获取 Service 列表"""
        namespace = params.get("namespace", "default")
        # TODO: 调用 MCP 工具
        return f"[MCP] get_services namespace={namespace}"
    
    async def _get_events(self, params: dict) -> str:
        """获取事件"""
        namespace = params.get("namespace", "default")
        # TODO: 调用 MCP 工具
        return f"[MCP] get_events namespace={namespace}"
    
    async def _get_nodes(self, params: dict) -> str:
        """获取 Node 列表"""
        # TODO: 调用 MCP 工具
        return "[MCP] get_nodes"
    
    async def _get_logs(self, params: dict) -> str:
        """获取日志"""
        namespace = params.get("namespace")
        pod = params.get("pod")
        # TODO: 调用 MCP 工具
        return f"[MCP] get_logs namespace={namespace} pod={pod}"
    
    async def _describe_pod(self, params: dict) -> str:
        """描述 Pod"""
        namespace = params.get("namespace")
        pod = params.get("pod")
        # TODO: 调用 MCP 工具
        return f"[MCP] describe_pod namespace={namespace} pod={pod}"
    
    async def _describe_node(self, params: dict) -> str:
        """描述 Node"""
        node = params.get("node")
        # TODO: 调用 MCP 工具
        return f"[MCP] describe_node node={node}"
    
    async def _restart_deployment(self, params: dict) -> str:
        """重启 Deployment"""
        namespace = params.get("namespace")
        deployment = params.get("deployment")
        # TODO: 调用 MCP 工具
        return f"[MCP] restart_deployment namespace={namespace} deployment={deployment}"
    
    async def _scale_deployment(self, params: dict) -> str:
        """扩缩容 Deployment"""
        namespace = params.get("namespace")
        deployment = params.get("deployment")
        replicas = params.get("replicas")
        # TODO: 调用 MCP 工具
        return f"[MCP] scale_deployment namespace={namespace} deployment={deployment} replicas={replicas}"
    
    async def _get_resource_usage(self, params: dict) -> str:
        """获取资源使用"""
        namespace = params.get("namespace", "default")
        # TODO: 调用 MCP 工具
        return f"[MCP] get_resource_usage namespace={namespace}"
    
    def _needs_approval(self, action: str, params: dict) -> bool:
        """检查是否需要审批"""
        
        # 只读操作不需要审批
        read_actions = ["get_pods", "get_deployments", "get_services", 
                       "get_events", "get_nodes", "get_logs", 
                       "describe_pod", "describe_node", "get_resource_usage"]
        if action in read_actions:
            return False
        
        # 生产环境操作需要审批
        namespace = params.get("namespace", "")
        if namespace in self.production_namespaces:
            return True
        
        # 扩缩容超过 10 副本需要审批
        if action == "scale_deployment":
            replicas = params.get("replicas", 0)
            if replicas > 10 or replicas == 0:
                return True
        
        return False
    
    async def _request_approval(self, action: str, params: dict) -> bool:
        """请求审批"""
        # TODO: 实现审批流程（飞书/钉钉通知）
        # 这里简化为自动批准
        print(f"⚠️ 需要审批：{action} params={params}")
        return True
    
    async def validate(self, task: dict) -> tuple[bool, Optional[str]]:
        """验证任务参数"""
        action = task.get("action")
        params = task.get("params", {})
        
        if not action:
            return False, "缺少 action 参数"
        
        # 检查必需参数
        if action in ["get_pods", "get_deployments", "get_services", "get_events"]:
            if "namespace" not in params:
                return False, "缺少 namespace 参数"
        
        if action == "restart_deployment":
            if not all(k in params for k in ["namespace", "deployment"]):
                return False, "缺少 namespace 或 deployment 参数"
        
        if action == "scale_deployment":
            required = ["namespace", "deployment", "replicas"]
            if not all(k in params for k in required):
                return False, f"缺少必需参数：{required}"
            if not isinstance(params.get("replicas"), int):
                return False, "replicas 必须是整数"
            if params.get("replicas", 0) < 0:
                return False, "replicas 不能小于 0"
        
        if action == "get_logs":
            if not all(k in params for k in ["namespace", "pod"]):
                return False, "缺少 namespace 或 pod 参数"
        
        return True, None
    
    def get_status(self) -> dict:
        """获取 Agent 状态"""
        base_status = super().get_status()
        base_status.update({
            "production_namespaces": self.production_namespaces,
            "mcp_connected": self.mcp_client is not None
        })
        return base_status
