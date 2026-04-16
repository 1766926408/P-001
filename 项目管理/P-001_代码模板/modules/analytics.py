# -*- coding: utf-8 -*-
"""
分析引擎模块
负责数据分析、周报生成、趋势预测
"""

import logging
from datetime import datetime, timedelta
from collections import Counter
from typing import Dict, List
import json
from .sqlite_manager import SQLiteManager as SheetManager

logger = logging.getLogger(__name__)


class AnalyticsEngine:
    """分析引擎"""

    def __init__(self):
        """初始化"""
        self.sheet_manager = SheetManager()
        logger.info("✅ 分析引擎初始化完成")

    def generate_weekly_report(self) -> Dict:
        """生成周报"""
        try:
            logger.info("📝 开始生成周报...")

            # 收集数据
            users = self.sheet_manager.get_all_users()
            feedback = self.sheet_manager.get_all_feedback()
            stats = self.sheet_manager.get_stats()

            # 数据分析
            report = {
                'timestamp': datetime.now().isoformat(),
                'week': self._get_week_string(),
                'overview': self._analyze_overview(users, feedback),
                'channels': self._analyze_channels(users),
                'feedback_analysis': self._analyze_feedback(feedback),
                'user_insights': self._analyze_users(users),
                'recommendations': self._generate_recommendations(feedback)
            }

            # 保存报告
            self._save_report(report)

            # 发送报告
            self._send_report(report)

            logger.info("✅ 周报生成完成")
            return report

        except Exception as e:
            logger.error(f"❌ 周报生成失败: {e}")
            return {}

    def _get_week_string(self) -> str:
        """获取周信息"""
        now = datetime.now()
        start = now - timedelta(days=now.weekday())
        end = start + timedelta(days=6)
        return f"{start.strftime('%Y-%m-%d')} ~ {end.strftime('%Y-%m-%d')}"

    def _analyze_overview(self, users: List[Dict], feedback: List[Dict]) -> Dict:
        """分析概览"""
        return {
            'total_users': len(users),
            'new_users_this_week': len([u for u in users if self._is_this_week(u.get('加入时间'))]),
            'total_feedback': len(feedback),
            'new_feedback_this_week': len([f for f in feedback if self._is_this_week(f.get('反馈时间'))]),
            'feedback_rate': f"{len([u for u in users if u.get('群聊状态') == '已反馈']) / max(len(users), 1) * 100:.1f}%",
        }

    def _analyze_channels(self, users: List[Dict]) -> Dict:
        """分析各渠道用户分布"""
        channels = Counter([u.get('来源渠道') for u in users])
        return dict(channels)

    def _analyze_feedback(self, feedback: List[Dict]) -> Dict:
        """分析反馈"""
        if not feedback:
            return {'total': 0, 'keywords': [], 'categories': {}}

        # 提取关键词
        all_content = [f.get('反馈内容', '') for f in feedback if f.get('反馈内容')]
        keywords = self._extract_keywords(' '.join(all_content))

        # 分类反馈
        categories = {
            'bug': len([f for f in feedback if '错误' in f.get('反馈内容', '') or 'bug' in f.get('反馈内容', '')]),
            'feature': len([f for f in feedback if '功能' in f.get('反馈内容', '') or '建议' in f.get('反馈内容', '')]),
            'ui': len([f for f in feedback if '界面' in f.get('反馈内容', '') or 'UI' in f.get('反馈内容', '')]),
            'performance': len([f for f in feedback if '性能' in f.get('反馈内容', '') or '速度' in f.get('反馈内容', '')]),
        }

        return {
            'total': len(feedback),
            'keywords': keywords,
            'categories': categories
        }

    def _analyze_users(self, users: List[Dict]) -> Dict:
        """分析用户"""
        total_points = sum(int(u.get('激励积分', 0)) for u in users)
        active_users = len([u for u in users if u.get('群聊状态') != '未加入'])

        return {
            'total': len(users),
            'active': active_users,
            'activity_rate': f"{active_users / max(len(users), 1) * 100:.1f}%",
            'total_points': total_points,
            'avg_points': total_points // max(len(users), 1),
            'top_users': self._get_top_users(users, 5)
        }

    def _generate_recommendations(self, feedback: List[Dict]) -> List[str]:
        """生成建议"""
        recommendations = []

        if not feedback:
            recommendations.append("⚠️ 反馈数量较少，建议增加激励以鼓励用户反馈")
        else:
            feedback_rate = len(feedback)
            if feedback_rate < 5:
                recommendations.append("💡 提高反馈激励，目标每周10+条有效反馈")

        # 根据反馈内容生成建议
        feedback_content = ' '.join([f.get('反馈内容', '') for f in feedback])
        if 'bug' in feedback_content.lower() or '错误' in feedback_content:
            recommendations.append("🐛 检测到用户反馈有bug，建议优先修复")

        if 'feature' in feedback_content.lower() or '功能' in feedback_content:
            recommendations.append("✨ 用户提出功能建议，可考虑纳入后续版本")

        if not recommendations:
            recommendations.append("✅ 当前运营状态良好，继续保持！")

        return recommendations

    def _extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """提取关键词"""
        # 简单的关键词提取（实际应用可用jieba等分词库）
        if not text:
            return []

        # 按空格和常见符号分割
        words = text.replace('，', ' ').replace('。', ' ').replace('！', ' ').split()

        # 过滤短词和停用词
        stopwords = {'的', '了', '是', '在', '和', '等', 'a', 'an', 'the', 'and'}
        words = [w for w in words if len(w) > 1 and w not in stopwords]

        # 词频统计
        word_freq = Counter(words)
        keywords = [w for w, _ in word_freq.most_common(top_n)]

        return keywords

    def _get_top_users(self, users: List[Dict], limit: int = 5) -> List[Dict]:
        """获取活跃度最高的用户"""
        sorted_users = sorted(
            users,
            key=lambda x: int(x.get('激励积分', 0)),
            reverse=True
        )

        return [
            {
                'nickname': u.get('昵称'),
                'points': u.get('激励积分'),
                'source': u.get('来源渠道')
            }
            for u in sorted_users[:limit]
        ]

    def _is_this_week(self, datetime_str: str) -> bool:
        """检查是否本周"""
        try:
            if not datetime_str:
                return False

            # 解析时间字符串
            dt = datetime.fromisoformat(datetime_str)
            now = datetime.now()

            # 判断是否同一周
            week_start = now - timedelta(days=now.weekday())
            return dt.date() >= week_start.date()

        except:
            return False

    def _save_report(self, report: Dict) -> bool:
        """保存报告"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"reports/weekly_report_{timestamp}.json"

            import os
            os.makedirs('reports', exist_ok=True)

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)

            logger.info(f"✅ 报告已保存: {filename}")
            return True

        except Exception as e:
            logger.error(f"❌ 报告保存失败: {e}")
            return False

    def _send_report(self, report: Dict) -> bool:
        """发送报告"""
        try:
            # 生成报告文本
            report_text = self._format_report(report)

            # TODO: 发送到钉钉/企业微信/邮件
            logger.info("📨 周报已发送")
            return True

        except Exception as e:
            logger.error(f"❌ 报告发送失败: {e}")
            return False

    def _format_report(self, report: Dict) -> str:
        """格式化报告"""
        overview = report['overview']
        channels = report['channels']
        feedback_analysis = report['feedback_analysis']
        user_insights = report['user_insights']
        recommendations = report['recommendations']

        text = f"""
{'='*60}
📊 邀测招募周报 - {report['week']}
{'='*60}

📈 概览
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ 总用户数: {overview['total_users']}
✓ 本周新增: {overview['new_users_this_week']}
✓ 总反馈数: {overview['total_feedback']}
✓ 本周新反馈: {overview['new_feedback_this_week']}
✓ 反馈率: {overview['feedback_rate']}

📱 渠道分布
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

        for channel, count in channels.items():
            text += f"  • {channel}: {count}\n"

        text += f"""
💬 反馈分析
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ 反馈总数: {feedback_analysis['total']}
✓ 热词 Top 5: {', '.join(feedback_analysis['keywords'][:5])}
✓ 反馈分类:
  - Bug: {feedback_analysis['categories'].get('bug', 0)}
  - 功能: {feedback_analysis['categories'].get('feature', 0)}
  - UI: {feedback_analysis['categories'].get('ui', 0)}
  - 性能: {feedback_analysis['categories'].get('performance', 0)}

👥 用户洞察
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ 活跃用户: {user_insights['active']}/{user_insights['total']} ({user_insights['activity_rate']})
✓ 总积分: {user_insights['total_points']}
✓ 平均积分: {user_insights['avg_points']}
✓ 活跃用户 Top 5:
"""

        for idx, user in enumerate(user_insights['top_users'], start=1):
            text += f"  {idx}. {user['nickname']} - {user['points']}积分\n"

        text += f"""
💡 建议与规划
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

        for rec in recommendations:
            text += f"  • {rec}\n"

        text += f"""
{'='*60}
生成时间: {report['timestamp']}
{'='*60}
"""

        return text

    def print_report(self, report: Dict = None):
        """打印报告"""
        if report is None:
            report = self.generate_weekly_report()

        report_text = self._format_report(report)
        print(report_text)


if __name__ == '__main__':
    # 测试
    logging.basicConfig(level=logging.INFO)

    ae = AnalyticsEngine()
    ae.print_report()
