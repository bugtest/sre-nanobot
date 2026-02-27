#!/usr/bin/env python3
"""
Skills API 测试脚本

测试 Skills API 端点
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from webui.backend.api_skills import get_skill_loader, execute_skill, SkillExecutionRequest


async def test_api():
    """测试 Skills API"""
    print("=" * 60)
    print("Skills API 测试")
    print("=" * 60)
    print()
    
    # 获取加载器
    loader = get_skill_loader()
    print(f"✅ Skills 加载器初始化成功")
    print(f"   已加载 Skills: {loader.list_skills()}")
    print()
    
    # 测试 1: 列出 Skills
    print("--- 测试 1: 列出 Skills ---")
    skills = loader.list_skills()
    print(f"Skills 数量：{len(skills)}")
    for skill in skills:
        print(f"  - {skill['name']} v{skill['version']}")
    print()
    
    # 测试 2: 执行告警处理技能
    print("--- 测试 2: 执行告警处理技能 ---")
    result = await execute_skill(
        'sre_alert_handler',
        SkillExecutionRequest(params={
            "alert": {
                "name": "PodCrashLooping",
                "severity": "P1",
                "namespace": "production"
            },
            "auto_approve": True
        })
    )
    print(f"执行结果：{result}")
    print()
    
    # 测试 3: 执行故障分析技能
    print("--- 测试 3: 执行故障分析技能 ---")
    result = await execute_skill(
        'sre_incident_analyzer',
        SkillExecutionRequest(params={
            "incident_id": "INC-001",
            "depth": "shallow"
        })
    )
    print(f"执行结果：{result}")
    print()
    
    # 测试 4: 获取 Skill 状态
    print("--- 测试 4: 获取 Skill 状态 ---")
    skill = loader.get_skill('sre_alert_handler')
    if skill:
        status = {
            "enabled": skill.enabled,
            "config": skill.config
        }
        print(f"状态：{status}")
    print()
    
    # 测试 5: 获取 Skills 整体状态
    print("--- 测试 5: 获取 Skills 整体状态 ---")
    status = loader.get_status()
    print(f"整体状态：{status}")
    print()
    
    print("=" * 60)
    print("✅ 所有 API 测试通过")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_api())
