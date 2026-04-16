# -*- coding: utf-8 -*-
"""
自动化任务执行脚本
根据系统时间或手动触发，执行相应的定时任务
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from modules.sqlite_manager import SQLiteManager
from modules.rewards import RewardCalculator
from modules.analytics import AnalyticsEngine


def get_current_hour():
    """获取当前小时（0-23）"""
    return datetime.now().hour


def sync_form_data():
    """同步问卷星表单数据到SQLite"""
    logger.info("=" * 60)
    logger.info("🔄 开始同步表单数据...")
    logger.info("=" * 60)

    try:
        from scripts.sync_form_to_db import sync_wenjuan_data
        sync_wenjuan_data()
        logger.info("✅ 表单数据同步完成")
        return True
    except Exception as e:
        logger.error(f"❌ 表单同步失败: {e}")
        return False


def calculate_daily_rewards():
    """计算每日激励积分"""
    logger.info("=" * 60)
    logger.info("📊 开始计算每日激励...")
    logger.info("=" * 60)

    try:
        calculator = RewardCalculator()
        calculator.calculate_daily_rewards()
        logger.info("✅ 每日激励计算完成")
        return True
    except Exception as e:
        logger.error(f"❌ 激励计算失败: {e}")
        return False


def distribute_rewards():
    """发放激励通知"""
    logger.info("=" * 60)
    logger.info("🎁 开始发放激励通知...")
    logger.info("=" * 60)

    try:
        calculator = RewardCalculator()
        calculator.distribute_rewards()
        logger.info("✅ 激励通知发放完成")
        return True
    except Exception as e:
        logger.error(f"❌ 激励发放失败: {e}")
        return False


def generate_weekly_report():
    """生成周报"""
    logger.info("=" * 60)
    logger.info("📈 开始生成周报...")
    logger.info("=" * 60)

    try:
        analytics = AnalyticsEngine()
        report = analytics.generate_weekly_report()
        logger.info("✅ 周报生成完成")

        # 尝试导出为Excel
        try:
            from scripts.export_weekly_report import export_to_excel
            export_to_excel(report)
            logger.info("✅ Excel导出完成")
        except Exception as e:
            logger.warning(f"⚠️ Excel导出失败: {e}")

        return True
    except Exception as e:
        logger.error(f"❌ 周报生成失败: {e}")
        return False


def classify_feedbacks():
    """自动分类反馈（低优先级，可选）"""
    logger.info("=" * 60)
    logger.info("🏷️ 开始自动分类反馈...")
    logger.info("=" * 60)

    try:
        db = SQLiteManager()
        feedbacks = db.get_all_feedback()

        if not feedbacks:
            logger.info("ℹ️ 没有新反馈需要分类")
            return True

        # 分类规则
        categories = {
            'bug': ['错误', 'bug', '崩溃', '异常', '崩', '卡'],
            'feature': ['功能', '建议', '改进', '希望', '想要'],
            'ui': ['界面', 'UI', '样式', '美观', '不美观'],
            'performance': ['性能', '慢', '卡顿', '响应', '加载'],
            'doc': ['文档', '说明', '教程', '帮助']
        }

        classified_count = 0
        for fb in feedbacks:
            if fb.get('分类'):
                continue  # 已分类

            content = fb.get('反馈内容', '')
            category = 'other'

            for cat, keywords in categories.items():
                if any(kw in content for kw in keywords):
                    category = cat
                    break

            db.update_feedback_category(fb['id'], category)
            classified_count += 1

        db.close()
        logger.info(f"✅ 分类完成: {classified_count} 条反馈")
        return True
    except Exception as e:
        logger.error(f"❌ 反馈分类失败: {e}")
        return False


def show_status():
    """显示当前系统状态"""
    logger.info("=" * 60)
    logger.info("📊 系统状态")
    logger.info("=" * 60)

    try:
        db = SQLiteManager()
        stats = db.get_stats()

        logger.info(f"👥 总用户数: {stats.get('total_users', 0)}")
        logger.info(f"📝 总反馈数: {stats.get('total_feedbacks', 0)}")
        logger.info(f"📢 总邀请数: {stats.get('total_invitations', 0)}")

        db.close()
    except Exception as e:
        logger.warning(f"⚠️ 无法读取状态: {e}")


def run_scheduled_tasks():
    """根据当前时间执行定时任务"""
    hour = get_current_hour()

    logger.info(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"执行小时: {hour}")

    # 显示系统状态
    show_status()

    results = {}

    # 06:00 - 计算激励积分
    if hour == 6:
        logger.info("⏰ 触发 06:00 任务: 计算激励积分")
        results['calculate_rewards'] = calculate_daily_rewards()

    # 09:00 - 发放激励通知
    elif hour == 9:
        logger.info("⏰ 触发 09:00 任务: 发放激励通知")
        results['distribute_rewards'] = distribute_rewards()

    # 10:00 - 同步表单数据
    elif hour == 10:
        logger.info("⏰ 触发 10:00 任务: 同步表单数据")
        results['sync_form'] = sync_form_data()

    # 17:00 - 周五生成周报
    elif hour == 17 and datetime.now().weekday() == 4:  # 4 = 周五
        logger.info("⏰ 触发 17:00 周五任务: 生成周报")
        results['generate_report'] = generate_weekly_report()

    # 其他时间：执行可选任务（可注释掉）
    else:
        logger.info(f"ℹ️ 当前时间 {hour}:00 没有定时任务")
        logger.info("🔄 执行定期维护任务...")
        results['classify'] = classify_feedbacks()

    # 显示执行结果
    logger.info("=" * 60)
    logger.info("📋 任务执行结果")
    logger.info("=" * 60)
    for task_name, success in results.items():
        status = "✅ 成功" if success else "❌ 失败"
        logger.info(f"{task_name}: {status}")

    # 最终状态
    show_status()
    logger.info("=" * 60)
    logger.info("✨ 自动化任务执行完成")
    logger.info("=" * 60)


if __name__ == '__main__':
    try:
        run_scheduled_tasks()
    except KeyboardInterrupt:
        logger.info("⚠️ 用户中断任务")
    except Exception as e:
        logger.error(f"❌ 致命错误: {e}", exc_info=True)
        sys.exit(1)
