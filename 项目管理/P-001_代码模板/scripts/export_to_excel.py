#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导出数据到Excel
每周自动生成报告
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()


def main():
    """导出数据到Excel"""
    print("\n" + "="*60)
    print("📊 导出邀测招募数据到Excel")
    print("="*60 + "\n")

    try:
        from modules.sqlite_manager import SQLiteManager

        db = SQLiteManager()

        # 导出Excel
        output_file = 'recruitment_report.xlsx'
        success = db.export_to_excel(output_file)

        if success:
            print(f"\n✅ 成功导出到: {output_file}")
            print("\n📋 文件包含以下Sheet:")
            print("  • 统计概览 - 关键指标")
            print("  • 用户列表 - 所有用户数据")
            print("  • 反馈日志 - 用户反馈")
            print("  • 邀请追踪 - 邀请转化数据")
            print("\n💡 提示：用Excel打开查看")

        else:
            print("\n❌ 导出失败，请检查日志")
            return 1

        db.close()

    except ImportError as e:
        print(f"\n❌ 缺少依赖: {e}")
        print("\n📦 请安装必要的包:")
        print("   pip install pandas openpyxl")
        return 1

    except Exception as e:
        logger.error(f"❌ 错误: {e}", exc_info=True)
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
