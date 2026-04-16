# -*- coding: utf-8 -*-
"""
SQLite 数据库管理模块
本地数据库方案，无需Google Sheets API
"""

import sqlite3
import logging
from datetime import datetime
import uuid
import json
from typing import Dict, List, Optional
import os

logger = logging.getLogger(__name__)


class SQLiteManager:
    """SQLite 数据库管理器"""

    def __init__(self, db_path: str = 'recruitment.db'):
        """初始化数据库"""
        self.db_path = db_path
        try:
            self.conn = sqlite3.connect(db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row  # 返回字典形式
            self.cursor = self.conn.cursor()
            self._init_tables()
            logger.info(f"✅ SQLite 数据库初始化成功: {db_path}")
        except Exception as e:
            logger.error(f"❌ SQLite 连接失败: {e}")
            raise

    # ========== 初始化 ==========

    def _init_tables(self):
        """初始化数据库表"""

        # 用户表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                nickname TEXT NOT NULL,
                source TEXT,
                invite_link TEXT,
                join_time TEXT,
                group_status TEXT DEFAULT '已加入',
                feedback_content TEXT,
                invite_count INTEGER DEFAULT 0,
                reward_points INTEGER DEFAULT 0,
                reward_status TEXT DEFAULT '待发放',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 反馈表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT,
                user_id TEXT,
                user_name TEXT,
                content TEXT NOT NULL,
                feedback_time TEXT,
                status TEXT DEFAULT '未读',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 邀请追踪表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS invitations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inviter_id TEXT,
                invitee_id TEXT,
                invite_link TEXT,
                is_converted TEXT DEFAULT '待转化',
                convert_time TEXT,
                reward_status TEXT DEFAULT '待处理',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 统计表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT,
                metric_value INTEGER,
                recorded_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        self.conn.commit()
        logger.info("✅ 数据库表初始化完成")

    # ========== 用户操作 ==========

    def add_user(self, nickname: str, source: str, invite_link: Optional[str] = None) -> str:
        """添加新用户"""
        try:
            user_id = str(uuid.uuid4())[:8]
            invite_link = invite_link or f"https://invite.yourapp.com/{user_id}"

            self.cursor.execute('''
                INSERT INTO users
                (user_id, nickname, source, invite_link, join_time, group_status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, nickname, source, invite_link, datetime.now().isoformat(), '已加入'))

            self.conn.commit()
            logger.info(f"➕ 新增用户: {nickname} ({source})")
            return user_id

        except Exception as e:
            logger.error(f"❌ 添加用户失败: {e}")
            return None

    def get_all_users(self) -> List[Dict]:
        """获取所有用户"""
        try:
            self.cursor.execute('SELECT * FROM users ORDER BY created_at DESC')
            rows = self.cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"❌ 获取用户列表失败: {e}")
            return []

    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """按ID获取用户"""
        try:
            self.cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            row = self.cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            logger.error(f"❌ 获取用户失败: {e}")
            return None

    def update_user(self, user_id: str, **kwargs) -> bool:
        """更新用户信息"""
        try:
            # 构建UPDATE语句
            set_clause = ', '.join([f"{k} = ?" for k in kwargs.keys()])
            values = list(kwargs.values()) + [user_id]

            self.cursor.execute(
                f'UPDATE users SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?',
                values
            )
            self.conn.commit()
            logger.info(f"✏️ 更新用户: {user_id}")
            return True

        except Exception as e:
            logger.error(f"❌ 更新用户失败: {e}")
            return False

    def count_users(self) -> int:
        """获取用户总数"""
        try:
            self.cursor.execute('SELECT COUNT(*) FROM users')
            return self.cursor.fetchone()[0]
        except:
            return 0

    def get_users_by_source(self, source: str) -> List[Dict]:
        """按来源获取用户"""
        try:
            self.cursor.execute('SELECT * FROM users WHERE source = ?', (source,))
            rows = self.cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"❌ 按源获取用户失败: {e}")
            return []

    # ========== 反馈操作 ==========

    def add_feedback(self, source: str, user_name: str, content: str, user_id: Optional[str] = None) -> bool:
        """添加反馈"""
        try:
            self.cursor.execute('''
                INSERT INTO feedback
                (source, user_id, user_name, content, feedback_time, status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (source, user_id, user_name, content, datetime.now().isoformat(), '未读'))

            self.conn.commit()
            logger.info(f"💬 新增反馈: {user_name} ({source})")
            return True

        except Exception as e:
            logger.error(f"❌ 添加反馈失败: {e}")
            return False

    def get_all_feedback(self, status: Optional[str] = None) -> List[Dict]:
        """获取所有反馈"""
        try:
            if status:
                self.cursor.execute('SELECT * FROM feedback WHERE status = ? ORDER BY created_at DESC', (status,))
            else:
                self.cursor.execute('SELECT * FROM feedback ORDER BY created_at DESC')

            rows = self.cursor.fetchall()
            return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"❌ 获取反馈列表失败: {e}")
            return []

    def sync_feedback(self) -> Dict:
        """同步反馈数据"""
        try:
            logger.info("🔄 反馈数据已同步")
            return {'total': len(self.get_all_feedback())}
        except Exception as e:
            logger.error(f"❌ 反馈同步失败: {e}")
            return {}

    # ========== 邀请追踪 ==========

    def add_invitation(self, inviter_id: str, invitee_id: str, invite_link: str) -> bool:
        """记录邀请"""
        try:
            self.cursor.execute('''
                INSERT INTO invitations
                (inviter_id, invitee_id, invite_link)
                VALUES (?, ?, ?)
            ''', (inviter_id, invitee_id, invite_link))

            self.conn.commit()
            logger.info(f"🔗 记录邀请: {inviter_id} → {invitee_id}")
            return True

        except Exception as e:
            logger.error(f"❌ 记录邀请失败: {e}")
            return False

    def mark_invitation_converted(self, invite_link: str) -> bool:
        """标记邀请为已转化"""
        try:
            self.cursor.execute('''
                UPDATE invitations
                SET is_converted = '已转化', convert_time = ?
                WHERE invite_link = ?
            ''', (datetime.now().isoformat(), invite_link))

            self.conn.commit()
            logger.info(f"✅ 邀请已转化: {invite_link}")
            return True

        except Exception as e:
            logger.error(f"❌ 标记邀请失败: {e}")
            return False

    # ========== 统计操作 ==========

    def get_stats(self) -> Dict:
        """获取统计数据"""
        try:
            users = self.get_all_users()
            feedback = self.get_all_feedback()
            invites = self.cursor.execute('SELECT * FROM invitations').fetchall()

            total_users = len(users)
            wechat_users = len([u for u in users if u['source'] == 'wechat'])
            qq_users = len([u for u in users if u['source'] == 'qq'])
            feedback_count = len(feedback)
            converted = len([i for i in invites if i['is_converted'] == '已转化'])
            conversion_rate = converted / max(len(invites), 1) * 100

            return {
                'total_users': total_users,
                'wechat_users': wechat_users,
                'qq_users': qq_users,
                'feedback_count': feedback_count,
                'conversion_rate': f"{conversion_rate:.1f}%",
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ 获取统计失败: {e}")
            return {}

    def update_stats_dashboard(self) -> bool:
        """更新统计仪表板"""
        try:
            stats = self.get_stats()
            logger.info(f"📊 统计数据已更新: {stats}")
            return True
        except Exception as e:
            logger.error(f"❌ 更新统计失败: {e}")
            return False

    # ========== 数据备份和导出 ==========

    def backup_data(self) -> bool:
        """备份数据"""
        try:
            logger.info("💾 开始数据备份...")

            os.makedirs('backups', exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = f'backups/recruitment_{timestamp}.db'

            # 复制数据库文件
            import shutil
            shutil.copy(self.db_path, backup_file)

            logger.info(f"✅ 数据备份完成: {backup_file}")
            return True

        except Exception as e:
            logger.error(f"❌ 数据备份失败: {e}")
            return False

    def export_to_excel(self, output_file: str = 'recruitment_report.xlsx') -> bool:
        """导出数据到Excel"""
        try:
            import pandas as pd

            logger.info(f"📊 导出数据到 {output_file}...")

            # 读取数据
            df_users = pd.read_sql_query('SELECT * FROM users', self.conn)
            df_feedback = pd.read_sql_query('SELECT * FROM feedback', self.conn)
            df_invites = pd.read_sql_query('SELECT * FROM invitations', self.conn)

            # 计算统计数据
            stats = self.get_stats()
            df_stats = pd.DataFrame({
                '指标': ['总用户数', '微信用户', 'QQ用户', '总反馈数', '转化率'],
                '数值': [
                    stats['total_users'],
                    stats['wechat_users'],
                    stats['qq_users'],
                    stats['feedback_count'],
                    stats['conversion_rate']
                ]
            })

            # 写入Excel
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                df_stats.to_excel(writer, sheet_name='统计概览', index=False)
                df_users.to_excel(writer, sheet_name='用户列表', index=False)
                df_feedback.to_excel(writer, sheet_name='反馈日志', index=False)
                df_invites.to_excel(writer, sheet_name='邀请追踪', index=False)

            logger.info(f"✅ 数据已导出到 {output_file}")
            return True

        except ImportError:
            logger.error("❌ 需要安装pandas和openpyxl")
            logger.error("运行: pip install pandas openpyxl")
            return False
        except Exception as e:
            logger.error(f"❌ 导出失败: {e}")
            return False

    def export_to_json(self, output_dir: str = 'exports') -> bool:
        """导出数据到JSON"""
        try:
            os.makedirs(output_dir, exist_ok=True)

            data = {
                'users': self.get_all_users(),
                'feedback': self.get_all_feedback(),
                'stats': self.get_stats(),
                'export_time': datetime.now().isoformat()
            }

            output_file = f'{output_dir}/recruitment_export.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            logger.info(f"✅ 数据已导出到 {output_file}")
            return True

        except Exception as e:
            logger.error(f"❌ JSON导出失败: {e}")
            return False

    # ========== 关闭数据库 ==========

    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            logger.info("✅ 数据库连接已关闭")

    def __del__(self):
        """析构时关闭连接"""
        self.close()


# ========== 便利函数 ==========

def print_dashboard():
    """打印仪表板"""
    try:
        sm = SQLiteManager()
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
    logging.basicConfig(level=logging.INFO)

    print("🔍 测试SQLite连接...")
    sm = SQLiteManager()

    # 添加测试用户
    print("\n添加测试用户...")
    sm.add_user("测试用户", "wechat")

    print("\n显示仪表板...")
    print_dashboard()

    print("\n查看所有用户:")
    for user in sm.get_all_users():
        print(f"  • {user['nickname']} ({user['source']})")

    sm.close()
    print("\n✅ 测试完成")
