#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试脚本 - 验证所有连接和配置
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()


def test_sqlite():
    """测试SQLite连接"""
    print("\n" + "="*60)
    print("🔍 测试 SQLite 数据库连接...")
    print("="*60)

    try:
        from modules.sqlite_manager import SQLiteManager
        sm = SQLiteManager()

        # 测试读取数据
        users = sm.get_all_users()
        stats = sm.get_stats()

        print("✅ SQLite 数据库连接成功！")
        print(f"   • 当前用户数: {stats['total_users']}")
        print(f"   • 微信用户: {stats['wechat_users']}")
        print(f"   • QQ用户: {stats['qq_users']}")
        print(f"   • 总反馈数: {stats['feedback_count']}")

        return True

    except Exception as e:
        print(f"❌ SQLite 连接失败: {e}")
        return False


def test_wechat():
    """测试微信配置"""
    print("\n" + "="*60)
    print("🔍 测试 企业微信 配置...")
    print("="*60)

    try:
        corp_id = os.getenv('WECHAT_CORP_ID')
        agent_id = os.getenv('WECHAT_AGENT_ID')
        secret = os.getenv('WECHAT_SECRET')

        if not all([corp_id, agent_id, secret]):
            print("⚠️  缺少企业微信配置")
            return False

        # TODO: 调用WeChat API获取access_token来验证
        print("✅ 企业微信配置已填写")
        print(f"   • CorpID: {corp_id[:10]}...")
        print(f"   • AgentID: {agent_id}")
        print(f"   • Secret: {secret[:10]}...")

        return True

    except Exception as e:
        print(f"❌ 企业微信配置检查失败: {e}")
        return False


def test_rewards():
    """测试激励系统"""
    print("\n" + "="*60)
    print("🔍 测试 激励系统...")
    print("="*60)

    try:
        # 先确保数据库存在
        from modules.sqlite_manager import SQLiteManager
        sm = SQLiteManager()

        from modules.rewards import RewardCalculator
        rc = RewardCalculator()

        stats = rc.get_reward_stat()

        print("✅ 激励系统初始化成功！")
        print(f"   • 总积分: {stats['total_points']}")
        print(f"   • 已发放: {stats['distributed_count']}")
        print(f"   • 待发放: {stats['pending_count']}")
        print(f"   • 平均积分: {stats['avg_points']}")

        return True

    except Exception as e:
        print(f"❌ 激励系统初始化失败: {e}")
        return False


def test_analytics():
    """测试分析引擎"""
    print("\n" + "="*60)
    print("🔍 测试 分析引擎...")
    print("="*60)

    try:
        # 先确保数据库存在
        from modules.sqlite_manager import SQLiteManager
        sm = SQLiteManager()

        from modules.analytics import AnalyticsEngine
        ae = AnalyticsEngine()

        print("✅ 分析引擎初始化成功！")
        print("   • 周报生成功能：可用")
        print("   • 数据分析功能：可用")

        return True

    except Exception as e:
        print(f"❌ 分析引擎初始化失败: {e}")
        return False


def test_all():
    """测试所有连接"""
    print("\n" + "="*70)
    print("🚀 P-001 邀测招募系统 - 完整性检查")
    print("="*70)

    results = {
        'SQLite数据库': test_sqlite(),
        '企业微信': test_wechat(),
        '激励系统': test_rewards(),
        '分析引擎': test_analytics(),
    }

    # 汇总结果
    print("\n" + "="*70)
    print("📋 检查结果汇总")
    print("="*70)

    success_count = 0
    for component, status in results.items():
        status_text = "✅ 正常" if status else "❌ 异常"
        print(f"{component:<20} {status_text}")
        if status:
            success_count += 1

    print("="*70)
    print(f"总体状态: {success_count}/{len(results)} 组件正常")

    if success_count == len(results):
        print("\n✨ 所有检查通过！系统已准备好启动。")
        print("运行: python main.py")
        return 0
    else:
        print("\n⚠️  部分组件有问题，请检查配置。")
        return 1


if __name__ == '__main__':
    sys.exit(test_all())
