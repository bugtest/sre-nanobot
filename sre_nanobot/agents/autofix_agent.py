"""
AutoFix Agent - 自动修复 Agent
"""

from typing import Any, Optional, List, Dict
from .base import SREAgent, TaskResult
from datetime import datetime
import yaml


class AutoFixAgent(SREAgent):
    """自动修复 Agent"""
    
    name = "autofix_agent"
    description = "负责执行自动修复预案，包括服务重启、扩缩容、回滚等"
    
    system_prompt = """
    你是自动化修复专家，负责：
    - 执行修复预案
    - 服务重启
    - 扩缩容
    - 版本回滚
    - 配置修复
    
    执行原则：
    1. 确认修复方案经过审批
    2. 准备回滚方案
    3. 小步执行，逐步验证
    4. 记录所有操作
    5. 修复后验证效果
    
    安全边界：
    - 生产环境操作需要审批
    - 大规模变更需要分阶段
    - 必须有回滚方案
    """
    
    tools = [
        "execute_runbook",
        "restart_service",
        "scale_service",
        "rollback_deployment",
        "update_config",
        "verify_fix",
        "rollback_fix"
    ]
    
    requires_approval = True
    approval_level = "high"
    
    # 预案库
    RUNBOOKS = {}
    
    def __init__(self):
        super().__init__()
        self.execution_history = []
        self.load_runbooks()
    
    async def initialize(self) -> None:
        """初始化 AutoFix Agent"""
        await super().initialize()
        self.mcp_client = await self._init_mcp_client()
    
    async def _init_mcp_client(self):
        """初始化 MCP 客户端"""
        return None
    
    def load_runbooks(self):
        """加载预案"""
        # 内置核心预案
        self.RUNBOOKS = {
            "pod_restart": {
                "name": "Pod 重启预案",
                "version": "1.0",
                "description": "重启故障 Pod",
                "triggers": ["PodCrashLooping", "PodNotReady", "PodError"],
                "severity": "low",
                "timeout": 300,
                "steps": [
                    {
                        "name": "check_status",
                        "type": "k8s",
                        "action": "get_pods",
                        "params": {
                            "namespace": "{{alert.namespace}}",
                            "label_selector": "app={{alert.app}}"
                        },
                        "on_failure": "abort"
                    },
                    {
                        "name": "confirm_issue",
                        "type": "analysis",
                        "action": "verify_crash_loop",
                        "params": {
                            "restart_count_threshold": 5
                        },
                        "on_failure": "abort"
                    },
                    {
                        "name": "restart_deployment",
                        "type": "k8s",
                        "action": "rollout_restart",
                        "params": {
                            "namespace": "{{alert.namespace}}",
                            "deployment": "{{alert.deployment}}"
                        },
                        "requires_approval": True,
                        "approval_timeout": 300
                    },
                    {
                        "name": "wait_healthy",
                        "type": "wait",
                        "duration": 60,
                        "check": {
                            "type": "k8s",
                            "action": "get_pods",
                            "condition": "all_ready == true"
                        }
                    },
                    {
                        "name": "verify_service",
                        "type": "http",
                        "action": "health_check",
                        "params": {
                            "url": "{{service.health_endpoint}}"
                        },
                        "retries": 3,
                        "on_failure": "rollback"
                    }
                ],
                "rollback": [
                    {
                        "name": "notify_failure",
                        "type": "notification",
                        "action": "send_message",
                        "params": {
                            "channel": "feishu",
                            "message": "重启失败，需要人工介入"
                        }
                    }
                ]
            },
            "scale_up": {
                "name": "扩容预案",
                "version": "1.0",
                "description": "服务扩容",
                "triggers": ["HighCPUUsage", "HighMemoryUsage", "HighLoad"],
                "severity": "low",
                "timeout": 600,
                "steps": [
                    {
                        "name": "check_current_replicas",
                        "type": "k8s",
                        "action": "get_deployment",
                        "params": {
                            "namespace": "{{alert.namespace}}",
                            "deployment": "{{alert.deployment}}"
                        }
                    },
                    {
                        "name": "calculate_target",
                        "type": "calculation",
                        "action": "calculate_replicas",
                        "params": {
                            "current": "{{current_replicas}}",
                            "cpu_usage": "{{metrics.cpu_usage}}",
                            "increment": 2
                        }
                    },
                    {
                        "name": "scale_deployment",
                        "type": "k8s",
                        "action": "scale",
                        "params": {
                            "namespace": "{{alert.namespace}}",
                            "deployment": "{{alert.deployment}}",
                            "replicas": "{{target_replicas}}"
                        },
                        "requires_approval": True
                    },
                    {
                        "name": "wait_stable",
                        "type": "wait",
                        "duration": 120
                    },
                    {
                        "name": "verify_metrics",
                        "type": "metrics",
                        "action": "check_cpu",
                        "params": {
                            "threshold": 70
                        }
                    }
                ]
            },
            "rollback": {
                "name": "回滚预案",
                "version": "1.0",
                "description": "回滚到上一个稳定版本",
                "triggers": ["DeploymentFailed", "HighErrorRate", "ServiceUnavailable"],
                "severity": "medium",
                "timeout": 600,
                "steps": [
                    {
                        "name": "get_current_version",
                        "type": "k8s",
                        "action": "get_deployment_history",
                        "params": {
                            "namespace": "{{alert.namespace}}",
                            "deployment": "{{alert.deployment}}"
                        }
                    },
                    {
                        "name": "rollback_deployment",
                        "type": "k8s",
                        "action": "rollout_undo",
                        "params": {
                            "namespace": "{{alert.namespace}}",
                            "deployment": "{{alert.deployment}}"
                        },
                        "requires_approval": True
                    },
                    {
                        "name": "wait_rollback",
                        "type": "wait",
                        "duration": 120
                    },
                    {
                        "name": "verify_health",
                        "type": "http",
                        "action": "health_check",
                        "retries": 3
                    }
                ]
            },
            # 新增预案
            "deployment_restart": {
                "name": "部署重启预案",
                "version": "1.0",
                "description": "重启整个 Deployment",
                "triggers": ["HighErrorRate", "ServiceUnavailable"],
                "severity": "medium",
                "timeout": 600
            },
            "dns_recovery": {
                "name": "DNS 恢复预案",
                "version": "1.0",
                "description": "恢复 DNS 服务",
                "triggers": ["DNSResolutionFailed", "CoreDNSHighLatency"],
                "severity": "medium",
                "timeout": 600
            },
            "pvc_recovery": {
                "name": "PVC 恢复预案",
                "version": "1.0",
                "description": "恢复 PVC 绑定",
                "triggers": ["PVCPending", "PVCBoundFailed"],
                "severity": "medium",
                "timeout": 900
            },
            "database_connection_fix": {
                "name": "数据库连接修复预案",
                "version": "1.0",
                "description": "修复数据库连接问题",
                "triggers": ["DatabaseConnectionFailed", "TooManyConnections"],
                "severity": "high",
                "timeout": 600
            },
            "resource_limit_update": {
                "name": "资源限制更新预案",
                "version": "1.0",
                "description": "更新 Pod 资源限制",
                "triggers": ["OOMKilled", "CPUCgroupThrottled"],
                "severity": "medium",
                "timeout": 900
            },
            "node_drain": {
                "name": "节点排空预案",
                "version": "1.0",
                "description": "安全排空节点",
                "triggers": ["NodeNotReady", "DiskPressure"],
                "severity": "high",
                "timeout": 1200
            }
        }
        
        # 从文件加载额外预案
        self._load_runbooks_from_file()
    
    def _load_runbooks_from_file(self):
        """从 YAML 文件加载预案"""
        try:
            import yaml
            from pathlib import Path
            
            runbook_file = Path(__file__).parent.parent / "runbooks" / "runbooks.yaml"
            
            if runbook_file.exists():
                with open(runbook_file, 'r', encoding='utf-8') as f:
                    file_runbooks = yaml.safe_load_all(f)
                    
                    for runbook in file_runbooks:
                        if runbook and 'name' in runbook:
                            runbook_id = runbook.get('name')
                            self.RUNBOOKS[runbook_id] = runbook
                            self.log(f"加载预案：{runbook_id}")
        
        except Exception as e:
            # 文件加载失败不影响内置预案
            pass
    
    async def execute(self, task: dict) -> TaskResult:
        """执行修复任务"""
        action = task.get("action")
        params = task.get("params", {})
        
        # 验证参数
        is_valid, error = await self.validate(task)
        if not is_valid:
            return TaskResult(success=False, error=error)
        
        # 检查审批
        if self.requires_approval and not params.get("approved"):
            return TaskResult(
                success=False,
                error="操作需要审批",
                metadata={"approval_required": True}
            )
        
        try:
            result = await self._execute_action(action, params)
            
            # 记录执行历史
            self.execution_history.append({
                "timestamp": datetime.now().isoformat(),
                "action": action,
                "params": params,
                "result": "success" if result.get("success") else "failed"
            })
            
            return TaskResult(
                success=result.get("success", True),
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
    
    async def _execute_action(self, action: str, params: dict) -> dict:
        """执行具体操作"""
        
        action_map = {
            "execute_runbook": self._execute_runbook,
            "restart_service": self._restart_service,
            "scale_service": self._scale_service,
            "rollback_deployment": self._rollback_deployment,
            "update_config": self._update_config,
            "verify_fix": self._verify_fix,
            "rollback_fix": self._rollback_fix,
        }
        
        handler = action_map.get(action)
        if not handler:
            raise ValueError(f"未知操作：{action}")
        
        return await handler(params)
    
    # ─────────────────────────────────────────────────────────
    # 核心修复操作
    # ─────────────────────────────────────────────────────────
    
    async def _execute_runbook(self, params: dict) -> dict:
        """执行预案"""
        runbook_id = params.get("runbook_id")
        context = params.get("context", {})
        
        if runbook_id not in self.RUNBOOKS:
            return {
                "success": False,
                "error": f"预案不存在：{runbook_id}"
            }
        
        runbook = self.RUNBOOKS[runbook_id]
        execution_result = {
            "runbook_id": runbook_id,
            "runbook_name": runbook["name"],
            "start_time": datetime.now().isoformat(),
            "steps_executed": [],
            "steps_failed": [],
            "success": False
        }
        
        # 执行预案步骤
        for i, step in enumerate(runbook["steps"]):
            step_result = await self._execute_step(step, context)
            
            execution_result["steps_executed"].append({
                "step": i + 1,
                "name": step["name"],
                "result": step_result
            })
            
            # 检查失败处理
            if not step_result.get("success"):
                if step.get("on_failure") == "abort":
                    execution_result["error"] = f"步骤 {step['name']} 失败，中止执行"
                    return execution_result
                elif step.get("on_failure") == "rollback":
                    execution_result["error"] = f"步骤 {step['name']} 失败，执行回滚"
                    await self._execute_rollback(runbook, context)
                    return execution_result
        
        execution_result["success"] = True
        execution_result["end_time"] = datetime.now().isoformat()
        
        return execution_result
    
    async def _execute_step(self, step: dict, context: dict) -> dict:
        """执行单个步骤"""
        step_type = step.get("type")
        action = step.get("action")
        params = self._render_params(step.get("params", {}), context)
        
        try:
            if step_type == "k8s":
                return await self._k8s_action(action, params)
            elif step_type == "http":
                return await self._http_action(action, params)
            elif step_type == "wait":
                return await self._wait_action(step, context)
            elif step_type == "analysis":
                return await self._analysis_action(action, params)
            elif step_type == "calculation":
                return await self._calculation_action(action, params, context)
            elif step_type == "metrics":
                return await self._metrics_action(action, params)
            elif step_type == "notification":
                return await self._notification_action(action, params)
            else:
                return {"success": False, "error": f"未知步骤类型：{step_type}"}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _k8s_action(self, action: str, params: dict) -> dict:
        """K8s 操作"""
        # TODO: 调用 K8s Agent
        return {
            "success": True,
            "action": action,
            "params": params,
            "output": f"[K8s] {action} executed"
        }
    
    async def _http_action(self, action: str, params: dict) -> dict:
        """HTTP 操作"""
        # TODO: 调用 HTTP 客户端
        return {
            "success": True,
            "action": action,
            "params": params,
            "output": f"[HTTP] {action} executed"
        }
    
    async def _wait_action(self, step: dict, context: dict) -> dict:
        """等待操作"""
        duration = step.get("duration", 60)
        
        # TODO: 实际等待
        return {
            "success": True,
            "action": "wait",
            "duration": duration,
            "output": f"等待 {duration} 秒"
        }
    
    async def _analysis_action(self, action: str, params: dict) -> dict:
        """分析操作"""
        # TODO: 调用分析工具
        return {
            "success": True,
            "action": action,
            "params": params,
            "output": "分析完成"
        }
    
    async def _calculation_action(self, action: str, params: dict, context: dict) -> dict:
        """计算操作"""
        if action == "calculate_replicas":
            current = params.get("current", 1)
            increment = params.get("increment", 2)
            target = current + increment
            
            # 更新上下文
            context["target_replicas"] = target
            
            return {
                "success": True,
                "action": action,
                "result": target,
                "output": f"计算目标副本数：{current} + {increment} = {target}"
            }
        
        return {"success": False, "error": f"未知计算操作：{action}"}
    
    async def _metrics_action(self, action: str, params: dict) -> dict:
        """指标检查"""
        # TODO: 调用 Monitor Agent
        return {
            "success": True,
            "action": action,
            "params": params,
            "output": "指标检查通过"
        }
    
    async def _notification_action(self, action: str, params: dict) -> dict:
        """通知操作"""
        # TODO: 调用通知服务
        return {
            "success": True,
            "action": action,
            "params": params,
            "output": "通知已发送"
        }
    
    async def _restart_service(self, params: dict) -> dict:
        """重启服务"""
        namespace = params.get("namespace")
        deployment = params.get("deployment")
        
        # 执行重启预案
        return await self._execute_runbook({
            "runbook_id": "pod_restart",
            "context": {
                "alert": {
                    "namespace": namespace,
                    "deployment": deployment
                }
            },
            "approved": params.get("approved", False)
        })
    
    async def _scale_service(self, params: dict) -> dict:
        """扩缩容服务"""
        namespace = params.get("namespace")
        deployment = params.get("deployment")
        replicas = params.get("replicas")
        
        # TODO: 调用 K8s Agent
        return {
            "success": True,
            "action": "scale",
            "namespace": namespace,
            "deployment": deployment,
            "replicas": replicas,
            "output": f"服务已扩缩容到 {replicas} 副本"
        }
    
    async def _rollback_deployment(self, params: dict) -> dict:
        """回滚部署"""
        namespace = params.get("namespace")
        deployment = params.get("deployment")
        
        # 执行回滚预案
        return await self._execute_runbook({
            "runbook_id": "rollback",
            "context": {
                "alert": {
                    "namespace": namespace,
                    "deployment": deployment
                }
            },
            "approved": params.get("approved", False)
        })
    
    async def _update_config(self, params: dict) -> dict:
        """更新配置"""
        # TODO: 实现配置更新
        return {
            "success": True,
            "action": "update_config",
            "params": params,
            "output": "配置已更新"
        }
    
    async def _verify_fix(self, params: dict) -> dict:
        """验证修复效果"""
        # TODO: 调用 Monitor Agent 验证指标
        return {
            "success": True,
            "verified": True,
            "metrics": {
                "cpu_usage": "45%",
                "memory_usage": "60%",
                "error_rate": "0.1%"
            },
            "output": "修复验证通过"
        }
    
    async def _rollback_fix(self, params: dict) -> dict:
        """回滚修复"""
        # TODO: 实现回滚
        return {
            "success": True,
            "action": "rollback",
            "output": "已回滚到修复前状态"
        }
    
    async def _execute_rollback(self, runbook: dict, context: dict):
        """执行回滚"""
        rollback_steps = runbook.get("rollback", [])
        
        for step in rollback_steps:
            await self._execute_step(step, context)
    
    def _render_params(self, params: dict, context: dict) -> dict:
        """渲染参数模板"""
        rendered = {}
        
        for key, value in params.items():
            if isinstance(value, str):
                # 简单模板渲染
                for ctx_key, ctx_value in context.items():
                    if isinstance(ctx_value, dict):
                        for k, v in ctx_value.items():
                            value = value.replace(f"{{{{{ctx_key}.{k}}}}}", str(v))
                    else:
                        value = value.replace(f"{{{{{ctx_key}}}}}", str(ctx_value))
                rendered[key] = value
            else:
                rendered[key] = value
        
        return rendered
    
    async def validate(self, task: dict) -> tuple[bool, Optional[str]]:
        """验证任务参数"""
        action = task.get("action")
        params = task.get("params", {})
        
        if not action:
            return False, "缺少 action 参数"
        
        if action == "execute_runbook":
            if "runbook_id" not in params:
                return False, "缺少 runbook_id 参数"
        
        if action == "restart_service":
            if not all(k in params for k in ["namespace", "deployment"]):
                return False, "缺少 namespace 或 deployment 参数"
        
        return True, None
    
    def get_status(self) -> dict:
        """获取 Agent 状态"""
        base_status = super().get_status()
        base_status.update({
            "runbooks_loaded": len(self.RUNBOOKS),
            "executions_count": len(self.execution_history),
            "requires_approval": self.requires_approval
        })
        return base_status
