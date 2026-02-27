# K8s 运维技能

> Kubernetes 集群管理技能包

## 功能

本技能提供以下 K8s 运维能力：

- 📦 Pod 管理（查看、日志、描述）
- 🚀 Deployment 管理（查看、重启、扩缩容）
- 🌐 Service 查看
- 📋 事件查看
- 🖥️ Node 管理（查看、描述）
- 📊 资源使用监控

## 工具

### 查看类工具

| 工具 | 描述 | 参数 |
|------|------|------|
| `kubectl_get_pods` | 获取 Pod 列表 | namespace, label_selector, show_labels |
| `kubectl_get_deployments` | 获取 Deployment 列表 | namespace, show_details |
| `kubectl_get_services` | 获取 Service 列表 | namespace |
| `kubectl_get_events` | 获取事件 | namespace, field_selector, limit |
| `kubectl_get_nodes` | 获取 Node 列表 | show_details |
| `kubectl_get_resource_usage` | 获取资源使用 | namespace |
| `kubectl_get_logs` | 获取 Pod 日志 | namespace, pod, container, tail, since |
| `kubectl_describe_pod` | 描述 Pod 详情 | namespace, pod |
| `kubectl_describe_node` | 描述 Node 详情 | node |

### 操作类工具

| 工具 | 描述 | 参数 | 审批 |
|------|------|------|------|
| `kubectl_restart_deployment` | 重启 Deployment | namespace, deployment | 生产环境需要 |
| `kubectl_scale_deployment` | 扩缩容 Deployment | namespace, deployment, replicas | >10 副本需要 |

## 使用示例

### 查看 Pod 状态

```
查看 production 命名空间的所有 Pod
```

```
查看 app=api 的 Pod
```

```
查看 production 命名空间的 Pod，显示标签
```

### 重启服务

```
重启 production 命名空间的 api-service
```

```
重启 staging 命名空间的 web-frontend
```

### 扩缩容

```
将 api-service 扩展到 10 个副本
```

```
将 test-service 缩容到 0 个副本
```

### 查看日志

```
查看 api-service-abc123 的最后 200 行日志
```

```
查看 api-service-abc123 的日志，过去 1 小时
```

### 故障排查

```
详细描述 pod api-service-abc123 的问题
```

```
查看节点 node-1 的详细信息
```

```
查看 production 命名空间最近的事件
```

## 安全边界

### 允许的操作（无需审批）

- ✅ 查看所有资源
- ✅ 查看日志
- ✅ 查看事件
- ✅ 查看资源使用
- ✅ 描述资源详情

### 需要审批的操作

- ⚠️ 生产环境重启 Deployment
- ⚠️ 扩缩容超过 10 副本
- ⚠️ 缩容到 0 副本

### 禁止的操作

- ❌ 删除 Pod/Deployment
- ❌ 修改资源定义
- ❌ 删除命名空间
- ❌ 修改 RBAC 配置
- ❌ 访问 kube-system 命名空间（除非明确授权）

## 配置

在 `~/.nanobot/config.json` 中添加：

```json
{
  "tools": {
    "mcpServers": {
      "k8s": {
        "command": "python",
        "args": ["-m", "sre_nanobot.mcp.k8s_server"]
      }
    }
  }
}
```

## 依赖

- kubectl（已配置集群访问）
- Kubernetes 集群访问权限
- metrics-server（用于资源使用查看）

## 故障排查

### kubectl 命令失败

检查集群连接：
```bash
kubectl cluster-info
kubectl get nodes
```

### 权限不足

确保有正确的 RBAC 权限：
```bash
kubectl auth can-i get pods -n production
kubectl auth can-i restart deployment -n production
```

### MCP 服务器无法启动

检查日志：
```bash
python -m sre_nanobot.mcp.k8s_server
```

## 版本

- v0.1.0 - 初始版本
