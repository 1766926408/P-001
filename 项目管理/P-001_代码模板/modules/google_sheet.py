# -*- coding: utf-8 -*-
"""
Google Sheets 操作模块
负责数据读写、同步、备份
"""

import gspread
from google.oauth2.service_account import Credentials
import logging
from datetime import datetime
import os
import json
import uuid
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class SheetManager:
    """Google Sheets 管理器"""

    def __init__(self):
        """初始化Google Sheets连接"""
        self.sheet_id = os.getenv('GOOGLE_SHEET_ID')
        self.credentials_file = os.getenv('GOOGLE_CREDENTIALS_FILE', 'google-credentials.json')

        try:
            # 认证
            creds = Credentials.from_service_account_file(
                self.credentials_file,
                scopes=['https://www.googleapis.com/auth/spreadsheets',
                        'https://www.googleapis.com/auth/drive']
            )
            self.client = gspread.authorize(creds)

            # 打开Sheet
            self.spreadsheet = self.client.open_by_key(self.sheet_id)
            self.sheet_users = self.spreadsheet.worksheet('users-base')
            self.sheet_feedback = self.spreadsheet.worksheet('feedback-log')
            self.sheet_invites = self.spreadsheet.worksheet('invitation-tracking')
            self.sheet_stats = self.spreadsheet.worksheet('stats-dashboard')

            logger.info("✅ Google Sheets 连接成功")
        except Exception as e:
            logger.error(f"❌ Google Sheets 连接失败: {e}")
            raise

    # ========== 用户操作 ==========

    def add_user(self, nickname: str, source: str, invite_link: Optional[str] = None) -> str:
        """添加新用户"""
        try:
            user_id = str(uuid.uuid4())[:8]
            invite_link = invite_link or f"https://invite.yourapp.com/{user_id}"

            row = [
                user_id,
                nickname,
                source,
                invite_link,
                datetime.now().isoformat(),
                '已加入',
                '',  # 反馈内容
                0,   # 邀请数量
                0,   # 激励积分
                '待发放'
            ]

            self.sheet_users.append_row(row)
            logger.info(f"➕ 新增用户: {nickname} ({source})")
            return user_id

        except Exception as e:
            logger.error(f"❌ 添加用户失败: {e}")
            return None

    def get_all_users(self) -> List[Dict]:
        """获取所有用户"""
        try:
            records = self.sheet_users.get_all_records()
            return records
        except Exception as e:
            logger.error(f"❌ 获取用户列表失败: {e}")
            return []

    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """按ID获取用户"""
        try:
            records = self.sheet_users.get_all_records()
            for record in records:
                if record.get('用户ID') == user_id:
                    return record
            return None
        except Exception as e:
            logger.error(f"❌ 获取用户失败: {e}")
            return None

    def update_user(self, user_id: str, **kwargs) -> bool:
        """更新用户信息"""
        try:
            records = self.sheet_users.get_all_records()
            for idx, record in enumerate(records, start=2):  # 从第2行开始（第1行是标题）
                if record.get('用户ID') == user_id:
                    # 更新对应的单元格
                    for key, value in kwargs.items():
                        col_index = self._get_column_index(self.sheet_users, key)
                        if col_index:
                            self.sheet_users.update_cell(idx, col_index, value)
                    logger.info(f"✏️ 更新用户: {user_id}")
                    return True
            return False
        except Exception as e:
            logger.error(f"❌ 更新用户失败: {e}")
            return False

    # ========== 反馈操作 ==========

    def add_feedback(self, source: str, user: str, content: str, status: str = '未读') -> bool:
        """添加反馈"""
        try:
            row = [
                source,
                user,
                content,
                datetime.now().isoformat(),
                status
            ]
            self.sheet_feedback.append_row(row)
            logger.info(f"💬 新增反馈: {user} ({source})")
            return True
        except Exception as e:
            logger.error(f"❌ 添加反馈失败: {e}")
            return False

    def get_all_feedback(self, status: Optional[str] = None) -> List[Dict]:
        """获取所有反馈"""
        try:
            records = self.sheet_feedback.get_all_records()
            if status:
                records = [r for r in records if r.get('处理状态') == status]
            return records
        except Exception as e:
            logger.error(f"❌ 获取反馈列表失败: {e}")
            return []

    def sync_feedback(self) -> Dict:
        """同步反馈数据（从微信/QQ/论坛）"""
        try:
            logger.info("🔄 开始同步反馈...")

            # TODO: 从微信/QQ机器人同步数据
            # 这里调用 wechat_bot.py 和 qq_bot.py 中的反馈收集函数

            sync_result = {
                'wechat': 0,
                'qq': 0,
                'forum': 0,
                'total': 0
            }

            logger.info(f"✅ 反馈同步完成: {sync_result}")
            return sync_result

        except Exception as e:
            logger.error(f"❌ 反馈同步失败: {e}")
            return {}

    # ========== 邀请追踪操作 ==========

    def add_invitation(self, inviter_id: str, invitee_id: str, invite_link: str) -> bool:
        """记录邀请"""
        try:
            row = [
                inviter_id,
                invitee_id,
                invite_link,
                '待转化',
                '',
                '待处理'
            ]
            self.sheet_invites.append_row(row)
            logger.info(f"🔗 记录邀请: {inviter_id} → {invitee_id}")
            return True
        except Exception as e:
            logger.error(f"❌ 记录邀请失败: {e}")
            return False

    def mark_invitation_converted(self, invite_link: str) -> bool:
        """标记邀请为已转化"""
        try:
            records = self.sheet_invites.get_all_records()
            for idx, record in enumerate(records, start=2):
                if record.get('邀请链接') == invite_link:
                    self.sheet_invites.update_cell(idx, 4, '已转化')  # D列
                    self.sheet_invites.update_cell(idx, 5, datetime.now().isoformat())  # E列
                    logger.info(f"✅ 邀请已转化: {invite_link}")
                    return True
            return False
        except Exception as e:
            logger.error(f"❌ 标记邀请失败: {e}")
            return False

    # ========== 统计操作 ==========

    def get_stats(self) -> Dict:
        """获取统计数据"""
        try:
            users = self.get_all_users()
            feedback = self.get_all_feedback()
            invites = self.sheet_invites.get_all_records()

            total_users = len(users)
            wechat_users = len([u for u in users if u.get('来源渠道') == 'wechat'])
            qq_users = len([u for u in users if u.get('来源渠道') == 'qq'])
            feedback_count = len(feedback)
            conversion_rate = len([i for i in invites if i.get('是否转化') == '已转化']) / max(len(invites), 1)

            return {
                'total_users': total_users,
                'wechat_users': wechat_users,
                'qq_users': qq_users,
                'feedback_count': feedback_count,
                'conversion_rate': f"{conversion_rate * 100:.1f}%",
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"❌ 获取统计失败: {e}")
            return {}

    def update_stats_dashboard(self) -> bool:
        """更新统计仪表板"""
        try:
            stats = self.get_stats()
            # 更新Sheet中的统计数据
            # TODO: 实现具体的更新逻辑
            logger.info(f"📊 统计数据已更新: {stats}")
            return True
        except Exception as e:
            logger.error(f"❌ 更新统计失败: {e}")
            return False

    # ========== 数据备份 ==========

    def backup_data(self) -> bool:
        """备份所有数据"""
        try:
            logger.info("💾 开始数据备份...")

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_dir = 'backups'
            os.makedirs(backup_dir, exist_ok=True)

            # 导出所有Sheet
            for sheet_name in ['users-base', 'feedback-log', 'invitation-tracking']:
                sheet = self.spreadsheet.worksheet(sheet_name)
                records = sheet.get_all_records()
                filename = f"{backup_dir}/backup_{sheet_name}_{timestamp}.json"

                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(records, f, ensure_ascii=False, indent=2)

                logger.info(f"  ✓ {sheet_name} 已备份")

            logger.info("✅ 数据备份完成")
            return True

        except Exception as e:
            logger.error(f"❌ 数据备份失败: {e}")
            return False

    # ========== 辅助方法 ==========

    def _get_column_index(self, sheet, column_name: str) -> Optional[int]:
        """获取列号"""
        try:
            first_row = sheet.row_values(1)
            return first_row.index(column_name) + 1
        except ValueError:
            return None

    def count_users(self) -> int:
        """获取用户总数"""
        try:
            return len(self.get_all_users())
        except:
            return 0

    def get_users_by_source(self, source: str) -> List[Dict]:
        """按来源获取用户"""
        users = self.get_all_users()
        return [u for u in users if u.get('来源渠道') == source]


# ========== 便利函数 ==========

def print_dashboard():
    """打印仪表板"""
    try:
        sm = SheetManager()
        stats = sm.get_stats()

        print("\n" + "="*50)
        print("📊 邀测招募实时仪表板")
        print("="*50)
        print(f"👥 总用户数: {stats['total_users']}")
        print(f"💬 微信用户: {stats['wechat_users']}")
        print(f"📱 QQ用户: {stats['qq_users']}")
        print(f"💭 反馈数: {stats['feedback_count']}")
        print(f"🎯 转化率: {stats['conversion_rate']}")
        print(f"⏰ 更新时间: {stats['timestamp']}")
        print("="*50 + "\n")

    except Exception as e:
        print(f"❌ 打印仪表板失败: {e}")


if __name__ == '__main__':
    # 测试连接
    import sys
    logging.basicConfig(level=logging.INFO)

    print("🔍 测试Google Sheets连接...")
    sm = SheetManager()
    print("✅ 连接成功！")

    print_dashboard()
