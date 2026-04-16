#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
显示实时仪表板
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.WARNING)
load_dotenv()


def main():
    from modules.google_sheet import SheetManager, print_dashboard
    from modules.rewards import RewardCalculator
    from modules.invite_tracker import InviteTracker

    # 显示Google Sheet仪表板
    print_dashboard()

    # 显示积分排行榜
    rc = RewardCalculator()
    rc.print_leaderboard()

    # 显示邀请排行榜
    it = InviteTracker()
    it.print_invite_leaderboard()

    # 显示激励统计
    print("\n" + "="*60)
    print("💰 激励统计")
    print("="*60)
    reward_stats = rc.get_reward_stat()
    print(f"总积分: {reward_stats['total_points']}")
    print(f"已发放: {reward_stats['distributed_count']}")
    print(f"待发放: {reward_stats['pending_count']}")
    print(f"平均积分: {reward_stats['avg_points']}")
    print("="*60 + "\n")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)
