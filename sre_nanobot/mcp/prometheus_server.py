"""
Prometheus MCP Server

提供 Prometheus 监控指标查询的 MCP 工具接口
"""

import asyncio
import httpx
from typing import Any
from datetime import datetime, timedelta
from mcp.server import Server
from mcp.types import Tool, TextContent

# 创建 MCP 服务器实例
prometheus_server = Server("sre-prometheus-mcp")

# Prometheus 服务器配置
PROMETHEUS_URL = "http://localhost:9090"


# ─────────────────────────────────────────────────────────────
# 工具定义
# ─────────────────────────────────────────────────────────────

@prometheus_server.list_tools()
async def list_tools() -> list[Tool]:
    """列出所有可用的 Prometheus 工具"""
    return [
        Tool(
            name="prom_query",
            description="执行 PromQL 查询，返回即时指标数据",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "PromQL 查询语句"
                    },
                    "time": {
                        "type": "string",
                        "description": "查询时间点（RFC3339 或 Unix 时间戳），默认当前时间"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="prom_query_range",
            description="执行 PromQL 范围查询，返回时间序列数据",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "PromQL 查询语句"
                    },
                    "start": {
                        "type": "string",
                        "description": "开始时间（RFC3339 或 Unix 时间戳）"
                    },
                    "end": {
                        "type": "string",
                        "description": "结束时间（RFC3339 或 Unix 时间戳）"
                    },
                    "step": {
                        "type": "string",
                        "description": "查询步长，例如：15s, 1m, 1h"
                    }
                },
                "required": ["query", "start", "end", "step"]
            }
        ),
        Tool(
            name="prom_get_metric_metadata",
            description="获取指标的元数据（帮助信息、类型等）",
            inputSchema={
                "type": "object",
                "properties": {
                    "metric": {
                        "type": "string",
                        "description": "指标名称"
                    }
                },
                "required": ["metric"]
            }
        ),
        Tool(
            name="prom_get_targets",
            description="获取 Prometheus 抓取目标状态",
            inputSchema={
                "type": "object",
                "properties": {
                    "state": {
                        "type": "string",
                        "description": "过滤状态：active 或 dropped",
                        "enum": ["active", "dropped"]
                    }
                }
            }
        ),
        Tool(
            name="prom_get_alerts",
            description="获取当前告警列表",
            inputSchema={
                "type": "object",
                "properties": {
                    "state": {
                        "type": "string",
                        "description": "过滤告警状态",
                        "enum": ["firing", "pending", "inactive"]
                    }
                }
            }
        ),
        Tool(
            name="prom_get_rules",
            description="获取告警规则和记录规则",
            inputSchema={
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "description": "规则类型",
                        "enum": ["alert", "record", "all"]
                    },
                    "name": {
                        "type": "string",
                        "description": "规则名称过滤"
                    }
                }
            }
        ),
        Tool(
            name="prom_get_config",
            description="获取 Prometheus 当前配置",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="prom_get_status",
            description="获取 Prometheus 服务器状态",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="prom_get_label_values",
            description="获取指定标签的所有值",
            inputSchema={
                "type": "object",
                "properties": {
                    "label": {
                        "type": "string",
                        "description": "标签名称，例如：namespace, pod, job"
                    }
                },
                "required": ["label"]
            }
        ),
        Tool(
            name="prom_get_series",
            description="获取匹配的时间序列",
            inputSchema={
                "type": "object",
                "properties": {
                    "match": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "匹配模式列表，例如：['up', 'node_cpu_seconds_total']"
                    },
                    "start": {
                        "type": "string",
                        "description": "开始时间"
                    },
                    "end": {
                        "type": "string",
                        "description": "结束时间"
                    }
                },
                "required": ["match"]
            }
        ),
        Tool(
            name="prom_node_cpu_usage",
            description="获取节点 CPU 使用率",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {
                        "type": "string",
                        "description": "节点名称，不填则返回所有节点"
                    }
                }
            }
        ),
        Tool(
            name="prom_node_memory_usage",
            description="获取节点内存使用率",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {
                        "type": "string",
                        "description": "节点名称，不填则返回所有节点"
                    }
                }
            }
        ),
        Tool(
            name="prom_pod_cpu_usage",
            description="获取 Pod CPU 使用率",
            inputSchema={
                "type": "object",
                "properties": {
                    "namespace": {
                        "type": "string",
                        "description": "命名空间，不填则返回所有"
                    },
                    "pod": {
                        "type": "string",
                        "description": "Pod 名称，不填则返回所有"
                    }
                }
            }
        ),
        Tool(
            name="prom_pod_memory_usage",
            description="获取 Pod 内存使用率",
            inputSchema={
                "type": "object",
                "properties": {
                    "namespace": {
                        "type": "string",
                        "description": "命名空间，不填则返回所有"
                    },
                    "pod": {
                        "type": "string",
                        "description": "Pod 名称，不填则返回所有"
                    }
                }
            }
        ),
        Tool(
            name="prom_service_latency",
            description="获取服务延迟（P50/P90/P99）",
            inputSchema={
                "type": "object",
                "properties": {
                    "service": {
                        "type": "string",
                        "description": "服务名称"
                    },
                    "percentile": {
                        "type": "string",
                        "description": "百分位数：p50, p90, p99",
                        "enum": ["p50", "p90", "p99"]
                    }
                },
                "required": ["service"]
            }
        ),
        Tool(
            name="prom_service_error_rate",
            description="获取服务错误率",
            inputSchema={
                "type": "object",
                "properties": {
                    "service": {
                        "type": "string",
                        "description": "服务名称"
                    }
                },
                "required": ["service"]
            }
        )
    ]


# ─────────────────────────────────────────────────────────────
# 工具执行
# ─────────────────────────────────────────────────────────────

@prometheus_server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """执行 Prometheus 工具"""
    
    try:
        if name == "prom_query":
            return await prom_query(arguments)
        elif name == "prom_query_range":
            return await prom_query_range(arguments)
        elif name == "prom_get_metric_metadata":
            return await prom_get_metric_metadata(arguments)
        elif name == "prom_get_targets":
            return await prom_get_targets(arguments)
        elif name == "prom_get_alerts":
            return await prom_get_alerts(arguments)
        elif name == "prom_get_rules":
            return await prom_get_rules(arguments)
        elif name == "prom_get_config":
            return await prom_get_config(arguments)
        elif name == "prom_get_status":
            return await prom_get_status(arguments)
        elif name == "prom_get_label_values":
            return await prom_get_label_values(arguments)
        elif name == "prom_get_series":
            return await prom_get_series(arguments)
        elif name == "prom_node_cpu_usage":
            return await prom_node_cpu_usage(arguments)
        elif name == "prom_node_memory_usage":
            return await prom_node_memory_usage(arguments)
        elif name == "prom_pod_cpu_usage":
            return await prom_pod_cpu_usage(arguments)
        elif name == "prom_pod_memory_usage":
            return await prom_pod_memory_usage(arguments)
        elif name == "prom_service_latency":
            return await prom_service_latency(arguments)
        elif name == "prom_service_error_rate":
            return await prom_service_error_rate(arguments)
        else:
            return [TextContent(type="text", text=f"未知工具：{name}")]
    
    except Exception as e:
        return [TextContent(type="text", text=f"❌ 执行失败：{str(e)}")]


# ─────────────────────────────────────────────────────────────
# HTTP 客户端
# ─────────────────────────────────────────────────────────────

async def prometheus_request(endpoint: str, params: dict = None) -> dict:
    """发送请求到 Prometheus API"""
    url = f"{PROMETHEUS_URL}/api/v1/{endpoint}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, timeout=30.0)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") != "success":
            raise Exception(f"Prometheus API 错误：{data.get('error', 'Unknown error')}")
        
        return data.get("data", {})


# ─────────────────────────────────────────────────────────────
# 工具实现 - 基础查询
# ─────────────────────────────────────────────────────────────

async def prom_query(args: dict) -> list[TextContent]:
    """执行即时查询"""
    query = args.get("query")
    time = args.get("time")
    
    params = {"query": query}
    if time:
        params["time"] = time
    
    data = await prometheus_request("query", params)
    
    result_type = data.get("resultType")
    results = data.get("result", [])
    
    output = f"查询：{query}\n"
    output += f"类型：{result_type}\n"
    output += f"结果数量：{len(results)}\n\n"
    
    for result in results:
        metric = result.get("metric", {})
        value = result.get("value", [])
        timestamp = value[0] if len(value) > 0 else "N/A"
        metric_value = value[1] if len(value) > 1 else "N/A"
        
        output += f"指标：{metric.get('__name__', 'N/A')}\n"
        for k, v in metric.items():
            if k != "__name__":
                output += f"  {k}: {v}\n"
        output += f"  时间：{timestamp}\n"
        output += f"  值：{metric_value}\n\n"
    
    return [TextContent(type="text", text=f"📊 Prometheus 查询结果:\n```\n{output}\n```")]


async def prom_query_range(args: dict) -> list[TextContent]:
    """执行范围查询"""
    query = args.get("query")
    start = args.get("start")
    end = args.get("end")
    step = args.get("step")
    
    params = {
        "query": query,
        "start": start,
        "end": end,
        "step": step
    }
    
    data = await prometheus_request("query_range", params)
    
    results = data.get("result", [])
    output = f"范围查询：{query}\n"
    output += f"时间范围：{start} - {end}\n"
    output += f"步长：{step}\n"
    output += f"结果数量：{len(results)}\n\n"
    
    for result in results:
        metric = result.get("metric", {})
        values = result.get("values", [])
        
        output += f"指标：{metric.get('__name__', 'N/A')}\n"
        for k, v in metric.items():
            if k != "__name__":
                output += f"  {k}: {v}\n"
        output += f"  数据点数：{len(values)}\n"
        
        # 显示前 5 个和后 5 个数据点
        if len(values) > 10:
            for ts, val in values[:5]:
                output += f"  [{ts}] {val}\n"
            output += "  ...\n"
            for ts, val in values[-5:]:
                output += f"  [{ts}] {val}\n"
        else:
            for ts, val in values:
                output += f"  [{ts}] {val}\n"
        output += "\n"
    
    return [TextContent(type="text", text=f"📈 Prometheus 范围查询:\n```\n{output}\n```")]


# ─────────────────────────────────────────────────────────────
# 工具实现 - 元数据
# ─────────────────────────────────────────────────────────────

async def prom_get_metric_metadata(args: dict) -> list[TextContent]:
    """获取指标元数据"""
    metric = args.get("metric")
    
    data = await prometheus_request("metadata")
    
    if metric in data:
        metadata = data[metric]
        output = f"指标：{metric}\n"
        output += f"类型：{metadata.get('type', 'N/A')}\n"
        output += f"帮助：{metadata.get('help', 'N/A')}\n"
        return [TextContent(type="text", text=f"📝 指标元数据:\n```\n{output}\n```")]
    else:
        return [TextContent(type="text", text=f"⚠️ 未找到指标 {metric} 的元数据")]


async def prom_get_targets(args: dict) -> list[TextContent]:
    """获取抓取目标"""
    state = args.get("state", "active")
    
    data = await prometheus_request("targets", {"state": state})
    
    targets = data.get("activeTargets", [])
    output = f"抓取目标（状态：{state}）\n"
    output += f"数量：{len(targets)}\n\n"
    
    for target in targets:
        output += f"URL: {target.get('scrapeUrl', 'N/A')}\n"
        output += f"  状态：{target.get('health', 'N/A')}\n"
        output += f"  最后抓取：{target.get('lastScrape', 'N/A')}\n"
        if target.get('labels'):
            output += f"  标签:\n"
            for k, v in target['labels'].items():
                output += f"    {k}: {v}\n"
        output += "\n"
    
    return [TextContent(type="text", text=f"🎯 Prometheus 抓取目标:\n```\n{output}\n```")]


# ─────────────────────────────────────────────────────────────
# 工具实现 - 告警
# ─────────────────────────────────────────────────────────────

async def prom_get_alerts(args: dict) -> list[TextContent]:
    """获取告警列表"""
    state = args.get("state")
    
    params = {}
    if state:
        params["state"] = state
    
    data = await prometheus_request("alerts", params)
    
    alerts = data.get("alerts", [])
    output = f"告警列表"
    if state:
        output += f"（状态：{state}）"
    output += f"\n数量：{len(alerts)}\n\n"
    
    for alert in alerts:
        labels = alert.get("labels", {})
        annotations = alert.get("annotations", {})
        
        output += f"🚨 {labels.get('alertname', 'Unknown')}\n"
        output += f"  状态：{alert.get('state', 'N/A')}\n"
        output += f"  级别：{labels.get('severity', 'N/A')}\n"
        output += f"  描述：{annotations.get('description', 'N/A')}\n"
        output += f"  开始时间：{alert.get('startsAt', 'N/A')}\n"
        if alert.get('labels'):
            output += f"  标签:\n"
            for k, v in alert['labels'].items():
                if k not in ['alertname', 'severity']:
                    output += f"    {k}: {v}\n"
        output += "\n"
    
    return [TextContent(type="text", text=f"🔔 Prometheus 告警:\n```\n{output}\n```")]


async def prom_get_rules(args: dict) -> list[TextContent]:
    """获取规则列表"""
    rule_type = args.get("type", "all")
    name = args.get("name")
    
    data = await prometheus_request("rules")
    
    groups = data.get("groups", [])
    output = f"规则列表"
    if rule_type != "all":
        output += f"（类型：{rule_type}）"
    if name:
        output += f"（名称：{name}）"
    output += "\n\n"
    
    for group in groups:
        output += f"组：{group.get('name', 'N/A')}\n"
        output += f"  文件：{group.get('file', 'N/A')}\n"
        output += f"  规则数：{len(group.get('rules', []))}\n\n"
        
        for rule in group.get("rules", []):
            if rule_type == "alert" and rule.get("type") != "alerting":
                continue
            if rule_type == "record" and rule.get("type") != "recording":
                continue
            if name and name not in rule.get("name", ""):
                continue
            
            output += f"  - {rule.get('name', 'N/A')}\n"
            output += f"    类型：{rule.get('type', 'N/A')}\n"
            output += f"    查询：{rule.get('query', 'N/A')}\n"
            if rule.get("health"):
                output += f"    健康状态：{rule.get('health')}\n"
            output += "\n"
    
    return [TextContent(type="text", text=f"📋 Prometheus 规则:\n```\n{output}\n```")]


# ─────────────────────────────────────────────────────────────
# 工具实现 - 配置和状态
# ─────────────────────────────────────────────────────────────

async def prom_get_config(args: dict) -> list[TextContent]:
    """获取 Prometheus 配置"""
    data = await prometheus_request("status/config")
    
    yaml_config = data.get("yaml", "")
    return [TextContent(type="text", text=f"⚙️ Prometheus 配置:\n```\n{yaml_config}\n```")]


async def prom_get_status(args: dict) -> list[TextContent]:
    """获取 Prometheus 状态"""
    data = await prometheus_request("status/runtimeinfo")
    
    output = "Prometheus 状态\n"
    output += f"启动时间：{data.get('startTime', 'N/A')}\n"
    output += f"CWD: {data.get('CWD', 'N/A')}\n"
    output += f"版本：{data.get('prometheusVersion', 'N/A')}\n"
    output += f"存储保留：{data.get('storageRetention', 'N/A')}\n"
    
    return [TextContent(type="text", text=f"ℹ️ {output}")]


async def prom_get_label_values(args: dict) -> list[TextContent]:
    """获取标签值"""
    label = args.get("label")
    
    data = await prometheus_request(f"label/{label}/values")
    
    output = f"标签 '{label}' 的值:\n"
    output += f"数量：{len(data)}\n\n"
    
    # 显示前 20 个值
    for value in data[:20]:
        output += f"- {value}\n"
    
    if len(data) > 20:
        output += f"\n... 还有 {len(data) - 20} 个值"
    
    return [TextContent(type="text", text=f"🏷️ {output}")]


async def prom_get_series(args: dict) -> list[TextContent]:
    """获取时间序列"""
    match = args.get("match", [])
    start = args.get("start")
    end = args.get("end")
    
    params = {"match[]": match}
    if start:
        params["start"] = start
    if end:
        params["end"] = end
    
    data = await prometheus_request("series", params)
    
    output = f"时间序列:\n"
    output += f"数量：{len(data)}\n\n"
    
    for series in data[:10]:  # 限制显示数量
        output += f"- {series}\n"
    
    if len(data) > 10:
        output += f"\n... 还有 {len(data) - 10} 个序列"
    
    return [TextContent(type="text", text=f"📈 {output}")]


# ─────────────────────────────────────────────────────────────
# 工具实现 - 预定义指标
# ─────────────────────────────────────────────────────────────

async def prom_node_cpu_usage(args: dict) -> list[TextContent]:
    """获取节点 CPU 使用率"""
    node = args.get("node")
    
    query = '100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)'
    if node:
        query = f'100 - (avg by(instance) (irate(node_cpu_seconds_total{{mode="idle", instance="{node}"}}[5m])) * 100)'
    
    data = await prometheus_request("query", {"query": query})
    
    results = data.get("result", [])
    output = "节点 CPU 使用率\n\n"
    
    for result in results:
        instance = result.get("metric", {}).get("instance", "unknown")
        value = result.get("value", [None, "N/A"])[1]
        output += f"{instance}: {value}%\n"
    
    return [TextContent(type="text", text=f"🖥️ {output}")]


async def prom_node_memory_usage(args: dict) -> list[TextContent]:
    """获取节点内存使用率"""
    node = args.get("node")
    
    query = '(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100'
    if node:
        query = f'(1 - (node_memory_MemAvailable_bytes{{instance="{node}"}} / node_memory_MemTotal_bytes{{instance="{node}"}})) * 100'
    
    data = await prometheus_request("query", {"query": query})
    
    results = data.get("result", [])
    output = "节点内存使用率\n\n"
    
    for result in results:
        instance = result.get("metric", {}).get("instance", "unknown")
        value = result.get("value", [None, "N/A"])[1]
        output += f"{instance}: {value}%\n"
    
    return [TextContent(type="text", text=f"🖥️ {output}")]


async def prom_pod_cpu_usage(args: dict) -> list[TextContent]:
    """获取 Pod CPU 使用率"""
    namespace = args.get("namespace")
    pod = args.get("pod")
    
    query = 'sum by (namespace, pod) (rate(container_cpu_usage_seconds_total{container!=""}[5m])) * 100'
    
    if namespace:
        query = f'sum by (namespace, pod) (rate(container_cpu_usage_seconds_total{{container!="", namespace="{namespace}"}}[5m])) * 100'
    
    data = await prometheus_request("query", {"query": query})
    
    results = data.get("result", [])
    output = "Pod CPU 使用率\n\n"
    
    for result in results[:10]:  # 限制显示数量
        ns = result.get("metric", {}).get("namespace", "unknown")
        pod_name = result.get("metric", {}).get("pod", "unknown")
        value = result.get("value", [None, "N/A"])[1]
        output += f"{ns}/{pod_name}: {value}%\n"
    
    if len(results) > 10:
        output += f"\n... 还有 {len(results) - 10} 个 Pod"
    
    return [TextContent(type="text", text=f"📦 {output}")]


async def prom_pod_memory_usage(args: dict) -> list[TextContent]:
    """获取 Pod 内存使用率"""
    namespace = args.get("namespace")
    pod = args.get("pod")
    
    query = 'sum by (namespace, pod) (container_memory_usage_bytes{container!=""}) / sum by (namespace, pod) (container_spec_memory_limit_bytes{container!=""}) * 100'
    
    if namespace:
        query = f'sum by (namespace, pod) (container_memory_usage_bytes{{container!="", namespace="{namespace}"}}) / sum by (namespace, pod) (container_spec_memory_limit_bytes{{container!="", namespace="{namespace}"}}) * 100'
    
    data = await prometheus_request("query", {"query": query})
    
    results = data.get("result", [])
    output = "Pod 内存使用率\n\n"
    
    for result in results[:10]:
        ns = result.get("metric", {}).get("namespace", "unknown")
        pod_name = result.get("metric", {}).get("pod", "unknown")
        value = result.get("value", [None, "N/A"])[1]
        output += f"{ns}/{pod_name}: {value}%\n"
    
    if len(results) > 10:
        output += f"\n... 还有 {len(results) - 10} 个 Pod"
    
    return [TextContent(type="text", text=f"📦 {output}")]


async def prom_service_latency(args: dict) -> list[TextContent]:
    """获取服务延迟"""
    service = args.get("service")
    percentile = args.get("percentile", "p99")
    
    # 根据百分位选择查询
    percentile_map = {
        "p50": "0.50",
        "p90": "0.90",
        "p99": "0.99"
    }
    
    quantile = percentile_map.get(percentile, "0.99")
    query = f'histogram_quantile({quantile}, sum(rate(http_request_duration_seconds_bucket{{service="{service}"}}[5m])) by (le))'
    
    data = await prometheus_request("query", {"query": query})
    
    results = data.get("result", [])
    output = f"服务 {service} 延迟 ({percentile.upper()})\n\n"
    
    for result in results:
        value = result.get("value", [None, "N/A"])[1]
        output += f"延迟：{float(value) * 1000:.2f}ms\n"
    
    return [TextContent(type="text", text=f"⏱️ {output}")]


async def prom_service_error_rate(args: dict) -> list[TextContent]:
    """获取服务错误率"""
    service = args.get("service")
    
    query = f'sum(rate(http_requests_total{{service="{service}", status=~"5.."}}[5m])) / sum(rate(http_requests_total{{service="{service}"}}[5m])) * 100'
    
    data = await prometheus_request("query", {"query": query})
    
    results = data.get("result", [])
    output = f"服务 {service} 错误率\n\n"
    
    for result in results:
        value = result.get("value", [None, "N/A"])[1]
        output += f"错误率：{value}%\n"
    
    return [TextContent(type="text", text=f"❌ {output}")]


# ─────────────────────────────────────────────────────────────
# 主入口
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from mcp.server.stdio import stdio_server
    import asyncio
    
    async def main():
        async with stdio_server() as (read_stream, write_stream):
            await prometheus_server.run(
                read_stream,
                write_stream,
                prometheus_server.create_initialization_options()
            )
    
    asyncio.run(main())
