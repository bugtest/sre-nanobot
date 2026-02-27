"""
Incident Agent - 故障分析和根因定位 Agent
"""

from typing import Any, Optional, List, Dict
from .base import SREAgent, TaskResult
from datetime import datetime
import json


class IncidentAgent(SREAgent):
    """故障分析和根因定位 Agent"""
    
    name = "incident_agent"
    description = "负责故障分析、根因定位、影响面评估和故障报告生成"
    
    system_prompt = """
    你是 SRE 故障分析专家，负责：
    - 告警关联分析
    - 根因定位（RCA）
    - 影响面评估
    - 故障报告生成
    
    分析方法：
    1. 收集所有相关告警和指标
    2. 分析时间线，找出最早发生的问题
    3. 识别因果关系
    4. 定位根本原因
    5. 评估影响范围
    6. 生成修复建议
    
    输出要求：
    - 清晰的问题描述
    - 详细的时间线
    - 根因分析（5 Whys）
    - 影响面评估
    - 修复建议
    - 后续改进措施
    """
    
    tools = [
        "analyze_incident",
        "correlate_alerts",
        "build_timeline",
        "identify_root_cause",
        "assess_impact",
        "generate_report",
        "query_related_metrics",
        "analyze_logs",
        "check_dependencies",
        "recommend_actions"
    ]
    
    requires_approval = False
    
    # 故障模式库
    INCIDENT_PATTERNS = {
        "cascade_failure": {
            "name": "级联故障",
            "description": "一个服务故障导致依赖服务连锁故障",
            "indicators": ["多个服务同时告警", "依赖关系链", "时间顺序"],
            "actions": ["隔离故障服务", "恢复依赖服务", "检查健康检查"]
        },
        "resource_exhaustion": {
            "name": "资源耗尽",
            "description": "CPU/内存/磁盘等资源耗尽导致服务不可用",
            "indicators": ["资源使用率告警", "OOMKilled", "磁盘满"],
            "actions": ["扩容", "清理资源", "优化资源使用"]
        },
        "network_issue": {
            "name": "网络问题",
            "description": "网络连接问题导致服务间通信失败",
            "indicators": ["连接超时", "DNS 解析失败", "网络延迟高"],
            "actions": ["检查网络配置", "检查 DNS", "检查防火墙"]
        },
        "deployment_issue": {
            "name": "部署问题",
            "description": "新部署导致的问题",
            "indicators": ["部署后告警", "版本变更", "配置变更"],
            "actions": ["回滚", "检查变更", "修复配置"]
        },
        "dependency_failure": {
            "name": "依赖服务故障",
            "description": "外部依赖服务故障导致的问题",
            "indicators": ["数据库连接失败", "API 调用失败", "第三方服务不可用"],
            "actions": ["检查依赖状态", "启用降级", "联系依赖团队"]
        }
    }
    
    def __init__(self):
        super().__init__()
        self.mcp_client = None
        self.incident_history = []
    
    async def initialize(self) -> None:
        """初始化 Incident Agent"""
        await super().initialize()
        self.mcp_client = await self._init_mcp_client()
    
    async def _init_mcp_client(self):
        """初始化 MCP 客户端"""
        # TODO: 实现 MCP 客户端连接
        return None
    
    async def execute(self, task: dict) -> TaskResult:
        """执行故障分析任务"""
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
            "analyze_incident": self._analyze_incident,
            "correlate_alerts": self._correlate_alerts,
            "build_timeline": self._build_timeline,
            "identify_root_cause": self._identify_root_cause,
            "assess_impact": self._assess_impact,
            "generate_report": self._generate_report,
            "query_related_metrics": self._query_related_metrics,
            "analyze_logs": self._analyze_logs,
            "check_dependencies": self._check_dependencies,
            "recommend_actions": self._recommend_actions,
        }
        
        handler = action_map.get(action)
        if not handler:
            raise ValueError(f"未知操作：{action}")
        
        return await handler(params)
    
    # ─────────────────────────────────────────────────────────
    # 核心分析方法
    # ─────────────────────────────────────────────────────────
    
    async def _analyze_incident(self, params: dict) -> dict:
        """分析故障（主入口）"""
        alerts = params.get("alerts", [])
        start_time = params.get("start_time")
        end_time = params.get("end_time")
        
        # 1. 告警关联
        correlation = await self._correlate_alerts({"alerts": alerts})
        
        # 2. 构建时间线
        timeline = await self._build_timeline({"alerts": alerts, "start_time": start_time})
        
        # 3. 根因分析
        root_cause = await self._identify_root_cause({
            "correlation": correlation,
            "timeline": timeline
        })
        
        # 4. 影响面评估
        impact = await self._assess_impact({
            "alerts": alerts,
            "root_cause": root_cause
        })
        
        # 5. 生成建议
        recommendations = await self._recommend_actions({
            "root_cause": root_cause,
            "impact": impact
        })
        
        # 6. 生成报告
        report = await self._generate_report({
            "incident_id": params.get("incident_id", "INC-UNKNOWN"),
            "alerts": alerts,
            "timeline": timeline,
            "root_cause": root_cause,
            "impact": impact,
            "recommendations": recommendations
        })
        
        # 保存历史记录
        self.incident_history.append({
            "id": params.get("incident_id"),
            "timestamp": datetime.now().isoformat(),
            "summary": report.get("summary")
        })
        
        return report
    
    async def _correlate_alerts(self, params: dict) -> dict:
        """关联告警"""
        alerts = params.get("alerts", [])
        
        # 按时间排序
        sorted_alerts = sorted(
            alerts,
            key=lambda x: x.get("starts_at", "")
        )
        
        # 按服务分组
        by_service = {}
        for alert in alerts:
            service = alert.get("labels", {}).get("service", "unknown")
            if service not in by_service:
                by_service[service] = []
            by_service[service].append(alert)
        
        # 按严重性分组
        by_severity = {}
        for alert in alerts:
            severity = alert.get("labels", {}).get("severity", "P2")
            if severity not in by_severity:
                by_severity[severity] = []
            by_severity[severity].append(alert)
        
        # 识别告警组
        groups = []
        for service, service_alerts in by_service.items():
            groups.append({
                "service": service,
                "count": len(service_alerts),
                "severities": list(set(a.get("labels", {}).get("severity", "P2") for a in service_alerts)),
                "first_alert": min(a.get("starts_at", "") for a in service_alerts),
                "alerts": service_alerts
            })
        
        return {
            "total_alerts": len(alerts),
            "services_affected": len(by_service),
            "groups": groups,
            "by_severity": by_severity,
            "time_span": self._calculate_time_span(sorted_alerts)
        }
    
    async def _build_timeline(self, params: dict) -> list:
        """构建故障时间线"""
        alerts = params.get("alerts", [])
        
        events = []
        for alert in alerts:
            # 告警触发
            events.append({
                "time": alert.get("starts_at"),
                "type": "alert_fired",
                "description": f"告警触发：{alert.get('labels', {}).get('alertname')}",
                "severity": alert.get("labels", {}).get("severity", "P2"),
                "details": alert
            })
            
            # 告警恢复（如果有）
            if alert.get("ends_at"):
                events.append({
                    "time": alert.get("ends_at"),
                    "type": "alert_resolved",
                    "description": f"告警恢复：{alert.get('labels', {}).get('alertname')}",
                    "severity": alert.get("labels", {}).get("severity", "P2"),
                    "details": alert
                })
        
        # 按时间排序（处理 None 值）
        events.sort(key=lambda x: x.get("time") or "")
        
        return events
    
    async def _identify_root_cause(self, params: dict) -> dict:
        """识别根因"""
        correlation = params.get("correlation", {})
        timeline = params.get("timeline", [])
        
        # 找出最早的告警
        first_alert = None
        if timeline:
            for event in timeline:
                if event.get("type") == "alert_fired":
                    first_alert = event
                    break
        
        # 分析故障模式
        pattern = self._match_incident_pattern(correlation, timeline)
        
        # 5 Whys 分析
        five_whys = await self._five_whys_analysis(first_alert, pattern)
        
        # 根因假设
        hypotheses = []
        if pattern:
            hypotheses.append({
                "cause": pattern["name"],
                "confidence": 0.8,
                "evidence": pattern["indicators"],
                "description": pattern["description"]
            })
        
        return {
            "first_alert": first_alert,
            "pattern": pattern,
            "five_whys": five_whys,
            "hypotheses": hypotheses,
            "most_likely": hypotheses[0] if hypotheses else None
        }
    
    def _match_incident_pattern(self, correlation: dict, timeline: list) -> Optional[dict]:
        """匹配故障模式"""
        # 检查级联故障
        if correlation.get("services_affected", 0) > 2:
            return self.INCIDENT_PATTERNS["cascade_failure"]
        
        # 检查资源耗尽
        for alert in correlation.get("groups", []):
            for a in alert.get("alerts", []):
                name = a.get("labels", {}).get("alertname", "").lower()
                if "cpu" in name or "memory" in name or "disk" in name:
                    return self.INCIDENT_PATTERNS["resource_exhaustion"]
        
        # 检查部署问题
        for event in timeline:
            if event.get("description") and "deploy" in event.get("description", "").lower():
                return self.INCIDENT_PATTERNS["deployment_issue"]
        
        return None
    
    async def _five_whys_analysis(self, first_alert: dict, pattern: dict) -> list:
        """5 Whys 分析"""
        whys = []
        
        if not first_alert:
            return whys
        
        alert_name = first_alert.get("details", {}).get("labels", {}).get("alertname", "Unknown")
        
        # Why 1
        whys.append({
            "why": 1,
            "question": f"为什么发生 {alert_name}？",
            "answer": f"服务出现异常（根据告警信息）"
        })
        
        # Why 2
        whys.append({
            "why": 2,
            "question": "为什么服务会出现异常？",
            "answer": pattern["description"] if pattern else "需要进一步调查"
        })
        
        # Why 3-5（需要更多上下文）
        for i in range(3, 6):
            whys.append({
                "why": i,
                "question": f"为什么会出现这个问题？",
                "answer": "需要人工深入分析"
            })
        
        return whys
    
    async def _assess_impact(self, params: dict) -> dict:
        """评估影响面"""
        alerts = params.get("alerts", [])
        root_cause = params.get("root_cause", {})
        
        # 受影响的服务
        services = set()
        for alert in alerts:
            service = alert.get("labels", {}).get("service")
            if service:
                services.add(service)
        
        # 受影响的命名空间
        namespaces = set()
        for alert in alerts:
            ns = alert.get("labels", {}).get("namespace")
            if ns:
                namespaces.add(ns)
        
        # 严重性统计
        severity_count = {}
        for alert in alerts:
            sev = alert.get("labels", {}).get("severity", "P2")
            severity_count[sev] = severity_count.get(sev, 0) + 1
        
        # 用户影响评估
        user_impact = self._assess_user_impact(alerts, services)
        
        return {
            "services_affected": list(services),
            "namespaces_affected": list(namespaces),
            "alert_count": len(alerts),
            "severity_breakdown": severity_count,
            "user_impact": user_impact,
            "business_impact": self._assess_business_impact(user_impact)
        }
    
    def _assess_user_impact(self, alerts: list, services: list) -> dict:
        """评估用户影响"""
        # 简单启发式评估
        high_severity = sum(1 for a in alerts if a.get("labels", {}).get("severity") in ["P0", "P1"])
        
        if high_severity > 0:
            return {
                "level": "high",
                "description": "大量用户可能受到影响",
                "affected_percentage": "10-100%"
            }
        elif len(services) > 2:
            return {
                "level": "medium",
                "description": "部分用户可能受到影响",
                "affected_percentage": "1-10%"
            }
        else:
            return {
                "level": "low",
                "description": "少数用户可能受到影响",
                "affected_percentage": "<1%"
            }
    
    def _assess_business_impact(self, user_impact: dict) -> str:
        """评估业务影响"""
        level = user_impact.get("level", "low")
        
        if level == "high":
            return "严重 - 可能导致收入损失或声誉损害"
        elif level == "medium":
            return "中等 - 可能影响用户体验"
        else:
            return "轻微 - 影响有限"
    
    def _match_runbook(self, alert_name: str) -> Optional[str]:
        """匹配预案"""
        runbook_map = {
            "PodCrashLooping": "pod_restart",
            "HighCPUUsage": "scale_up",
            "HighMemoryUsage": "scale_up",
            "ServiceUnavailable": "rollback",
            "HighErrorRate": "rollback"
        }
        
        for key, runbook in runbook_map.items():
            if key.lower() in alert_name.lower():
                return runbook
        
        return None
    
    async def _recommend_actions(self, params: dict) -> list:
        """生成修复建议"""
        root_cause = params.get("root_cause", {})
        impact = params.get("impact", {})
        
        recommendations = []
        
        # 立即行动
        recommendations.append({
            "priority": "P0",
            "type": "immediate",
            "action": "确认故障范围和影响",
            "details": "通知相关人员，建立作战室"
        })
        
        # 根据根因推荐
        pattern = root_cause.get("pattern")
        if pattern:
            for action in pattern.get("actions", []):
                recommendations.append({
                    "priority": "P1",
                    "type": "fix",
                    "action": action,
                    "details": f"针对{pattern['name']}的标准处理流程"
                })
        
        # 恢复建议
        recommendations.append({
            "priority": "P1",
            "type": "recovery",
            "action": "执行修复操作",
            "details": "根据预案执行修复"
        })
        
        # 验证建议
        recommendations.append({
            "priority": "P2",
            "type": "verification",
            "action": "验证修复效果",
            "details": "确认指标恢复正常，告警清除"
        })
        
        # 后续改进
        recommendations.append({
            "priority": "P3",
            "type": "followup",
            "action": "编写故障报告",
            "details": "记录根因、时间线、改进措施"
        })
        
        return recommendations
    
    async def _generate_report(self, params: dict) -> dict:
        """生成故障报告"""
        incident_id = params.get("incident_id", "INC-UNKNOWN")
        timeline = params.get("timeline", [])
        root_cause = params.get("root_cause", {})
        impact = params.get("impact", {})
        recommendations = params.get("recommendations", [])
        
        # 计算持续时间
        duration = self._calculate_duration(timeline)
        
        report = {
            "incident_id": incident_id,
            "summary": self._generate_summary(root_cause, impact),
            "severity": self._determine_severity(impact),
            "status": "investigating",
            "timeline": timeline,
            "root_cause": {
                "hypothesis": root_cause.get("most_likely"),
                "five_whys": root_cause.get("five_whys", []),
                "confidence": "需要进一步验证"
            },
            "impact": impact,
            "actions": recommendations,
            "duration": duration,
            "next_steps": [
                "继续监控相关指标",
                "执行修复操作",
                "更新故障状态"
            ]
        }
        
        return report
    
    def _generate_summary(self, root_cause: dict, impact: dict) -> str:
        """生成故障摘要"""
        pattern = root_cause.get("pattern", {})
        pattern_name = pattern.get("name", "未知故障类型")
        
        services = impact.get("services_affected", [])
        user_impact = impact.get("user_impact", {}).get("level", "unknown")
        
        return f"发生{pattern_name}，影响{len(services)}个服务，用户影响程度：{user_impact}"
    
    def _determine_severity(self, impact: dict) -> str:
        """确定故障严重性"""
        severity_breakdown = impact.get("severity_breakdown", {})
        
        if severity_breakdown.get("P0", 0) > 0:
            return "P0"
        elif severity_breakdown.get("P1", 0) > 0:
            return "P1"
        elif severity_breakdown.get("P2", 0) > 0:
            return "P2"
        else:
            return "P3"
    
    def _calculate_time_span(self, alerts: list) -> str:
        """计算时间跨度"""
        if not alerts:
            return "N/A"
        
        times = [a.get("starts_at", "") for a in alerts if a.get("starts_at")]
        if not times:
            return "N/A"
        
        return f"{min(times)} - {max(times)}"
    
    def _calculate_duration(self, timeline: list) -> str:
        """计算故障持续时间"""
        if not timeline:
            return "N/A"
        
        start_time = None
        end_time = None
        
        for event in timeline:
            if event.get("type") == "alert_fired" and not start_time:
                start_time = event.get("time")
            if event.get("type") == "alert_resolved":
                end_time = event.get("time")
        
        if start_time and end_time:
            # 简化处理，实际需要计算时间差
            return f"{start_time} - {end_time}"
        elif start_time:
            return f"从 {start_time} 至今"
        else:
            return "N/A"
    
    # ─────────────────────────────────────────────────────────
    # 辅助方法
    # ─────────────────────────────────────────────────────────
    
    async def _query_related_metrics(self, params: dict) -> list:
        """查询相关指标"""
        # TODO: 调用 Monitor Agent 查询指标
        return [
            {"name": "cpu_usage", "query": "up"},
            {"name": "memory_usage", "query": "up"},
            {"name": "error_rate", "query": "up"}
        ]
    
    async def _analyze_logs(self, params: dict) -> dict:
        """分析日志"""
        # TODO: 调用日志分析工具
        return {
            "error_count": 0,
            "patterns": [],
            "anomalies": []
        }
    
    async def _check_dependencies(self, params: dict) -> list:
        """检查依赖"""
        # TODO: 调用拓扑分析工具
        return [
            {"service": "database", "status": "healthy"},
            {"service": "cache", "status": "healthy"}
        ]
    
    async def validate(self, task: dict) -> tuple[bool, Optional[str]]:
        """验证任务参数"""
        action = task.get("action")
        params = task.get("params", {})
        
        if not action:
            return False, "缺少 action 参数"
        
        if action == "analyze_incident":
            if "alerts" not in params:
                return False, "缺少 alerts 参数"
        
        return True, None
    
    def get_status(self) -> dict:
        """获取 Agent 状态"""
        base_status = super().get_status()
        base_status.update({
            "incident_count": len(self.incident_history),
            "patterns_loaded": len(self.INCIDENT_PATTERNS)
        })
        return base_status
