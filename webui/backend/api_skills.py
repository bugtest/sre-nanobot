"""
Skills API

提供 Skills 管理和执行接口
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from skills.loader import SkillLoader

router = APIRouter(prefix="/api/skills", tags=["Skills"])

# 全局 Skills 加载器
_skill_loader: Optional[SkillLoader] = None


def get_skill_loader() -> SkillLoader:
    """获取或创建 Skills 加载器"""
    global _skill_loader
    if _skill_loader is None:
        _skill_loader = SkillLoader()
        # 加载配置
        config = {
            "enabled": ["sre_alert_handler", "sre_incident_analyzer"]
        }
        _skill_loader.load_config(config)
        _skill_loader.load_all_skills()
    return _skill_loader


class SkillExecutionRequest(BaseModel):
    """Skill 执行请求"""
    params: Dict[str, Any] = {}


class SkillConfigUpdate(BaseModel):
    """Skill 配置更新"""
    config: Dict[str, Any]


@router.get("")
async def list_skills():
    """获取所有 Skills"""
    loader = get_skill_loader()
    skills = loader.list_skills()
    return {"skills": skills}


@router.get("/{skill_name}")
async def get_skill_info(skill_name: str):
    """获取单个 Skill 信息"""
    loader = get_skill_loader()
    skill = loader.get_skill(skill_name)
    
    if not skill:
        raise HTTPException(status_code=404, detail=f"Skill '{skill_name}' 不存在")
    
    return skill.get_info()


@router.post("/{skill_name}/execute")
async def execute_skill(skill_name: str, request: SkillExecutionRequest):
    """执行 Skill"""
    import asyncio
    
    loader = get_skill_loader()
    skill = loader.get_skill(skill_name)
    
    if not skill:
        raise HTTPException(status_code=404, detail=f"Skill '{skill_name}' 不存在")
    
    try:
        # 执行 Skill
        result = await loader.execute_skill(skill_name, **request.params)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"执行失败：{str(e)}")


@router.get("/{skill_name}/status")
async def get_skill_status(skill_name: str):
    """获取 Skill 状态"""
    loader = get_skill_loader()
    skill = loader.get_skill(skill_name)
    
    if not skill:
        raise HTTPException(status_code=404, detail=f"Skill '{skill_name}' 不存在")
    
    return {
        "enabled": skill.enabled,
        "config": skill.config
    }


@router.put("/{skill_name}/config")
async def update_skill_config(skill_name: str, update: SkillConfigUpdate):
    """更新 Skill 配置"""
    loader = get_skill_loader()
    skill = loader.get_skill(skill_name)
    
    if not skill:
        raise HTTPException(status_code=404, detail=f"Skill '{skill_name}' 不存在")
    
    # 更新配置
    skill.config.update(update.config)
    
    return {"success": True}


@router.post("/{skill_name}/reload")
async def reload_skill(skill_name: str):
    """重新加载 Skill"""
    loader = get_skill_loader()
    
    success = loader.reload_skill(skill_name)
    
    if not success:
        raise HTTPException(status_code=500, detail="重新加载失败")
    
    return {"success": True}


@router.get("/status")
async def get_skills_status():
    """获取 Skills 整体状态"""
    loader = get_skill_loader()
    return loader.get_status()
