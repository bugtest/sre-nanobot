"""
SRE Agent 基类
"""

from abc import ABC, abstractmethod
from typing import Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class TaskResult:
    """任务执行结果"""
    success: bool
    output: Any = None
    error: Optional[str] = None
    metadata: dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class SREAgent(ABC):
    """SRE Agent 基类"""
    
    # Agent 名称（唯一标识）
    name: str = "base_agent"
    
    # Agent 描述
    description: str = "Base SRE Agent"
    
    # 系统提示词
    system_prompt: str = """
    你是一个 SRE 运维 Agent，负责协助运维工作。
    
    工作原则：
    1. 操作前确认影响范围
    2. 生产环境操作需要审批
    3. 所有操作必须可审计
    4. 优先使用只读操作
    5. 发现问题及时报告
    """
    
    # 工具列表
    tools: list[str] = []
    
    # 是否需要审批
    requires_approval: bool = False
    
    # 审批级别（low/medium/high）
    approval_level: str = "low"
    
    def __init__(self):
        """初始化 Agent"""
        self.initialized = False
        self.context = {}
    
    async def initialize(self) -> None:
        """初始化 Agent（可重写）"""
        self.initialized = True
    
    @abstractmethod
    async def execute(self, task: dict) -> TaskResult:
        """
        执行任务
        
        Args:
            task: 任务字典，包含 action 和 params
        
        Returns:
            TaskResult: 执行结果
        """
        pass
    
    async def validate(self, task: dict) -> tuple[bool, Optional[str]]:
        """
        验证任务参数
        
        Args:
            task: 任务字典
        
        Returns:
            (是否有效，错误信息)
        """
        return True, None
    
    async def rollback(self, task: dict, result: TaskResult) -> TaskResult:
        """
        回滚操作（可重写）
        
        Args:
            task: 原始任务
            result: 执行结果
        
        Returns:
            TaskResult: 回滚结果
        """
        return TaskResult(
            success=True,
            output="无回滚操作"
        )
    
    def get_status(self) -> dict:
        """获取 Agent 状态"""
        return {
            "name": self.name,
            "description": self.description,
            "initialized": self.initialized,
            "tools": self.tools,
            "requires_approval": self.requires_approval,
            "approval_level": self.approval_level
        }
