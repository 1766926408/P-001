# -*- coding: utf-8 -*-
"""
激励系统模块
负责积分计算、激励发放、用户奖励管理
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List
from .sqlite_manager import SQLiteManager as SheetManager

logger = logging.getLogger(__name__)


class RewardCalculator:
    """激励计算器"""

    # 激励规则
    REWARD_RULES = {
        'join_group': 5,           # 加入群聊 +5积分
        'submit_feedback': 10,     # 提交反馈 +10积分
        'invite_friend': 15,       # 邀请朋友 +15积分/人
        'feedback_selected': 20,   # 反馈被采用 +20积分
        'weekly_active': 5,        # 周活跃 +5积分
    }

    # 积分兑换规则
    REWARD_EXCHANGE = {
        50: '产品8折优惠券',
        100: '产品免费使用1个月',
        200: '产品高级版本升级',
        500: '产品定制功能咨询',
    }

    def __init__(self):
        """初始化"""
        self.sheet_manager = SheetManager()
        logger.info("✅ 激励计算器初始化完成")

    def calculate_daily_rewards(self) -> Dict:
        """每日激励计算"""
        try:
            logger.info("🧮 开始计算每日激励...")

            users = self.sheet_manager.get_all_users()
            reward_summary = {
                'processed': 0,
                'total_points': 0,
                'details': []
            }

            for user in users:
                user_id = user.get('用户ID')
                points = 0
                details = []

                # 规则1：加入群聊
                if user.get('群聊状态') == '已加入':
                    points += self.REWARD_RULES['join_group']
                    details.append('加入群聊')

                # 规则2：已反馈
                if user.get('群聊状态') == '已反馈':
                    points += self.REWARD_RULES['submit_feedback']
                    details.append('提交反馈')

                # 规则3：邀请数量
                invites = int(user.get('邀请数量', 0))
                if invites > 0:
                    invite_points = invites * self.REWARD_RULES['invite_friend']
                    points += invite_points
                    details.append(f"邀请{invites}位")

                # 更新用户积分
                if points > 0:
                    self.sheet_manager.update_user(
                        user_id,
                        激励积分=points
                    )
                    reward_summary['processed'] += 1
                    reward_summary['total_points'] += points
                    reward_summary['details'].append({
                        'user_id': user_id,
                        'nickname': user.get('昵称'),
                        'points': points,
                        'details': ', '.join(details)
                    })

            logger.info(f"✅ 激励计算完成: 处理{reward_summary['processed']}个用户, 总积分{reward_summary['total_points']}")
            return reward_summary

        except Exception as e:
            logger.error(f"❌ 激励计算失败: {e}")
            return {}

    def distribute_rewards(self) -> Dict:
        """发放激励奖励"""
        try:
            logger.info("🎁 开始发放激励...")

            users = self.sheet_manager.get_all_users()
            distribution_summary = {
                'processed': 0,
                'sent': 0,
                'details': []
            }

            for user in users:
                user_id = user.get('用户ID')
                points = int(user.get('激励积分', 0))
                status = user.get('激励发放', '')

                # 检查是否已发放
                if status == '已发放':
                    continue

                # 检查是否有待发放的积分
                if points > 0:
                    # 发送通知
                    reward_message = self._generate_reward_message(user, points)
                    success = self._send_reward_notification(user, reward_message)

                    if success:
                        # 标记为已发放
                        self.sheet_manager.update_user(
                            user_id,
                            激励发放='已发放'
                        )
                        distribution_summary['sent'] += 1
                        distribution_summary['details'].append({
                            'user_id': user_id,
                            'nickname': user.get('昵称'),
                            'points': points,
                            'status': '已发放'
                        })

                distribution_summary['processed'] += 1

            logger.info(f"✅ 激励发放完成: 处理{distribution_summary['processed']}个, 已发放{distribution_summary['sent']}个")
            return distribution_summary

        except Exception as e:
            logger.error(f"❌ 激励发放失败: {e}")
            return {}

    def _generate_reward_message(self, user: Dict, points: int) -> str:
        """生成激励消息"""
        nickname = user.get('昵称', '用户')
        source = user.get('来源渠道', 'unknown')

        message = f"""
🎉 恭喜！{nickname}

您已获得 {points} 积分！

✨ 您可以用积分兑换:
"""

        # 添加兑换选项
        for threshold, reward in sorted(self.REWARD_EXCHANGE.items()):
            if points >= threshold:
                message += f"✅ {threshold}积分: {reward}\n"
            else:
                message += f"⏳ {threshold}积分: {reward} (还需{threshold - points}积分)\n"

        message += """
💡 继续参与反馈、邀请朋友，获得更多积分！

感谢支持！❤️
"""
        return message

    def _send_reward_notification(self, user: Dict, message: str) -> bool:
        """发送激励通知"""
        try:
            source = user.get('来源渠道', 'unknown')

            # TODO: 根据来源发送不同渠道的通知
            # 这里需要调用微信/QQ机器人发送消息

            if source == 'wechat':
                # from modules.wechat_bot import send_wechat_message
                # return send_wechat_message(user['昵称'], message)
                logger.info(f"📨 [WeChat] 向 {user['昵称']} 发送激励通知")
                return True

            elif source == 'qq':
                # from modules.qq_bot import send_qq_message
                # return send_qq_message(user['昵称'], message)
                logger.info(f"📨 [QQ] 向 {user['昵称']} 发送激励通知")
                return True

            else:
                logger.warning(f"⚠️ 未知来源: {source}")
                return False

        except Exception as e:
            logger.error(f"❌ 发送通知失败: {e}")
            return False

    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """获取积分排行榜"""
        try:
            users = self.sheet_manager.get_all_users()
            sorted_users = sorted(
                users,
                key=lambda x: int(x.get('激励积分', 0)),
                reverse=True
            )

            leaderboard = []
            for idx, user in enumerate(sorted_users[:limit], start=1):
                leaderboard.append({
                    'rank': idx,
                    'nickname': user.get('昵称'),
                    'points': user.get('激励积分'),
                    'source': user.get('来源渠道')
                })

            return leaderboard

        except Exception as e:
            logger.error(f"❌ 获取排行榜失败: {e}")
            return []

    def print_leaderboard(self):
        """打印积分排行榜"""
        leaderboard = self.get_leaderboard()

        print("\n" + "="*60)
        print("🏆 邀测用户积分排行榜")
        print("="*60)
        print(f"{'排名':<5} {'昵称':<15} {'积分':<10} {'来源':<10}")
        print("-"*60)

        for item in leaderboard:
            print(f"{item['rank']:<5} {item['nickname']:<15} {item['points']:<10} {item['source']:<10}")

        print("="*60 + "\n")

    def get_reward_stat(self) -> Dict:
        """获取激励统计"""
        try:
            users = self.sheet_manager.get_all_users()
            total_points = sum(int(u.get('激励积分', 0)) for u in users)
            distributed = len([u for u in users if u.get('激励发放') == '已发放'])

            return {
                'total_points': total_points,
                'distributed_count': distributed,
                'pending_count': len(users) - distributed,
                'avg_points': total_points // max(len(users), 1)
            }

        except Exception as e:
            logger.error(f"❌ 获取激励统计失败: {e}")
            return {}


if __name__ == '__main__':
    # 测试
    logging.basicConfig(level=logging.INFO)

    rc = RewardCalculator()
    print("计算激励...")
    rc.calculate_daily_rewards()

    print("\n发放激励...")
    rc.distribute_rewards()

    print("\n显示排行榜...")
    rc.print_leaderboard()

    print("\n激励统计...")
    print(rc.get_reward_stat())
