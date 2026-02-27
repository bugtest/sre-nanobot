"""
飞书通知集成

支持：
- 告警通知
- 审批请求
- 故障报告
- 日常巡检报告
"""

import httpx
import hashlib
import hmac
import base64
import time
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class FeishuNotifier:
    """飞书通知器"""
    
    def __init__(self, webhook_url: str, secret: Optional[str] = None):
        """
        初始化飞书通知器
        
        Args:
            webhook_url: 飞书机器人 Webhook URL
            secret: 签名密钥（可选）
        """
        self.webhook_url = webhook_url
        self.secret = secret
        self.client = httpx.AsyncClient(timeout=30.0)
    
    def _generate_signature(self, timestamp: str) -> str:
        """生成签名"""
        if not self.secret:
            return ""
        
        string_to_sign = f"{timestamp}\n{self.secret}"
        hmac_code = hmac.new(
            string_to_sign.encode("utf-8"),
            digestmod=hashlib.sha256
        ).digest()
        
        sign = base64.b64encode(hmac_code).decode('utf-8')
        return sign
    
    async def send_message(self, content: Dict[str, Any], msg_type: str = "interactive") -> bool:
        """
        发送消息
        
        Args:
            content: 消息内容
            msg_type: 消息类型 (text/post/interactive)
        
        Returns:
            bool: 是否发送成功
        """
        try:
            timestamp = str(int(time.time()))
            headers = {
                "Content-Type": "application/json"
            }
            
            payload = {
                "msg_type": msg_type,
                "content": content
            }
            
            # 添加签名
            if self.secret:
                sign = self._generate_signature(timestamp)
                headers["X-Lark-Signature-Timestamp"] = timestamp
                headers["X-Lark-Signature"] = sign
            
            response = await self.client.post(
                self.webhook_url,
                json=payload,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 0 or result.get("StatusCode") == 0:
                    logger.info("飞书消息发送成功")
                    return True
            
            logger.error(f"飞书消息发送失败：{response.text}")
            return False
        
        except Exception as e:
            logger.error(f"飞书消息发送异常：{e}")
            return False
    
    async def send_text(self, text: str, mentioned: Optional[List[str]] = None) -> bool:
        """发送文本消息"""
        content = {"text": text}
        if mentioned:
            content["mentioned"] = mentioned
        
        return await self.send_message(content, msg_type="text")
    
    async def send_post(self, title: str, content: List[List[Dict[str, str]]]) -> bool:
        """
        发送 POST 消息（富文本）
        
        Args:
            title: 标题
            content: 内容数组，支持 text/ati/emoji/image
        """
        content_data = {
            "title": title,
            "content": content
        }
        
        return await self.send_message(content_data, msg_type="post")
    
    async def send_interactive(self, card: Dict[str, Any]) -> bool:
        """
        发送互动卡片消息
        
        Args:
            card: 卡片配置
        """
        return await self.send_message({"card": card}, msg_type="interactive")
    
    # ─────────────────────────────────────────────────────
    # 告警通知
    # ─────────────────────────────────────────────────────
    
    async def send_alert_notification(self, alert: Dict[str, Any]) -> bool:
        """
        发送告警通知
        
        Args:
            alert: 告警信息
        """
        severity = alert.get("severity", "P2")
        alert_name = alert.get("name", "Unknown")
        status = alert.get("status", "firing")
        
        # 根据严重性选择颜色和 emoji
        severity_config = {
            "P0": {"color": "red", "emoji": "🚨", "tag": "urgent"},
            "P1": {"color": "orange", "emoji": "⚠️", "tag": "high"},
            "P2": {"color": "yellow", "emoji": "⚡", "tag": "medium"},
            "P3": {"color": "blue", "emoji": "ℹ️", "tag": "low"}
        }
        
        config = severity_config.get(severity, severity_config["P2"])
        
        # 构建卡片
        card = {
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": f"{config['emoji']} {alert_name}"
                },
                "template": config["color"]
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**告警级别**: {severity}\n**状态**: {status}\n**时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    }
                },
                {
                    "tag": "hr"
                },
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**描述**: {alert.get('description', 'N/A')}"
                    }
                },
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**影响服务**: {', '.join(alert.get('affected_services', []))}"
                    }
                },
                {
                    "tag": "hr"
                },
                {
                    "tag": "action",
                    "actions": [
                        {
                            "tag": "button",
                            "text": {
                                "tag": "plain_text",
                                "content": "查看详情"
                            },
                            "type": "primary",
                            "url": alert.get("dashboard_url", "")
                        },
                        {
                            "tag": "button",
                            "text": {
                                "tag": "plain_text",
                                "content": "确认告警"
                            },
                            "type": "default",
                            "confirm": {
                                "title": "确认告警",
                                "text": "确认已收到此告警？",
                                "confirm": {"text": "确认"},
                                "deny": {"text": "取消"}
                            }
                        }
                    ]
                }
            ]
        }
        
        # 添加@提醒
        if severity in ["P0", "P1"]:
            card["elements"].insert(0, {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**<at id=all></at> 紧急告警！**"
                }
            })
        
        return await self.send_interactive(card)
    
    # ─────────────────────────────────────────────────────
    # 审批请求
    # ─────────────────────────────────────────────────────
    
    async def send_approval_request(self, approval: Dict[str, Any]) -> bool:
        """
        发送审批请求
        
        Args:
            approval: 审批信息
        """
        card = {
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": "🔐 运维操作审批请求"
                },
                "template": "blue"
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**操作类型**: {approval.get('operation', 'Unknown')}\n**执行 Agent**: {approval.get('agent', 'AutoFix')}\n**风险等级**: {approval.get('risk_level', 'medium')}"
                    }
                },
                {
                    "tag": "hr"
                },
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**详细信息**:\n{approval.get('details', 'N/A')}"
                    }
                },
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**影响范围**: {approval.get('impact', 'N/A')}\n**预计时间**: {approval.get('duration', 'N/A')}"
                    }
                },
                {
                    "tag": "hr"
                },
                {
                    "tag": "action",
                    "actions": [
                        {
                            "tag": "button",
                            "text": {
                                "tag": "plain_text",
                                "content": "✅ 批准"
                            },
                            "type": "primary",
                            "value": {
                                "action": "approve",
                                "request_id": approval.get("request_id")
                            },
                            "confirm": {
                                "title": "确认批准",
                                "text": "批准此运维操作？",
                                "confirm": {"text": "批准"},
                                "deny": {"text": "再想想"}
                            }
                        },
                        {
                            "tag": "button",
                            "text": {
                                "tag": "plain_text",
                                "content": "❌ 拒绝"
                            },
                            "type": "danger",
                            "value": {
                                "action": "reject",
                                "request_id": approval.get("request_id")
                            },
                            "confirm": {
                                "title": "确认拒绝",
                                "text": "拒绝此运维操作？",
                                "confirm": {"text": "拒绝"},
                                "deny": {"text": "再想想"}
                            }
                        },
                        {
                            "tag": "button",
                            "text": {
                                "tag": "plain_text",
                                "content": "💬 评论"
                            },
                            "type": "default"
                        }
                    ]
                },
                {
                    "tag": "note",
                    "elements": [
                        {
                            "tag": "plain_text",
                            "content": f"审批超时时间：{approval.get('timeout', 300)}秒"
                        }
                    ]
                }
            ]
        }
        
        return await self.send_interactive(card)
    
    # ─────────────────────────────────────────────────────
    # 故障报告
    # ─────────────────────────────────────────────────────
    
    async def send_incident_report(self, incident: Dict[str, Any]) -> bool:
        """
        发送故障报告
        
        Args:
            incident: 故障报告信息
        """
        card = {
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": "📋 故障处理报告"
                },
                "template": incident.get("status") == "resolved" and "green" or "blue"
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**故障 ID**: {incident.get('id', 'N/A')}\n**严重级别**: {incident.get('severity', 'P2')}\n**状态**: {incident.get('status', 'investigating')}"
                    }
                },
                {
                    "tag": "hr"
                },
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**摘要**: {incident.get('summary', 'N/A')}"
                    }
                },
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**根因**: {incident.get('root_cause', '待分析')}"
                    }
                },
                {
                    "tag": "hr"
                },
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**影响服务**: {', '.join(incident.get('affected_services', []))}\n**持续时间**: {incident.get('duration', 'N/A')}\n**用户影响**: {incident.get('user_impact', 'N/A')}"
                    }
                },
                {
                    "tag": "hr"
                },
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**处理过程**:\n{incident.get('timeline_summary', 'N/A')}"
                    }
                },
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**后续改进**:\n{incident.get('action_items', 'N/A')}"
                    }
                }
            ]
        }
        
        return await self.send_interactive(card)
    
    # ─────────────────────────────────────────────────────
    # 日常报告
    # ─────────────────────────────────────────────────────
    
    async def send_daily_report(self, report: Dict[str, Any]) -> bool:
        """
        发送日报
        
        Args:
            report: 日报信息
        """
        card = {
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": "📊 SRE 日报"
                },
                "template": "blue"
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**日期**: {report.get('date', datetime.now().strftime('%Y-%m-%d'))}\n**值班**: {report.get('on_call', 'N/A')}"
                    }
                },
                {
                    "tag": "hr"
                },
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**告警统计**:\n• P0 告警：{report.get('p0_count', 0)}\n• P1 告警：{report.get('p1_count', 0)}\n• P2 告警：{report.get('p2_count', 0)}\n• 自动修复：{report.get('auto_fixed', 0)}"
                    }
                },
                {
                    "tag": "hr"
                },
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**系统可用性**: {report.get('availability', '99.9%')}\n**平均响应时间**: {report.get('avg_latency', '50ms')}\n**错误率**: {report.get('error_rate', '0.1%')}"
                    }
                },
                {
                    "tag": "hr"
                },
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**今日变更**:\n{report.get('changes', '无')}"
                    }
                },
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**待办事项**:\n{report.get('todos', '无')}"
                    }
                }
            ]
        }
        
        return await self.send_interactive(card)
    
    async def close(self):
        """关闭客户端"""
        await self.client.aclose()


# ─────────────────────────────────────────────────────────
# 工厂函数
# ─────────────────────────────────────────────────────────

def create_feishu_notifier(webhook_url: str, secret: Optional[str] = None) -> FeishuNotifier:
    """创建飞书通知器"""
    return FeishuNotifier(webhook_url, secret)
