# SRE 预案库

> 标准化运维预案集合

---

## 📚 预案分类

### 故障处理类

| 预案 ID | 名称 | 触发条件 | 风险等级 |
|---------|------|----------|----------|
| `pod_restart` | Pod 重启 | CrashLooping, NotReady | 低 |
| `deployment_restart` | 部署重启 | HighErrorRate, Unavailable | 中 |
| `deployment_rollback` | 部署回滚 | DeploymentFailed | 中 |
| `service_recovery` | 服务恢复 | ServiceUnavailable | 中 |

### 资源管理类

| 预案 ID | 名称 | 触发条件 | 风险等级 |
|---------|------|----------|----------|
| `scale_up` | 扩容 | HighCPU, HighMemory | 低 |
| `scale_down` | 缩容 | LowUsage | 低 |
| `resource_limit_update` | 资源限制更新 | OOMKilled, Throttled | 中 |
| `node_drain` | 节点排空 | NodeNotReady, DiskPressure | 高 |

### 网络问题类

| 预案 ID | 名称 | 触发条件 | 风险等级 |
|---------|------|----------|----------|
| `dns_recovery` | DNS 恢复 | DNSResolutionFailed | 中 |
| `ingress_recovery` | Ingress 恢复 | IngressUnavailable | 中 |
| `network_policy_fix` | 网络策略修复 | NetworkPolicyDenied | 中 |

### 存储问题类

| 预案 ID | 名称 | 触发条件 | 风险等级 |
|---------|------|----------|----------|
| `pvc_recovery` | PVC 恢复 | PVCPending, PVCBoundFailed | 中 |
| `disk_cleanup` | 磁盘清理 | DiskPressure, HighDiskUsage | 低 |

### 数据库类

| 预案 ID | 名称 | 触发条件 | 风险等级 |
|---------|------|----------|----------|
| `database_connection_fix` | 数据库连接修复 | DatabaseConnectionFailed | 高 |
| `database_failover` | 数据库故障转移 | DatabaseUnavailable | 高 |

---

## 📋 预案结构

每个预案包含：

```yaml
name: 预案名称
version: 版本号
description: 预案描述
triggers:
  - 触发告警 1
  - 触发告警 2
severity: 风险等级（low/medium/high）
timeout: 超时时间（秒）
steps:
  - name: 步骤名称
    type: 步骤类型
    action: 操作
    params: 参数
    on_failure: 失败处理（abort/rollback/continue）
rollback:
  - 回滚步骤
verification:
  - 验证步骤
```

---

## 🔧 步骤类型

| 类型 | 说明 | 示例 |
|------|------|------|
| `k8s` | K8s 操作 | get_pods, restart, scale |
| `http` | HTTP 请求 | health_check, api_call |
| `wait` | 等待 | wait 60s |
| `analysis` | 分析操作 | verify_crash_loop |
| `calculation` | 计算操作 | calculate_replicas |
| `metrics` | 指标检查 | check_cpu, check_memory |
| `notification` | 通知发送 | send_message |
| `script` | 脚本执行 | run_shell_script |

---

## 📊 使用统计

- 总预案数：15+
- 覆盖场景：故障/资源/网络/存储/数据库
- 平均步骤数：5 步
- 自动化率：80%

---

*最后更新：2026-02-27*
