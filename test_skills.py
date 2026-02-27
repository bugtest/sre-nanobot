#!/usr/bin/env python3
"""
Skills 测试脚本

测试 Skills 框架和告警处理技能
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from skills.loader import SkillLoader
from skills.base import BaseSkill


# 测试数据
TEST_ALERTS = [
    {
        "name": "PodCrashLooping",
        "severity": "P1",
        "namespace": "production",
        "pod": "api-service-6d8f9c7b5-abc12",
        "deployment": "api-service",
        "description": "Pod 在 5 分钟内重启 5 次"
    },
    {
        "name": "HighCPUUsage",
        "severity": "P2",
        "namespace": "production",
        "service": "api-service",
        "description": "CPU 使用率超过 85%"
    },
    {
        "name": "HighMemoryUsage",
        "severity": "P2",
        "namespace": "production",
        "pod": "web-frontend-xyz98",
        "description": "内存使用率超过 90%"
    },
    {
        "name": "ServiceUnavailable",
        "severity": "P0",
        "namespace": "production",
        "service": "payment-service",
        "description": "支付服务不可用"
    }
]


async def test_skill_loader():
    """测试 Skills 加载器"""
    print("=" * 60)
    print("测试 1: Skills 加载器")
    print("=" * 60)
    print()
    
    try:
        # 创建加载器
        loader = SkillLoader()
        print("✅ Skills 加载器创建成功")
        
        # 加载配置
        config = {
            "enabled": ["sre_alert_handler"],
            "sre_alert_handler": {
                "auto_approve": {"enabled": True, "max_severity": "P2"},
                "notification": {"enabled": True, "channel": "feishu"}
            }
        }
        loader.load_config(config)
        print("✅ 配置加载成功")
        
        # 加载所有 Skills
        loaded = loader.load_all_skills()
        print(f"✅ 已加载 Skills: {loaded}")
        
        # 列出 Skills
        skills = loader.list_skills()
        print(f"✅ Skills 列表：{len(skills)} 个")
        for skill in skills:
            print(f"   - {skill['name']} v{skill['version']}")
        
        # 获取状态
        status = loader.get_status()
        print(f"✅ Skills 状态：{status}")
        
        print()
        print("✅ Skills 加载器测试通过")
        return True, loader
    
    except Exception as e:
        print(f"❌ Skills 加载器测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False, None


async def test_alert_handler(loader: SkillLoader):
    """测试告警处理技能"""
    print("=" * 60)
    print("测试 2: 告警处理技能")
    print("=" * 60)
    print()
    
    if not loader.get_skill('sre_alert_handler'):
        print("❌ 告警处理技能未加载")
        return False
    
    results = []
    
    for i, alert in enumerate(TEST_ALERTS, 1):
        print(f"--- 测试告警 {i}: {alert['name']} ({alert['severity']}) ---")
        
        try:
            result = await loader.execute_skill(
                'sre_alert_handler',
                alert=alert,
                auto_approve=True,
                notification=False
            )
            
            if result.get('success'):
                print(f"✅ 处理成功")
                print(f"   告警 ID: {result.get('alert_id')}")
                print(f"   根因：{result.get('analysis', {}).get('root_cause', 'N/A')}")
                print(f"   预案：{result.get('action', {}).get('runbook', 'N/A')}")
                print(f"   批准：{result.get('action', {}).get('approved', False)}")
                print(f"   执行：{result.get('action', {}).get('executed', False)}")
                results.append(True)
            else:
                print(f"❌ 处理失败：{result.get('error', 'Unknown')}")
                results.append(False)
        
        except Exception as e:
            print(f"❌ 执行异常：{e}")
            results.append(False)
        
        print()
    
    passed = sum(results)
    total = len(results)
    print(f"告警处理测试：{passed}/{total} 通过")
    
    return passed == total


async def test_skill_validation():
    """测试技能验证"""
    print("=" * 60)
    print("测试 3: 技能验证")
    print("=" * 60)
    print()
    
    try:
        loader = SkillLoader()
        config = {"enabled": ["sre_alert_handler"]}
        loader.load_config(config)
        loader.load_all_skills()
        
        skill = loader.get_skill('sre_alert_handler')
        
        # 测试有效告警
        is_valid, error = await skill.validate(
            alert={"name": "TestAlert", "severity": "P1"}
        )
        print(f"有效告警验证：{'✅' if is_valid else '❌'}")
        
        # 测试无效告警（缺少名称）
        is_valid, error = await skill.validate(
            alert={"severity": "P1"}
        )
        print(f"无效告警验证（无名称）：{'✅' if not is_valid else '❌'}")
        
        # 测试无效告警（缺少 severity）
        is_valid, error = await skill.validate(
            alert={"name": "TestAlert"}
        )
        print(f"无效告警验证（无 severity）：{'✅' if not is_valid else '❌'}")
        
        # 测试无效告警（空对象）
        is_valid, error = await skill.validate()
        print(f"无效告警验证（空对象）：{'✅' if not is_valid else '❌'}")
        
        print()
        print("✅ 技能验证测试通过")
        return True
    
    except Exception as e:
        print(f"❌ 技能验证测试失败：{e}")
        return False


async def test_skill_info():
    """测试技能信息"""
    print("=" * 60)
    print("测试 4: 技能信息")
    print("=" * 60)
    print()
    
    try:
        loader = SkillLoader()
        config = {"enabled": ["sre_alert_handler"]}
        loader.load_config(config)
        loader.load_all_skills()
        
        skill = loader.get_skill('sre_alert_handler')
        info = skill.get_info()
        
        print("技能信息:")
        print(f"  名称：{info['name']}")
        print(f"  描述：{info['description']}")
        print(f"  版本：{info['version']}")
        print(f"  作者：{info['author']}")
        print(f"  启用：{info['enabled']}")
        print(f"  配置：{info['config']}")
        
        print()
        print("✅ 技能信息测试通过")
        return True
    
    except Exception as e:
        print(f"❌ 技能信息测试失败：{e}")
        return False


async def run_all_tests():
    """运行所有测试"""
    print()
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 18 + "SRE-NanoBot Skills 测试" + " " * 15 + "║")
    print("╚" + "═" * 58 + "╝")
    print()
    
    results = []
    loader = None
    
    # 测试 1: Skills 加载器
    print("=" * 60)
    print("测试 1: Skills 加载器")
    print("=" * 60)
    print()
    
    try:
        loader = SkillLoader()
        print("✅ Skills 加载器创建成功")
        
        config = {
            "enabled": ["sre_alert_handler"],
            "sre_alert_handler": {
                "auto_approve": {"enabled": True, "max_severity": "P2"},
                "notification": {"enabled": True, "channel": "feishu"}
            }
        }
        loader.load_config(config)
        print("✅ 配置加载成功")
        
        loaded = loader.load_all_skills()
        print(f"✅ 已加载 Skills: {loaded}")
        
        skills = loader.list_skills()
        print(f"✅ Skills 列表：{len(skills)} 个")
        for skill in skills:
            print(f"   - {skill['name']} v{skill['version']}")
        
        results.append(True)
    except Exception as e:
        print(f"❌ Skills 加载器测试失败：{e}")
        results.append(False)
    
    print()
    
    # 测试 2: 告警处理
    if loader:
        print("=" * 60)
        print("测试 2: 告警处理技能")
        print("=" * 60)
        print()
        
        for i, alert in enumerate(TEST_ALERTS, 1):
            print(f"--- 测试告警 {i}: {alert['name']} ({alert['severity']}) ---")
            
            try:
                result = await loader.execute_skill(
                    'sre_alert_handler',
                    alert=alert,
                    auto_approve=True,
                    notification=False
                )
                
                if result.get('success'):
                    print(f"✅ 处理成功")
                    print(f"   告警 ID: {result.get('alert_id')}")
                    print(f"   根因：{result.get('analysis', {}).get('root_cause', 'N/A')}")
                    print(f"   预案：{result.get('action', {}).get('runbook', 'N/A')}")
                    print(f"   批准：{result.get('action', {}).get('approved', False)}")
                    results.append(True)
                else:
                    print(f"❌ 处理失败：{result.get('error', 'Unknown')}")
                    results.append(False)
            
            except Exception as e:
                print(f"❌ 执行异常：{e}")
                results.append(False)
            
            print()
    else:
        print("⏭️  跳过告警处理测试（加载器未初始化）")
    
    # 测试 3: 技能验证
    print("=" * 60)
    print("测试 3: 技能验证")
    print("=" * 60)
    print()
    
    if loader:
        skill = loader.get_skill('sre_alert_handler')
        if skill:
            # 测试有效告警
            is_valid, error = await skill.validate(alert={"name": "TestAlert", "severity": "P1"})
            print(f"有效告警验证：{'✅' if is_valid else '❌'}")
            results.append(is_valid)
            
            # 测试无效告警
            is_valid, error = await skill.validate(alert={"severity": "P1"})
            print(f"无效告警验证（无名称）：{'✅' if not is_valid else '❌'}")
            results.append(not is_valid)
        else:
            print("⏭️  跳过技能验证测试（技能未加载）")
    else:
        print("⏭️  跳过技能验证测试（加载器未初始化）")
    
    print()
    
    # 总结
    print("=" * 60)
    print("测试总结")
    print("=" * 60)
    print()
    
    passed = sum(results)
    total = len(results)
    
    print(f"总测试数：{total}")
    print(f"✅ 通过：{passed}")
    print(f"❌ 失败：{total - passed}")
    print()
    
    if passed == total:
        print("🎉 所有测试通过！")
        print()
        print("下一步:")
        print("1. 集成到 WebUI")
        print("2. 开发更多 Skills")
        print("3. 生产环境测试")
    else:
        print("⚠️  部分测试失败，请检查日志")
    
    print()
    print("=" * 60)
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
