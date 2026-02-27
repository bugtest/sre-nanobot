#!/usr/bin/env python3
"""
飞书集成测试

测试飞书通知功能
"""

import asyncio
import sys
from sre_nanobot.integrations.feishu_notifier import FeishuNotifier


# 测试配置（从环境变量或配置文件读取）
TEST_WEBHOOK_URL = "YOUR_WEBHOOK_URL"  # 替换为实际 Webhook
TEST_SECRET = None  # 可选的签名密钥


async def test_feishu_integration():
    """测试飞书集成"""
    
    print("=" * 60)
    print("飞书集成测试")
    print("=" * 60)
    print()
    
    # 检查配置
    if TEST_WEBHOOK_URL == "YOUR_WEBHOOK_URL":
        print("⚠️  警告：请配置 TEST_WEBHOOK_URL")
        print()
        print("使用方法:")
        print("1. 编辑 test_feishu.py")
        print("2. 替换 TEST_WEBHOOK_URL 为你的飞书 Webhook URL")
        print("3. 重新运行测试")
        print()
        return False
    
    # 创建通知器
    notifier = FeishuNotifier(TEST_WEBHOOK_URL, TEST_SECRET)
    
    try:
        # 测试 1: 文本消息
        print("📝 测试 1: 发送文本消息...")
        result = await notifier.send_text(
            "【SRE-NanoBot 测试】这是一条测试消息",
            mentioned=[]
        )
        print(f"{'✅' if result else '❌'} 文本消息发送{'成功' if result else '失败'}")
        print()
        
        # 测试 2: 告警通知
        print("🚨 测试 2: 发送告警通知...")
        alert_data = {
            "name": "PodCrashLooping",
            "severity": "P1",
            "status": "firing",
            "description": "Pod production/api-service-abc12 在 5 分钟内重启 5 次",
            "affected_services": ["api-service"],
            "dashboard_url": "https://grafana.example.com"
        }
        result = await notifier.send_alert_notification(alert_data)
        print(f"{'✅' if result else '❌'} 告警通知发送{'成功' if result else '失败'}")
        print()
        
        # 测试 3: 审批请求
        print("🔐 测试 3: 发送审批请求...")
        approval_data = {
            "operation": "Pod 重启",
            "agent": "AutoFix",
            "risk_level": "medium",
            "details": "重启 production/api-service Deployment",
            "impact": "api-service 服务，预计影响 3-5 分钟",
            "duration": "3-5 分钟",
            "request_id": "test-001",
            "timeout": 300
        }
        result = await notifier.send_approval_request(approval_data)
        print(f"{'✅' if result else '❌'} 审批请求发送{'成功' if result else '失败'}")
        print()
        
        # 测试 4: POST 消息（富文本）
        print("📄 测试 4: 发送 POST 消息...")
        result = await notifier.send_post(
            "SRE-NanoBot 测试报告",
            [
                [
                    {"tag": "text", "text": "测试时间："},
                    {"tag": "at", "user_id": "all"}
                ],
                [
                    {"tag": "text", "text": "测试结果："},
                    {"tag": "text", "text": "全部通过", "style": {"bold": True}}
                ],
                [
                    {"tag": "text", "text": "测试人员："},
                    {"tag": "user", "user_id": "ou_xxx"}
                ]
            ]
        )
        print(f"{'✅' if result else '❌'} POST 消息发送{'成功' if result else '失败'}")
        print()
        
        # 测试 5: 故障报告
        print("📋 测试 5: 发送故障报告...")
        incident_data = {
            "id": "INC-TEST-001",
            "severity": "P1",
            "status": "resolved",
            "summary": "发生资源耗尽，影响 1 个服务",
            "root_cause": "内存限制过低导致 OOM",
            "affected_services": ["api-service"],
            "duration": "6 分钟",
            "user_impact": "10%",
            "timeline_summary": "14:00 告警触发 → 14:01 分析 → 14:03 重启 → 14:06 恢复",
            "action_items": "1. 增加内存限制\n2. 添加内存监控"
        }
        result = await notifier.send_incident_report(incident_data)
        print(f"{'✅' if result else '❌'} 故障报告发送{'成功' if result else '失败'}")
        print()
        
        # 测试 6: 日报
        print("📊 测试 6: 发送日报...")
        report_data = {
            "date": "2026-02-27",
            "on_call": "张三",
            "p0_count": 0,
            "p1_count": 2,
            "p2_count": 5,
            "auto_fixed": 3,
            "availability": "99.9%",
            "avg_latency": "50ms",
            "error_rate": "0.1%",
            "changes": "- api-service v1.2.3 发布\n- 数据库索引优化",
            "todos": "- 审查 P1 告警根因\n- 更新扩容预案"
        }
        result = await notifier.send_daily_report(report_data)
        print(f"{'✅' if result else '❌'} 日报发送{'成功' if result else '失败'}")
        print()
        
        print("=" * 60)
        print("测试完成！")
        print("=" * 60)
        
        return True
    
    except Exception as e:
        print(f"❌ 测试异常：{e}")
        return False
    
    finally:
        await notifier.close()


if __name__ == "__main__":
    success = asyncio.run(test_feishu_integration())
    sys.exit(0 if success else 1)
