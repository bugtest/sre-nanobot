"""
Skills 加载器

负责加载和管理所有 Skills
"""

import importlib
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from .base import BaseSkill

logger = logging.getLogger(__name__)


class SkillLoader:
    """Skills 加载器"""
    
    def __init__(self, skills_dir: str = None):
        """
        初始化 Skills 加载器
        
        Args:
            skills_dir: Skills 目录路径
        """
        self.skills_dir = Path(__file__).parent if not skills_dir else Path(skills_dir)
        self.skills: Dict[str, BaseSkill] = {}
        self.config: Dict[str, Any] = {}
        
        logger.info(f"Skills 加载器初始化完成，目录：{self.skills_dir}")
    
    def load_config(self, config: Dict[str, Any]):
        """
        加载配置
        
        Args:
            config: Skills 配置
        """
        self.config = config
        logger.info(f"加载 Skills 配置：{list(config.keys())}")
    
    def load_all_skills(self) -> List[str]:
        """
        加载所有启用的 Skills
        
        Returns:
            已加载的 Skill 名称列表
        """
        loaded = []
        enabled_skills = self.config.get('enabled', [])
        
        for skill_name in enabled_skills:
            try:
                if self.load_skill(skill_name):
                    loaded.append(skill_name)
            except Exception as e:
                logger.error(f"加载 Skill '{skill_name}' 失败：{e}")
        
        logger.info(f"已加载 {len(loaded)} 个 Skills: {loaded}")
        return loaded
    
    def load_skill(self, skill_name: str) -> bool:
        """
        加载单个 Skill
        
        Args:
            skill_name: Skill 名称
        
        Returns:
            是否加载成功
        """
        try:
            # 检查 Skill 目录
            skill_dir = self.skills_dir / skill_name
            if not skill_dir.exists():
                logger.error(f"Skill 目录不存在：{skill_dir}")
                return False
            
            # 检查 SKILL.md
            skill_md = skill_dir / "SKILL.md"
            if not skill_md.exists():
                logger.warning(f"Skill 说明文件不存在：{skill_md}")
            
            # 动态导入 handler 模块
            module_path = f"skills.{skill_name}.handler"
            try:
                module = importlib.import_module(module_path)
            except ImportError as e:
                logger.error(f"导入 Skill 模块失败：{e}")
                return False
            
            # 查找 Skill 类
            skill_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and issubclass(attr, BaseSkill) and attr != BaseSkill:
                    skill_class = attr
                    break
            
            if not skill_class:
                logger.error(f"未找到 Skill 类：{module_path}")
                return False
            
            # 实例化 Skill
            config_path = skill_dir / "config.yaml"
            skill_instance = skill_class(
                config_path=str(config_path) if config_path.exists() else None
            )
            
            # 检查是否启用
            if not skill_instance.enabled:
                logger.info(f"Skill '{skill_name}' 未启用，跳过")
                return False
            
            # 注册 Skill
            self.skills[skill_name] = skill_instance
            logger.info(f"✅ 加载 Skill: {skill_name} v{skill_instance.version}")
            
            return True
        
        except Exception as e:
            logger.error(f"加载 Skill '{skill_name}' 异常：{e}", exc_info=True)
            return False
    
    def get_skill(self, skill_name: str) -> Optional[BaseSkill]:
        """
        获取 Skill 实例
        
        Args:
            skill_name: Skill 名称
        
        Returns:
            Skill 实例或 None
        """
        return self.skills.get(skill_name)
    
    def list_skills(self) -> List[Dict[str, Any]]:
        """
        列出所有 Skills
        
        Returns:
            Skill 信息列表
        """
        return [skill.get_info() for skill in self.skills.values()]
    
    async def execute_skill(self, skill_name: str, **kwargs) -> Dict[str, Any]:
        """
        执行 Skill
        
        Args:
            skill_name: Skill 名称
            **kwargs: 执行参数
        
        Returns:
            执行结果
        """
        skill = self.get_skill(skill_name)
        
        if not skill:
            return {
                "success": False,
                "error": f"Skill '{skill_name}' 不存在"
            }
        
        try:
            # 验证参数
            is_valid, error = await skill.validate(**kwargs)
            if not is_valid:
                return {
                    "success": False,
                    "error": error
                }
            
            # 执行 Skill
            result = await skill.execute(**kwargs)
            
            logger.info(f"Skill '{skill_name}' 执行成功")
            return result
        
        except Exception as e:
            logger.error(f"Skill '{skill_name}' 执行失败：{e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def cleanup(self):
        """清理所有 Skills"""
        logger.info("清理 Skills...")
        for skill_name, skill in self.skills.items():
            try:
                await skill.cleanup()
                logger.info(f"清理 Skill: {skill_name}")
            except Exception as e:
                logger.error(f"清理 Skill '{skill_name}' 失败：{e}")
    
    def reload_skill(self, skill_name: str) -> bool:
        """
        热重载 Skill
        
        Args:
            skill_name: Skill 名称
        
        Returns:
            是否重载成功
        """
        logger.info(f"热重载 Skill: {skill_name}")
        
        # 卸载旧 Skill
        if skill_name in self.skills:
            del self.skills[skill_name]
        
        # 重新加载
        return self.load_skill(skill_name)
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取 Skills 状态
        
        Returns:
            状态信息
        """
        return {
            "total": len(self.skills),
            "skills": list(self.skills.keys()),
            "config": self.config
        }
