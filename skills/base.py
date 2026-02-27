"""
Skills 基类

所有 Skills 的基类，提供通用功能
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import logging
import yaml
from pathlib import Path

logger = logging.getLogger(__name__)


class BaseSkill(ABC):
    """Skills 基类"""
    
    # Skill 名称（唯一标识）
    name: str = "base_skill"
    
    # Skill 描述
    description: str = "Base Skill"
    
    # 版本号
    version: str = "1.0.0"
    
    # 作者
    author: str = "Unknown"
    
    # 是否启用
    enabled: bool = True
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化 Skill
        
        Args:
            config_path: 配置文件路径
        """
        self.config = {}
        self.logger = logging.getLogger(f"skill.{self.name}")
        
        # 加载配置
        if config_path:
            self.load_config(config_path)
        
        self.logger.info(f"Skill '{self.name}' v{self.version} 初始化完成")
    
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """
        加载配置文件
        
        Args:
            config_path: 配置文件路径（YAML）
        
        Returns:
            配置字典
        """
        try:
            config_file = Path(config_path)
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    self.config = yaml.safe_load(f)
                self.logger.info(f"加载配置：{config_path}")
            else:
                self.logger.warning(f"配置文件不存在：{config_path}")
        except Exception as e:
            self.logger.error(f"加载配置失败：{e}")
        
        return self.config
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """
        获取配置项
        
        Args:
            key: 配置键
            default: 默认值
        
        Returns:
            配置值
        """
        return self.config.get(key, default)
    
    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        执行 Skill
        
        Args:
            **kwargs: 执行参数
        
        Returns:
            执行结果
        """
        pass
    
    async def validate(self, **kwargs) -> tuple[bool, Optional[str]]:
        """
        验证输入参数
        
        Args:
            **kwargs: 输入参数
        
        Returns:
            (是否有效，错误信息)
        """
        return True, None
    
    async def cleanup(self):
        """清理资源（可选）"""
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """
        获取 Skill 信息
        
        Returns:
            Skill 信息字典
        """
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "author": self.author,
            "enabled": self.enabled,
            "config": self.config
        }
    
    def __repr__(self) -> str:
        return f"Skill(name={self.name}, version={self.version}, enabled={self.enabled})"
