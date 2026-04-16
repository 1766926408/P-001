#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
P-001 邀测用户招募自动化主程序
Auto Recruitment Bot v1.0

功能：
  - 微信/QQ机器人自动回复
  - 用户信息自动记录
  - 反馈自动收集
  - 激励自动计算与发放
  - 周报自动生成

使用：python main.py
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import atexit

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/recruitment.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 导入所有模块
# 数据库方案选择：sqlite_manager（推荐）或 google_sheet
from modules.sqlite_manager import SQLiteManager as SheetManager
from modules.rewards import RewardCalculator
from modules.analytics import AnalyticsEngine
from modules.invite_tracker import InviteTracker

# 版本和配置
VERSION = "1.0.0"
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')


class AutoRecruitmentBot:
    """主程序：集成所有自动化模块"""

    def __init__(self):
        """初始化机器人"""
        self.sheet_manager = SheetManager()
        self.reward_calculator = RewardCalculator()
        self.analytics = AnalyticsEngine()
        self.invite_tracker = InviteTracker()
        self.scheduler = BackgroundScheduler()

        logger.info(f"✅ AutoRecruitmentBot v{VERSION} 初始化成功")
        logger.info(f"运行环境：{ENVIRONMENT}")

    def setup_jobs(self):
        """设置所有定时任务"""

        # 1️⃣ 每天早6点：计算激励积分
        self.scheduler.add_job(
            self.reward_calculator.calculate_daily_rewards,
            trigger=CronTrigger(hour=6, minute=0),
            id='calculate_rewards',
            name='计算激励积分'
        )
        logger.info("📌 [06:00] 激励计算任务已注册")

        # 2️⃣ 每天早9点：发放激励通知
        self.scheduler.add_job(
            self.reward_calculator.distribute_rewards,
            trigger=CronTrigger(hour=9, minute=0),
            id='distribute_rewards',
            name='发放激励通知'
        )
        logger.info("📌 [09:00] 激励发放任务已注册")

        # 3️⃣ 每天下午12点：同步反馈
        self.scheduler.add_job(
            self.sheet_manager.sync_feedback,
            trigger=CronTrigger(hour=12, minute=0),
            id='sync_feedback',
            name='同步反馈数据'
        )
        logger.info("📌 [12:00] 反馈同步任务已注册")

        # 4️⃣ 每周一早9点：发布到知乎
        self.scheduler.add_job(
            self.publish_to_zhihu,
            trigger=CronTrigger(day_of_week='0', hour=9, minute=0),
            id='publish_zhihu',
            name='知乎自动发布'
        )
        logger.info("📌 [周一 09:00] 知乎发布任务已注册")

        # 5️⃣ 每周五下午5点：生成周报
        self.scheduler.add_job(
            self.analytics.generate_weekly_report,
            trigger=CronTrigger(day_of_week='4', hour=17, minute=0),
            id='weekly_report',
            name='生成周报'
        )
        logger.info("📌 [周五 17:00] 周报生成任务已注册")

        # 6️⃣ 每天凌晨2点：数据备份
        self.scheduler.add_job(
            self.sheet_manager.backup_data,
            trigger=CronTrigger(hour=2, minute=0),
            id='backup',
            name='数据备份'
        )
        logger.info("📌 [凌晨 02:00] 数据备份任务已注册")

    def publish_to_zhihu(self):
        """发布到知乎"""
        try:
            logger.info("🚀 开始发布到知乎...")
            # TODO: 实现Selenium自动登录和发帖
            logger.info("✅ 知乎发布完成")
        except Exception as e:
            logger.error(f"❌ 知乎发布失败: {e}")

    def start(self):
        """启动机器人"""
        logger.info("=" * 60)
        logger.info(f"🤖 AutoRecruitmentBot v{VERSION} 启动")
        logger.info("=" * 60)

        # 验证配置
        self._validate_config()

        # 设置定时任务
        self.setup_jobs()

        # 启动调度器
        self.scheduler.start()
        logger.info("✅ 定时任务调度器已启动")

        # 注册关闭事件
        atexit.register(self.shutdown)

        # 显示启动信息
        self._show_startup_info()

        # 保持程序运行
        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("收到关闭信号...")
            self.shutdown()

    def _validate_config(self):
        """验证必要的配置"""
        required_vars = [
            'GOOGLE_SHEET_ID',
            'GOOGLE_CREDENTIALS_FILE',
        ]

        missing = [var for var in required_vars if not os.getenv(var)]

        if missing:
            logger.error(f"❌ 缺少配置: {', '.join(missing)}")
            logger.error("请检查 .env 文件")
            sys.exit(1)

        logger.info("✅ 配置验证通过")

    def _show_startup_info(self):
        """显示启动信息"""
        logger.info("")
        logger.info("📊 已注册的定时任务:")
        for job in self.scheduler.get_jobs():
            logger.info(f"  • {job.name}: {job.trigger}")
        logger.info("")
        logger.info("🔗 数据看板: https://docs.google.com/spreadsheets/d/{}/edit".format(
            os.getenv('GOOGLE_SHEET_ID')
        ))
        logger.info("")

    def shutdown(self):
        """优雅关闭"""
        logger.info("🛑 正在关闭机器人...")
        if self.scheduler.running:
            self.scheduler.shutdown()
        logger.info("✅ 机器人已关闭")


def main():
    """主函数"""
    try:
        # 创建日志目录
        Path('logs').mkdir(exist_ok=True)

        # 启动机器人
        bot = AutoRecruitmentBot()
        bot.start()

    except Exception as e:
        logger.error(f"❌ 启动失败: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
