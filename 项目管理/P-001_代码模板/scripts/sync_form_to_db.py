# -*- coding: utf-8 -*-
"""
从问卷星表单同步数据到SQLite数据库
支持自动导出CSV并导入数据库
"""

import os
import sys
import logging
import pandas as pd
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from modules.sqlite_manager import SQLiteManager


class WenJuanSyncer:
    """问卷星数据同步器"""

    def __init__(self, csv_path='wjx_export.csv'):
        """
        初始化同步器

        Args:
            csv_path: CSV文件路径（从问卷星导出）
        """
        self.csv_path = csv_path
        self.db = SQLiteManager()

    def load_csv(self):
        """从CSV文件加载数据"""
        try:
            if not os.path.exists(self.csv_path):
                logger.warning(f"⚠️ CSV文件不存在: {self.csv_path}")
                logger.info("💡 使用说明:")
                logger.info("  1. 访问问卷星后台: https://www.wjx.cn/manage/mysuveylist.aspx")
                logger.info("  2. 选择你的问卷")
                logger.info("  3. 点击'数据统计' → '数据下载'")
                logger.info("  4. 选择'Excel格式'或'CSV格式'")
                logger.info(f"  5. 保存为: {self.csv_path}")
                return None

            df = pd.read_csv(self.csv_path, encoding='utf-8')
            logger.info(f"✅ 已加载 {len(df)} 行数据")
            logger.info(f"📋 列名: {list(df.columns)}")
            return df

        except Exception as e:
            logger.error(f"❌ 加载CSV失败: {e}")
            return None

    def parse_user_data(self, row):
        """
        从表单行解析用户数据

        期望的列名（示例）:
        - 序号 / 提交时间
        - 姓名 / 用户名 / 昵称
        - 邮箱 / 手机 / 联系方式
        - 期望反馈重点 / 反馈 / 备注
        """
        # 尝试匹配常见的列名
        nickname = None
        for col in ['姓名', '用户名', '昵称', 'nickname']:
            if col in row and pd.notna(row[col]):
                nickname = str(row[col]).strip()
                break

        contact = None
        for col in ['邮箱', '手机', '联系方式', 'email', 'phone']:
            if col in row and pd.notna(row[col]):
                contact = str(row[col]).strip()
                break

        feedback = None
        for col in ['期望反馈重点', '反馈', '备注', 'feedback']:
            if col in row and pd.notna(row[col]):
                feedback = str(row[col]).strip()
                break

        return {
            'nickname': nickname or '匿名用户',
            'contact': contact or '',
            'feedback': feedback or '',
            'timestamp': datetime.now().isoformat()
        }

    def sync_users(self, df):
        """同步用户数据"""
        if df is None or df.empty:
            return 0

        sync_count = 0
        exist_count = 0
        error_count = 0

        for idx, row in df.iterrows():
            try:
                user_data = self.parse_user_data(row)
                nickname = user_data['nickname']

                # 检查用户是否已存在
                if self.db.user_exists(nickname):
                    exist_count += 1
                    logger.debug(f"⏭️ 用户已存在: {nickname}")
                    continue

                # 添加用户
                self.db.add_user(
                    nickname=nickname,
                    source='wenjuan',
                    contact=user_data['contact'],
                    created_at=datetime.now().isoformat()
                )
                sync_count += 1

                # 如果有反馈，也添加反馈记录
                if user_data['feedback']:
                    self.db.add_feedback(
                        user_name=nickname,
                        content=user_data['feedback'],
                        source='form',
                        created_at=datetime.now().isoformat()
                    )

                logger.info(f"✅ 用户已添加: {nickname}")

            except Exception as e:
                error_count += 1
                logger.error(f"❌ 处理行 {idx} 失败: {e}")

        logger.info("=" * 60)
        logger.info(f"✅ 新增用户: {sync_count}")
        logger.info(f"⏭️ 已存在: {exist_count}")
        logger.info(f"❌ 错误: {error_count}")
        logger.info("=" * 60)

        return sync_count

    def sync_from_wenjuan_api(self, form_id=None, api_key=None):
        """
        通过问卷星API同步数据（高级用法）

        需要问卷星的API凭证
        https://www.wjx.cn/openapi/docs/

        Args:
            form_id: 问卷ID
            api_key: API密钥
        """
        logger.info("💡 API同步说明:")
        logger.info("  问卷星专业版支持API，需要:")
        logger.info("  1. 升级为问卷星专业版")
        logger.info("  2. 获取API凭证")
        logger.info("  3. 设置 WJX_FORM_ID 和 WJX_API_KEY 环境变量")
        logger.info("")
        logger.info("  简单方案: 每次在问卷星后台手动导出CSV，本脚本会自动同步")
        logger.info("")

        # 如果提供了API凭证，尝试调用API
        if form_id and api_key:
            try:
                import requests
                # API实现留作扩展
                logger.info("🔄 正在通过API获取数据...")
                # TODO: 实现问卷星API调用
            except Exception as e:
                logger.warning(f"⚠️ API调用失败: {e}")

    def cleanup_csv(self):
        """备份并清理CSV文件"""
        try:
            if os.path.exists(self.csv_path):
                backup_dir = Path('backups/wenjuan')
                backup_dir.mkdir(parents=True, exist_ok=True)

                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_path = backup_dir / f'wjx_export_{timestamp}.csv'

                import shutil
                shutil.copy(self.csv_path, backup_path)
                logger.info(f"💾 CSV已备份到: {backup_path}")

        except Exception as e:
            logger.warning(f"⚠️ 备份失败: {e}")

    def close(self):
        """关闭数据库连接"""
        self.db.close()

    def get_sync_summary(self):
        """获取同步总结"""
        stats = self.db.get_stats()
        return {
            '总用户数': stats.get('total_users', 0),
            '总反馈数': stats.get('total_feedbacks', 0),
            '最后更新': datetime.now().isoformat()
        }


def sync_wenjuan_data(csv_path='wjx_export.csv'):
    """
    主函数：同步问卷星数据

    Args:
        csv_path: CSV文件路径
    """
    logger.info("=" * 60)
    logger.info("🔄 问卷星数据同步")
    logger.info("=" * 60)

    syncer = WenJuanSyncer(csv_path)

    try:
        # 加载CSV
        df = syncer.load_csv()

        if df is None:
            logger.warning("⚠️ 无法加载数据，请先导出CSV文件")
            return False

        # 同步用户
        sync_count = syncer.sync_users(df)

        # 备份CSV
        syncer.cleanup_csv()

        # 显示统计
        summary = syncer.get_sync_summary()
        logger.info("")
        logger.info("📊 同步完成统计:")
        for key, value in summary.items():
            logger.info(f"  {key}: {value}")

        logger.info("=" * 60)
        logger.info("✅ 数据同步完成")
        logger.info("=" * 60)

        return True

    except Exception as e:
        logger.error(f"❌ 同步失败: {e}", exc_info=True)
        return False

    finally:
        syncer.close()


if __name__ == '__main__':
    # 支持自定义CSV路径
    csv_file = sys.argv[1] if len(sys.argv) > 1 else 'wjx_export.csv'
    success = sync_wenjuan_data(csv_file)
    sys.exit(0 if success else 1)
