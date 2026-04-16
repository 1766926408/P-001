# -*- coding: utf-8 -*-
"""
企业微信机器人模块
支持发送消息、通知，无需企业认证也能用
"""

import requests
import logging
import os
from datetime import datetime
from typing import List, Optional

logger = logging.getLogger(__name__)


class WeChatBot:
    """企业微信机器人"""

    def __init__(self):
        """初始化企业微信机器人"""
        self.corp_id = os.getenv('WECHAT_CORP_ID')
        self.agent_id = os.getenv('WECHAT_AGENT_ID')
        self.secret = os.getenv('WECHAT_SECRET')
        self.token = None

        # 验证配置
        if not all([self.corp_id, self.agent_id, self.secret]):
            logger.warning("⚠️  缺少企业微信配置，消息发送功能不可用")
            return

        # 获取初始token
        self._refresh_token()

    def _refresh_token(self) -> bool:
        """获取或刷新access_token"""
        try:
            if not self.corp_id or not self.secret:
                return False

            url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"
            params = {
                'corpid': self.corp_id,
                'corpsecret': self.secret
            }

            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            if data.get('errcode') == 0:
                self.token = data.get('access_token')
                logger.info("✅ 企业微信Token获取成功")
                return True
            else:
                error_msg = data.get('errmsg', 'Unknown error')
                logger.error(f"❌ Token获取失败: {error_msg}")
                return False

        except Exception as e:
            logger.error(f"❌ Token刷新失败: {e}")
            return False

    def send_message(self, user_id: str, message: str) -> bool:
        """
        发送消息给指定用户

        Args:
            user_id: 用户ID或用户名
            message: 消息内容

        Returns:
            是否发送成功
        """
        try:
            if not self.token:
                if not self._refresh_token():
                    return False

            url = "https://qyapi.weixin.qq.com/cgi-bin/message/send"

            payload = {
                'touser': user_id,
                'agentid': int(self.agent_id),
                'msgtype': 'text',
                'text': {
                    'content': message
                },
                'safe': 0
            }

            params = {'access_token': self.token}
            response = requests.post(url, json=payload, params=params, timeout=10)
            data = response.json()

            if data.get('errcode') == 0:
                logger.info(f"✅ 消息已发送给 {user_id}")
                return True
            else:
                error_msg = data.get('errmsg', 'Unknown error')
                logger.error(f"❌ 消息发送失败 ({user_id}): {error_msg}")
                return False

        except Exception as e:
            logger.error(f"❌ 发送消息失败: {e}")
            return False

    def send_to_party(self, party_id: str, message: str) -> bool:
        """
        发送消息到部门

        Args:
            party_id: 部门ID
            message: 消息内容

        Returns:
            是否发送成功
        """
        try:
            if not self.token:
                if not self._refresh_token():
                    return False

            url = "https://qyapi.weixin.qq.com/cgi-bin/message/send"

            payload = {
                'toparty': party_id,
                'agentid': int(self.agent_id),
                'msgtype': 'text',
                'text': {
                    'content': message
                },
                'safe': 0
            }

            params = {'access_token': self.token}
            response = requests.post(url, json=payload, params=params, timeout=10)
            data = response.json()

            if data.get('errcode') == 0:
                logger.info(f"✅ 消息已发送到部门 {party_id}")
                return True
            else:
                error_msg = data.get('errmsg', 'Unknown error')
                logger.error(f"❌ 消息发送失败 (部门{party_id}): {error_msg}")
                return False

        except Exception as e:
            logger.error(f"❌ 发送消息失败: {e}")
            return False

    def send_batch(self, user_ids: List[str], message: str) -> int:
        """
        批量发送消息

        Args:
            user_ids: 用户ID列表
            message: 消息内容

        Returns:
            成功发送的数量
        """
        success_count = 0

        for user_id in user_ids:
            if self.send_message(user_id, message):
                success_count += 1

        logger.info(f"✅ 批量发送完成: {success_count}/{len(user_ids)} 成功")
        return success_count

    def send_reward_notification(self, user_id: str, nickname: str, points: int) -> bool:
        """
        发送激励通知

        Args:
            user_id: 用户ID
            nickname: 用户昵称
            points: 获得的积分数

        Returns:
            是否发送成功
        """
        message = f"""
🎉 恭喜，{nickname}！

您已获得 {points} 积分！

✨ 积分兑换规则：
  • 50积分 → 产品8折优惠券
  • 100积分 → 产品免费使用1个月
  • 200积分 → 产品高级版本升级
  • 500积分 → 产品定制功能咨询

💡 继续参与反馈、邀请朋友，获得更多积分吧！

感谢支持！❤️
"""
        return self.send_message(user_id, message.strip())

    def send_weekly_report(self, user_id: str, report_data: dict) -> bool:
        """
        发送周报

        Args:
            user_id: 用户ID
            report_data: 报告数据

        Returns:
            是否发送成功
        """
        message = f"""
📊 邀测招募周报

📈 本周数据：
  • 新增用户：{report_data.get('new_users', 0)}
  • 总用户数：{report_data.get('total_users', 0)}
  • 反馈数量：{report_data.get('feedback_count', 0)}
  • 反馈率：{report_data.get('feedback_rate', '0%')}

🏆 用户排行 Top 3：
{self._format_ranking(report_data.get('top_users', []))}

💬 热门反馈关键词：
{', '.join(report_data.get('keywords', [])[:5])}

💡 本周建议：
{report_data.get('recommendation', '继续保持！')}

——
周报生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return self.send_message(user_id, message.strip())

    def _format_ranking(self, users: List[dict]) -> str:
        """格式化排行榜"""
        if not users:
            return "  暂无数据"

        ranking_text = ""
        medals = ['🥇', '🥈', '🥉']

        for idx, user in enumerate(users[:3]):
            medal = medals[idx] if idx < len(medals) else f"{idx+1}."
            ranking_text += f"  {medal} {user.get('nickname', '用户')} - {user.get('points', 0)}积分\n"

        return ranking_text.strip()

    def test_connection(self) -> bool:
        """测试连接是否正常"""
        try:
            if not self.token:
                logger.warning("⚠️  未配置企业微信")
                return False

            logger.info("✅ 企业微信配置正确，可以发送消息")
            return True

        except Exception as e:
            logger.error(f"❌ 连接测试失败: {e}")
            return False


# ========== 测试函数 ==========

def test_wechat():
    """测试企业微信连接"""
    logging.basicConfig(level=logging.INFO)

    bot = WeChatBot()

    if not bot.token:
        print("⚠️  企业微信未配置或连接失败")
        return False

    print("✅ 企业微信机器人初始化成功")

    # 测试发送消息
    # 注意：需要将'用户ID'替换为实际的企业微信用户ID
    # bot.send_message('用户ID', '这是一条测试消息')

    return True


if __name__ == '__main__':
    test_wechat()
