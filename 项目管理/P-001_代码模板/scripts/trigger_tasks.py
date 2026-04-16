#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手动触发任务脚本
用于调试和临时执行各类任务
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from dotenv import load_dotenv
import argparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()


def trigger_calculate_rewards():
    """手动触发激励计算"""
    print("\n🧮 手动触发激励计算...\n")

    from modules.rewards import RewardCalculator
    rc = RewardCalculator()
    result = rc.calculate_daily_rewards()

    print(f"\n✅ 激励计算完成")
    print(f"   • 处理用户数: {result.get('processed')}")
    print(f"   • 总积分: {result.get('total_points')}")
    print(f"   • 详情: {result.get('details')}\n")


def trigger_distribute_rewards():
    """手动触发激励发放"""
    print("\n🎁 手动触发激励发放...\n")

    from modules.rewards import RewardCalculator
    rc = RewardCalculator()
    result = rc.distribute_rewards()

    print(f"\n✅ 激励发放完成")
    print(f"   • 处理用户数: {result.get('processed')}")
    print(f"   • 已发放: {result.get('sent')}\n")


def trigger_sync_feedback():
    """手动触发反馈同步"""
    print("\n🔄 手动触发反馈同步...\n")

    from modules.sqlite_manager import SQLiteManager
    db = SQLiteManager()
    feedbacks = db.get_all_feedback()

    print(f"\n✅ 反馈数据加载完成")
    print(f"   • 总反馈数: {len(feedbacks)}")
    print(f"   • 最新反馈: {feedbacks[0] if feedbacks else 'N/A'}\n")
    db.close()


def trigger_generate_report():
    """手动触发周报生成"""
    print("\n📝 手动触发周报生成...\n")

    from modules.analytics import AnalyticsEngine
    ae = AnalyticsEngine()
    ae.print_report()


def trigger_backup_data():
    """手动触发数据备份"""
    print("\n💾 手动触发数据备份...\n")

    import shutil
    from datetime import datetime

    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = f'backups/recruitment_backup_{timestamp}.db'
        shutil.copy('recruitment.db', backup_path)
        print(f"\n✅ 数据备份完成: {backup_path}\n")
    except Exception as e:
        print(f"\n❌ 数据备份失败: {e}\n")


def show_stats():
    """显示实时统计"""
    print("\n📊 实时统计数据...\n")

    from modules.sqlite_manager import SQLiteManager
    db = SQLiteManager()
    stats = db.get_stats()

    print(f"📊 数据库统计:")
    print(f"   • 总用户数: {stats.get('total_users', 0)}")
    print(f"   • 总反馈数: {stats.get('total_feedbacks', 0)}")
    print(f"   • 总邀请数: {stats.get('total_invitations', 0)}")
    print()

    db.close()


def main():
    parser = argparse.ArgumentParser(
        description='P-001 邀测招募 - 手动触发任务',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例：
  python scripts/trigger_tasks.py --calculate-rewards
  python scripts/trigger_tasks.py --distribute-rewards
  python scripts/trigger_tasks.py --sync-feedback
  python scripts/trigger_tasks.py --generate-report
  python scripts/trigger_tasks.py --backup-data
  python scripts/trigger_tasks.py --stats
        '''
    )

    parser.add_argument(
        '--calculate-rewards',
        action='store_true',
        help='计算激励积分'
    )

    parser.add_argument(
        '--distribute-rewards',
        action='store_true',
        help='发放激励奖励'
    )

    parser.add_argument(
        '--sync-feedback',
        action='store_true',
        help='同步用户反馈'
    )

    parser.add_argument(
        '--generate-report',
        action='store_true',
        help='生成周报'
    )

    parser.add_argument(
        '--backup-data',
        action='store_true',
        help='备份数据'
    )

    parser.add_argument(
        '--stats',
        action='store_true',
        help='显示统计数据'
    )

    parser.add_argument(
        '--all',
        action='store_true',
        help='执行所有任务'
    )

    args = parser.parse_args()

    if not any(vars(args).values()):
        parser.print_help()
        return

    try:
        if args.calculate_rewards or args.all:
            trigger_calculate_rewards()

        if args.distribute_rewards or args.all:
            trigger_distribute_rewards()

        if args.sync_feedback or args.all:
            trigger_sync_feedback()

        if args.generate_report or args.all:
            trigger_generate_report()

        if args.backup_data or args.all:
            trigger_backup_data()

        if args.stats or args.all:
            show_stats()

        print("\n✅ 所有任务执行完成\n")

    except Exception as e:
        logger.error(f"❌ 执行失败: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
