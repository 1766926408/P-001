#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MM 项目源文件 → Obsidian 镜像自动同步脚本

功能：
  1. 读取源文件：d:\work\9-other\motormind\开发计划.md
  2. 提取关键信息：版本号、进度、优先级
  3. 更新 Obsidian 镜像：01-Projects/MotorMind/P-001 项目地图与开发追踪.md
  4. 生成同步报告

使用方式：
  # 手动运行
  python sync_motormind.py

  # 查看详细日志
  python sync_motormind.py --verbose

  # 仅检查（不修改）
  python sync_motormind.py --dry-run
"""

import os
import sys
import re
from datetime import datetime
from pathlib import Path
import argparse

# 配置路径
SOURCE_FILE = r"d:\work\9-other\motormind\开发计划.md"
OBSIDIAN_VAULT = Path(__file__).parent  # 当前目录假设为 vault 根目录
MIRROR_FILE = OBSIDIAN_VAULT / "01-Projects/MotorMind/P-001 项目地图与开发追踪.md"

class SyncLogger:
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.messages = []

    def info(self, msg):
        self.messages.append(f"[INFO] {msg}")
        if self.verbose:
            print(f"ℹ️  {msg}")

    def success(self, msg):
        self.messages.append(f"[SUCCESS] {msg}")
        print(f"✅ {msg}")

    def warning(self, msg):
        self.messages.append(f"[WARNING] {msg}")
        print(f"⚠️  {msg}")

    def error(self, msg):
        self.messages.append(f"[ERROR] {msg}")
        print(f"❌ {msg}")

    def print_summary(self):
        print("\n" + "="*50)
        print("同步报告")
        print("="*50)
        for msg in self.messages:
            print(msg)

class MotorMindSync:
    def __init__(self, verbose=False, dry_run=False):
        self.logger = SyncLogger(verbose)
        self.dry_run = dry_run
        self.source_content = None
        self.mirror_content = None
        self.version = None
        self.update_date = None

    def run(self):
        """执行完整同步流程"""
        self.logger.info("开始同步 P-001 源文件...")

        if not self.check_files():
            return False

        if not self.read_source():
            return False

        self.read_mirror()
        self.extract_metadata()

        if not self.update_mirror():
            return False

        if not self.dry_run:
            if not self.write_mirror():
                return False

        self.logger.success("✨ 同步完成！" + (" (--dry-run 模式，未实际修改)" if self.dry_run else ""))
        self.logger.print_summary()
        return True

    def check_files(self):
        """检查源文件和镜像文件是否存在"""
        if not os.path.exists(SOURCE_FILE):
            self.logger.error(f"源文件不存在: {SOURCE_FILE}")
            return False

        self.logger.info(f"✓ 源文件存在: {SOURCE_FILE}")

        if not MIRROR_FILE.exists():
            self.logger.warning(f"镜像文件不存在，将创建: {MIRROR_FILE}")
        else:
            self.logger.info(f"✓ 镜像文件存在: {MIRROR_FILE}")

        return True

    def read_source(self):
        """读取源文件内容"""
        try:
            with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
                self.source_content = f.read()
            self.logger.info(f"✓ 读取源文件成功 ({len(self.source_content)} 字符)")
            return True
        except Exception as e:
            self.logger.error(f"读取源文件失败: {e}")
            return False

    def read_mirror(self):
        """读取镜像文件内容"""
        try:
            if MIRROR_FILE.exists():
                with open(MIRROR_FILE, 'r', encoding='utf-8') as f:
                    self.mirror_content = f.read()
                self.logger.info(f"✓ 读取镜像文件成功 ({len(self.mirror_content)} 字符)")
            else:
                self.mirror_content = ""
        except Exception as e:
            self.logger.warning(f"读取镜像文件失败: {e}")
            self.mirror_content = ""

    def extract_metadata(self):
        """从源文件提取版本号和更新时间"""
        # 提取版本号
        version_match = re.search(r'计划版本：(v[\d.]+)', self.source_content)
        if version_match:
            self.version = version_match.group(1)
            self.logger.info(f"✓ 源文件版本: {self.version}")

        # 提取更新日期
        date_match = re.search(r'更新日期：(\d{4}-\d{2}-\d{2})', self.source_content)
        if date_match:
            self.update_date = date_match.group(1)
            self.logger.info(f"✓ 源文件更新日期: {self.update_date}")

    def update_mirror(self):
        """更新镜像文件中的关键信息"""
        try:
            if not self.mirror_content:
                self.logger.info("首次创建镜像文件")
                return True

            # 更新版本和日期
            if self.version and self.update_date:
                self.mirror_content = re.sub(
                    r'v\d+\.\d+.*?(\d{4}-\d{2}-\d{2})',
                    f'{self.version} | {self.update_date}',
                    self.mirror_content
                )
                self.logger.info(f"✓ 更新版本和日期: {self.version} | {self.update_date}")

            # 更新 "最后更新" 时间戳
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.mirror_content = re.sub(
                r'\*Obsidian 笔记最后更新：\d{4}-\d{2}-\d{2}\*',
                f'*Obsidian 笔记最后更新：{datetime.now().strftime("%Y-%m-%d")}*',
                self.mirror_content
            )

            self.logger.info(f"✓ 更新时间戳: {now}")
            return True
        except Exception as e:
            self.logger.error(f"更新镜像内容失败: {e}")
            return False

    def write_mirror(self):
        """写入更新后的镜像文件"""
        try:
            # 确保目录存在
            MIRROR_FILE.parent.mkdir(parents=True, exist_ok=True)

            with open(MIRROR_FILE, 'w', encoding='utf-8') as f:
                f.write(self.mirror_content)

            self.logger.success(f"✓ 镜像文件已更新: {MIRROR_FILE}")
            return True
        except Exception as e:
            self.logger.error(f"写入镜像文件失败: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(
        description='P-001 源文件 → Obsidian 镜像自动同步'
    )
    parser.add_argument('--verbose', '-v', action='store_true', help='详细日志输出')
    parser.add_argument('--dry-run', action='store_true', help='仅检查，不修改文件')

    args = parser.parse_args()

    sync = MotorMindSync(verbose=args.verbose, dry_run=args.dry_run)
    success = sync.run()

    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
