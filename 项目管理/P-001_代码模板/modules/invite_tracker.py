# -*- coding: utf-8 -*-
"""
邀请链接追踪模块
负责邀请链接生成、追踪、转化统计
"""

import logging
import uuid
from typing import Dict, Optional
from .sqlite_manager import SQLiteManager

logger = logging.getLogger(__name__)


class InviteTracker:
    """邀请追踪器"""

    def __init__(self, invite_domain: str = 'https://invite.yourapp.com'):
        """初始化"""
        self.db = SQLiteManager()
        self.invite_domain = invite_domain
        logger.info("✅ 邀请追踪器初始化完成")

    def generate_invite_link(self, user_id: str) -> str:
        """生成邀请链接"""
        try:
            invite_code = str(uuid.uuid4())[:12]
            invite_link = f"{self.invite_domain}/{invite_code}"
            logger.info(f"🔗 生成邀请链接: {invite_code}")
            return invite_link

        except Exception as e:
            logger.error(f"❌ 生成邀请链接失败: {e}")
            return None

    def track_invite_click(self, invite_code: str, inviter_id: str) -> bool:
        """追踪邀请链接点击"""
        try:
            # 查询邀请码对应的邀请者
            invite_link = f"{self.invite_domain}/{invite_code}"

            # TODO: 实现邀请链接到数据库的映射
            # 这里需要维护一个invite_code -> user_id的映射表

            logger.info(f"📊 记录邀请点击: {invite_code}")
            return True

        except Exception as e:
            logger.error(f"❌ 追踪邀请失败: {e}")
            return False

    def mark_invite_converted(self, inviter_id: str, invitee_id: str) -> bool:
        """标记邀请为已转化"""
        try:
            # 更新Sheet中的邀请追踪数据
            self.sheet_manager.mark_invitation_converted(f"{self.invite_domain}/{inviter_id}_{invitee_id}")
            logger.info(f"✅ 邀请已转化: {inviter_id} → {invitee_id}")
            return True

        except Exception as e:
            logger.error(f"❌ 标记邀请失败: {e}")
            return False

    def get_invite_stats(self, user_id: str) -> Dict:
        """获取用户的邀请统计"""
        try:
            users = self.sheet_manager.get_all_users()
            user = self.sheet_manager.get_user_by_id(user_id)

            if not user:
                return {}

            # 获取此用户邀请的人数
            invites = int(user.get('邀请数量', 0))

            return {
                'user_id': user_id,
                'nickname': user.get('昵称'),
                'total_invites': invites,
                'invite_link': user.get('邀请链接'),
            }

        except Exception as e:
            logger.error(f"❌ 获取邀请统计失败: {e}")
            return {}

    def get_top_inviters(self, limit: int = 10) -> list:
        """获取邀请排行榜"""
        try:
            users = self.sheet_manager.get_all_users()

            # 按邀请数排序
            sorted_users = sorted(
                users,
                key=lambda x: int(x.get('邀请数量', 0)),
                reverse=True
            )

            inviters = []
            for idx, user in enumerate(sorted_users[:limit], start=1):
                if int(user.get('邀请数量', 0)) > 0:
                    inviters.append({
                        'rank': idx,
                        'nickname': user.get('昵称'),
                        'invites': int(user.get('邀请数量', 0)),
                        'reward': int(user.get('邀请数量', 0)) * 15  # 每个邀请15积分
                    })

            return inviters

        except Exception as e:
            logger.error(f"❌ 获取邀请排行榜失败: {e}")
            return []

    def print_invite_leaderboard(self):
        """打印邀请排行榜"""
        inviters = self.get_top_inviters()

        print("\n" + "="*70)
        print("🎖️  邀请排行榜 - 谁邀请了最多的朋友？")
        print("="*70)
        print(f"{'排名':<5} {'昵称':<15} {'邀请数':<10} {'可获积分':<10}")
        print("-"*70)

        if not inviters:
            print("暂无数据")
        else:
            for item in inviters:
                print(f"{item['rank']:<5} {item['nickname']:<15} {item['invites']:<10} {item['reward']:<10}")

        print("="*70 + "\n")


if __name__ == '__main__':
    # 测试
    logging.basicConfig(level=logging.INFO)

    it = InviteTracker()
    print("显示邀请排行榜...")
    it.print_invite_leaderboard()
