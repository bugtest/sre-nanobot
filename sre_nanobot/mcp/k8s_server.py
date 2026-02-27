"""
Kubernetes MCP Server

提供 K8s 集群操作的 MCP 工具接口
"""

import asyncio
import subprocess
from typing import Any
from mcp.server import Server
from mcp.types import Tool, TextContent, Resource, ResourceTemplate

# 创建 MCP 服务器实例
k8s_server = Server("sre-k8s-mcp")


# ─────────────────────────────────────────────────────────────
# 工具定义
# ─────────────────────────────────────────────────────────────

@k8s_server.list_tools()
async def list_tools() -> list[Tool]:
    """列出所有可用的 K8s 工具"""
    return [
        Tool(
            name="kubectl_get_pods",
            description="获取指定命名空间的 Pod 列表，支持标签选择器",
            inputSchema={
                "type": "object",
                "properties": {
                    "namespace": {
                        "type": "string",
                        "description": "Kubernetes 命名空间",
                        "default": "default"
                    },
                    "label_selector": {
                        "type": "string",
                        "description": "标签选择器，例如：app=nginx,tier=frontend"
                    },
                    "show_labels": {
                        "type": "boolean",
                        "description": "是否显示 Pod 标签",
                        "default": False
                    }
                },
                "required": ["namespace"]
            }
        ),
        Tool(
            name="kubectl_get_deployments",
            description="获取指定命名空间的 Deployment 列表",
            inputSchema={
                "type": "object",
                "properties": {
                    "namespace": {
                        "type": "string",
                        "description": "Kubernetes 命名空间",
                        "default": "default"
                    },
                    "show_details": {
                        "type": "boolean",
                        "description": "是否显示详细信息（副本数、镜像等）",
                        "default": False
                    }
                },
                "required": ["namespace"]
            }
        ),
        Tool(
            name="kubectl_get_services",
            description="获取指定命名空间的 Service 列表",
            inputSchema={
                "type": "object",
                "properties": {
                    "namespace": {
                        "type": "string",
                        "description": "Kubernetes 命名空间",
                        "default": "default"
                    }
                },
                "required": ["namespace"]
            }
        ),
        Tool(
            name="kubectl_get_events",
            description="获取指定命名空间的 Kubernetes 事件",
            inputSchema={
                "type": "object",
                "properties": {
                    "namespace": {
                        "type": "string",
                        "description": "Kubernetes 命名空间",
                        "default": "default"
                    },
                    "field_selector": {
                        "type": "string",
                        "description": "字段选择器，例如：involvedObject.name=my-pod"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "返回事件数量限制",
                        "default": 50
                    }
                },
                "required": ["namespace"]
            }
        ),
        Tool(
            name="kubectl_restart_deployment",
            description="重启指定的 Deployment（触发滚动更新）",
            inputSchema={
                "type": "object",
                "properties": {
                    "namespace": {
                        "type": "string",
                        "description": "Kubernetes 命名空间"
                    },
                    "deployment": {
                        "type": "string",
                        "description": "Deployment 名称"
                    }
                },
                "required": ["namespace", "deployment"]
            }
        ),
        Tool(
            name="kubectl_scale_deployment",
            description="扩缩容指定的 Deployment",
            inputSchema={
                "type": "object",
                "properties": {
                    "namespace": {
                        "type": "string",
                        "description": "Kubernetes 命名空间"
                    },
                    "deployment": {
                        "type": "string",
                        "description": "Deployment 名称"
                    },
                    "replicas": {
                        "type": "integer",
                        "description": "目标副本数",
                        "minimum": 0
                    }
                },
                "required": ["namespace", "deployment", "replicas"]
            }
        ),
        Tool(
            name="kubectl_get_logs",
            description="获取指定 Pod 的日志",
            inputSchema={
                "type": "object",
                "properties": {
                    "namespace": {
                        "type": "string",
                        "description": "Kubernetes 命名空间"
                    },
                    "pod": {
                        "type": "string",
                        "description": "Pod 名称"
                    },
                    "container": {
                        "type": "string",
                        "description": "容器名称（可选，用于多容器 Pod）"
                    },
                    "tail": {
                        "type": "integer",
                        "description": "返回最后多少行日志",
                        "default": 100
                    },
                    "since": {
                        "type": "string",
                        "description": "返回多久之前的日志，例如：1h, 30m, 5s"
                    }
                },
                "required": ["namespace", "pod"]
            }
        ),
        Tool(
            name="kubectl_describe_pod",
            description="获取指定 Pod 的详细信息（用于故障排查）",
            inputSchema={
                "type": "object",
                "properties": {
                    "namespace": {
                        "type": "string",
                        "description": "Kubernetes 命名空间"
                    },
                    "pod": {
                        "type": "string",
                        "description": "Pod 名称"
                    }
                },
                "required": ["namespace", "pod"]
            }
        ),
        Tool(
            name="kubectl_describe_node",
            description="获取指定 Node 的详细信息（用于节点故障排查）",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {
                        "type": "string",
                        "description": "Node 名称"
                    }
                },
                "required": ["node"]
            }
        ),
        Tool(
            name="kubectl_get_nodes",
            description="获取集群中所有 Node 的状态",
            inputSchema={
                "type": "object",
                "properties": {
                    "show_details": {
                        "type": "boolean",
                        "description": "是否显示详细信息（CPU、内存等）",
                        "default": False
                    }
                }
            }
        ),
        Tool(
            name="kubectl_get_resource_usage",
            description="获取命名空间的资源使用情况（CPU/内存）",
            inputSchema={
                "type": "object",
                "properties": {
                    "namespace": {
                        "type": "string",
                        "description": "Kubernetes 命名空间",
                        "default": "default"
                    }
                },
                "required": ["namespace"]
            }
        )
    ]


# ─────────────────────────────────────────────────────────────
# 工具执行
# ─────────────────────────────────────────────────────────────

@k8s_server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """执行 K8s 工具"""
    
    try:
        if name == "kubectl_get_pods":
            return await get_pods(arguments)
        elif name == "kubectl_get_deployments":
            return await get_deployments(arguments)
        elif name == "kubectl_get_services":
            return await get_services(arguments)
        elif name == "kubectl_get_events":
            return await get_events(arguments)
        elif name == "kubectl_restart_deployment":
            return await restart_deployment(arguments)
        elif name == "kubectl_scale_deployment":
            return await scale_deployment(arguments)
        elif name == "kubectl_get_logs":
            return await get_logs(arguments)
        elif name == "kubectl_describe_pod":
            return await describe_pod(arguments)
        elif name == "kubectl_describe_node":
            return await describe_node(arguments)
        elif name == "kubectl_get_nodes":
            return await get_nodes(arguments)
        elif name == "kubectl_get_resource_usage":
            return await get_resource_usage(arguments)
        else:
            return [TextContent(type="text", text=f"未知工具：{name}")]
    
    except Exception as e:
        return [TextContent(type="text", text=f"❌ 执行失败：{str(e)}")]


# ─────────────────────────────────────────────────────────────
# 工具实现
# ─────────────────────────────────────────────────────────────

async def run_kubectl(args: list[str], timeout: int = 30) -> str:
    """运行 kubectl 命令"""
    cmd = ["kubectl"] + args
    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=timeout
        )
        
        if process.returncode != 0:
            raise Exception(f"kubectl 失败：{stderr.decode('utf-8')}")
        
        return stdout.decode('utf-8')
    
    except asyncio.TimeoutError:
        raise Exception(f"kubectl 超时（{timeout}秒）")


async def get_pods(args: dict) -> list[TextContent]:
    """获取 Pod 列表"""
    namespace = args.get("namespace", "default")
    label_selector = args.get("label_selector")
    show_labels = args.get("show_labels", False)
    
    cmd_args = ["get", "pods", "-n", namespace]
    
    if label_selector:
        cmd_args.extend(["-l", label_selector])
    
    if show_labels:
        cmd_args.append("--show-labels")
    
    output = await run_kubectl(cmd_args)
    return [TextContent(type="text", text=f"📦 Pods in {namespace}:\n```\n{output}\n```")]


async def get_deployments(args: dict) -> list[TextContent]:
    """获取 Deployment 列表"""
    namespace = args.get("namespace", "default")
    show_details = args.get("show_details", False)
    
    cmd_args = ["get", "deployments", "-n", namespace]
    
    if show_details:
        cmd_args.append("-o wide")
    
    output = await run_kubectl(cmd_args)
    return [TextContent(type="text", text=f"🚀 Deployments in {namespace}:\n```\n{output}\n```")]


async def get_services(args: dict) -> list[TextContent]:
    """获取 Service 列表"""
    namespace = args.get("namespace", "default")
    
    output = await run_kubectl(["get", "services", "-n", namespace])
    return [TextContent(type="text", text=f"🌐 Services in {namespace}:\n```\n{output}\n```")]


async def get_events(args: dict) -> list[TextContent]:
    """获取 Kubernetes 事件"""
    namespace = args.get("namespace", "default")
    field_selector = args.get("field_selector")
    limit = args.get("limit", 50)
    
    cmd_args = ["get", "events", "-n", namespace, "--sort-by=.lastTimestamp"]
    
    if field_selector:
        cmd_args.extend(["--field-selector", field_selector])
    
    output = await run_kubectl(cmd_args)
    
    # 只返回最新的 limit 条事件
    lines = output.strip().split('\n')
    recent_events = '\n'.join(lines[-limit:]) if len(lines) > limit else output
    
    return [TextContent(type="text", text=f"📋 Events in {namespace}:\n```\n{recent_events}\n```")]


async def restart_deployment(args: dict) -> list[TextContent]:
    """重启 Deployment"""
    namespace = args.get("namespace")
    deployment = args.get("deployment")
    
    if not namespace or not deployment:
        return [TextContent(type="text", text="❌ 缺少参数：namespace 和 deployment 是必需的")]
    
    output = await run_kubectl([
        "rollout", "restart", "deployment", deployment, "-n", namespace
    ])
    
    return [TextContent(type="text", text=f"✅ 重启 Deployment `{deployment}` (namespace: {namespace}):\n```\n{output}\n```")]


async def scale_deployment(args: dict) -> list[TextContent]:
    """扩缩容 Deployment"""
    namespace = args.get("namespace")
    deployment = args.get("deployment")
    replicas = args.get("replicas")
    
    if not all([namespace, deployment, replicas is not None]):
        return [TextContent(type="text", text="❌ 缺少参数：namespace, deployment, replicas 是必需的")]
    
    output = await run_kubectl([
        "scale", "deployment", deployment, "-n", namespace, f"--replicas={replicas}"
    ])
    
    return [TextContent(type="text", text=f"✅ 扩缩容 Deployment `{deployment}` 到 {replicas} 副本:\n```\n{output}\n```")]


async def get_logs(args: dict) -> list[TextContent]:
    """获取 Pod 日志"""
    namespace = args.get("namespace")
    pod = args.get("pod")
    container = args.get("container")
    tail = args.get("tail", 100)
    since = args.get("since")
    
    if not namespace or not pod:
        return [TextContent(type="text", text="❌ 缺少参数：namespace 和 pod 是必需的")]
    
    cmd_args = ["logs", pod, "-n", namespace, "--tail", str(tail)]
    
    if container:
        cmd_args.extend(["-c", container])
    
    if since:
        cmd_args.extend(["--since", since])
    
    output = await run_kubectl(cmd_args)
    return [TextContent(type="text", text=f"📜 Logs from `{pod}`:\n```\n{output}\n```")]


async def describe_pod(args: dict) -> list[TextContent]:
    """描述 Pod 详情"""
    namespace = args.get("namespace")
    pod = args.get("pod")
    
    if not namespace or not pod:
        return [TextContent(type="text", text="❌ 缺少参数：namespace 和 pod 是必需的")]
    
    output = await run_kubectl(["describe", "pod", pod, "-n", namespace])
    return [TextContent(type="text", text=f"🔍 Pod `{pod}` 详情:\n```\n{output}\n```")]


async def describe_node(args: dict) -> list[TextContent]:
    """描述 Node 详情"""
    node = args.get("node")
    
    if not node:
        return [TextContent(type="text", text="❌ 缺少参数：node 是必需的")]
    
    output = await run_kubectl(["describe", "node", node])
    return [TextContent(type="text", text=f"🔍 Node `{node}` 详情:\n```\n{output}\n```")]


async def get_nodes(args: dict) -> list[TextContent]:
    """获取 Node 列表"""
    show_details = args.get("show_details", False)
    
    cmd_args = ["get", "nodes"]
    
    if show_details:
        cmd_args.append("-o wide")
    
    output = await run_kubectl(cmd_args)
    return [TextContent(type="text", text=f"🖥️ Cluster Nodes:\n```\n{output}\n```")]


async def get_resource_usage(args: dict) -> list[TextContent]:
    """获取资源使用情况"""
    namespace = args.get("namespace", "default")
    
    try:
        output = await run_kubectl(["top", "pods", "-n", namespace])
        return [TextContent(type="text", text=f"📊 Resource Usage in {namespace}:\n```\n{output}\n```")]
    except Exception as e:
        return [TextContent(type="text", text=f"⚠️ 无法获取资源使用（需要 metrics-server）: {str(e)}")]


# ─────────────────────────────────────────────────────────────
# 资源定义（可选）
# ─────────────────────────────────────────────────────────────

@k8s_server.list_resources()
async def list_resources() -> list[Resource]:
    """列出可用的 K8s 资源"""
    return [
        Resource(
            uri="k8s://cluster/nodes",
            name="Kubernetes Nodes",
            description="集群中的所有 Node",
            mimeType="application/json"
        ),
        Resource(
            uri="k8s://cluster/namespaces",
            name="Kubernetes Namespaces",
            description="集群中的所有命名空间",
            mimeType="application/json"
        )
    ]


@k8s_server.read_resource()
async def read_resource(uri: str) -> str:
    """读取 K8s 资源"""
    if uri == "k8s://cluster/nodes":
        return await run_kubectl(["get", "nodes", "-o", "json"])
    elif uri == "k8s://cluster/namespaces":
        return await run_kubectl(["get", "namespaces", "-o", "json"])
    else:
        raise ValueError(f"不支持的资源 URI: {uri}")


# ─────────────────────────────────────────────────────────────
# 资源模板（用于动态资源）
# ─────────────────────────────────────────────────────────────

@k8s_server.list_resource_templates()
async def list_resource_templates() -> list[ResourceTemplate]:
    """列出资源模板"""
    return [
        ResourceTemplate(
            uriTemplate="k8s://namespace/{namespace}/pods/{pod}",
            name="Kubernetes Pod",
            description="获取指定 Pod 的详细信息"
        ),
        ResourceTemplate(
            uriTemplate="k8s://namespace/{namespace}/deployments/{deployment}",
            name="Kubernetes Deployment",
            description="获取指定 Deployment 的详细信息"
        )
    ]


# ─────────────────────────────────────────────────────────────
# 主入口
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from mcp.server.stdio import stdio_server
    import asyncio
    
    async def main():
        async with stdio_server() as (read_stream, write_stream):
            await k8s_server.run(
                read_stream,
                write_stream,
                k8s_server.create_initialization_options()
            )
    
    asyncio.run(main())
