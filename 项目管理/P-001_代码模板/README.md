# P-001 邀测招募自动化系统

> 完全自动化的邀测用户招募、追踪、反馈收集和激励系统

## 🚀 快速开始

### 1. 克隆或复制项目

```bash
git clone <repo-url> auto-recruitment
cd auto-recruitment
```

### 2. 配置环境

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的配置
# - GOOGLE_SHEET_ID
# - WECHAT_CORP_ID
# - WECHAT_AGENT_ID
# - WECHAT_SECRET
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 验证连接

```bash
# 测试所有连接和配置
python scripts/test_connection.py
```

### 5. 启动机器人

```bash
# 运行主程序（会启动所有定时任务）
python main.py

# 或使用PM2管理进程
pm2 start main.py --name "recruitment-bot"
```

---

## 📁 项目结构

```
auto-recruitment/
├── main.py                    # 主程序入口
├── requirements.txt           # 依赖列表
├── config.yaml               # 配置文件
├── .env.example              # 环境变量模板
├── README.md                 # 本文件
│
├── modules/                  # 核心模块
│   ├── __init__.py
│   ├── google_sheet.py       # Google Sheets API操作
│   ├── rewards.py            # 激励系统
│   ├── analytics.py          # 数据分析和周报
│   └── invite_tracker.py     # 邀请链接追踪
│
├── scripts/                  # 辅助脚本
│   ├── test_connection.py    # 连接测试
│   ├── show_dashboard.py     # 显示仪表板
│   └── trigger_tasks.py      # 手动触发任务
│
├── templates/                # 消息模板
│   ├── wechat_reply.txt
│   └── post_zhihu.md
│
├── logs/                     # 日志目录（自动生成）
├── backups/                  # 数据备份目录（自动生成）
└── reports/                  # 周报目录（自动生成）
```

---

## 🔧 配置说明

### Google Sheets API

1. 访问 [Google Cloud Console](https://console.cloud.google.com)
2. 创建项目并启用 Google Sheets API
3. 创建Service Account，下载JSON密钥
4. 获取Sheet ID（URL中的长ID）
5. 将JSON文件保存为 `google-credentials.json`
6. 在Google Sheet中Share给Service Account的Email

### 企业微信配置

1. 注册 [企业微信](https://work.weixin.qq.com)
2. 创建应用，获取 CorpID、AgentID、Secret
3. 填入 `.env` 文件

### 可选：QQ机器人

需要安装并运行 `go-cqhttp` + `nonebot2`

---

## 📊 定时任务

系统自动执行以下任务：

| 时间 | 任务 | 说明 |
|------|------|------|
| 早 06:00 | 计算激励 | 根据用户活动计算积分 |
| 早 09:00 | 发放激励 | 向用户发送激励通知 |
| 午 12:00 | 同步反馈 | 从微信/QQ收集反馈 |
| 周一 09:00 | 知乎发布 | 自动发布到知乎 |
| 周五 17:00 | 生成周报 | 生成数据分析周报 |
| 凌晨 02:00 | 数据备份 | 备份所有数据 |

---

## 🎯 常见命令

### 手动触发任务

```bash
# 计算激励
python scripts/trigger_tasks.py --calculate-rewards

# 发放激励
python scripts/trigger_tasks.py --distribute-rewards

# 同步反馈
python scripts/trigger_tasks.py --sync-feedback

# 生成周报
python scripts/trigger_tasks.py --generate-report

# 备份数据
python scripts/trigger_tasks.py --backup-data

# 显示统计
python scripts/trigger_tasks.py --stats

# 执行所有任务
python scripts/trigger_tasks.py --all
```

### 查看仪表板

```bash
# 显示实时仪表板
python scripts/show_dashboard.py
```

### 完整性检查

```bash
# 检查所有连接
python scripts/test_connection.py
```

---

## 🔐 数据安全

- 所有数据存储在 Google Sheets，自动备份到 `backups/` 目录
- `.env` 文件包含敏感信息，**不要提交到版本控制**
- 建议使用 `.gitignore` 忽略：
  ```
  .env
  *.log
  backups/
  google-credentials.json
  ```

---

## 📈 核心特性

### ✅ 自动化覆盖度：93%

- **用户信息收集**（95%）：自动记录微信/QQ用户
- **邀请追踪**（100%）：唯一链接自动追踪
- **反馈收集**（90%）：自动抓取群内反馈
- **激励计算**（100%）：自动规则引擎
- **激励发放**（100%）：自动推送通知
- **数据分析**（100%）：自动生成报告

### 💡 智能特性

- 🎯 **积分排行榜**：自动排名，激励竞争
- 🔗 **邀请追踪**：每个用户有唯一邀请链接
- 📊 **实时仪表板**：Google Sheet自动更新
- 📝 **周报自动生成**：带数据分析和建议
- 💾 **自动备份**：每日数据备份

---

## 🐛 故障排查

### Google Sheets 无法连接

```
问题：credentials.json not found
解决：确保 google-credentials.json 在项目根目录

问题：Permission denied
解决：检查 Service Account Email 是否被Share到Sheet
```

### 微信机器人不回复

```
问题：Token过期
解决：重新登录或刷新token

问题：消息未收到
解决：检查企业微信权限配置
```

### 定时任务未执行

```
问题：看不到日志
解决：检查 logs/recruitment.log 文件

问题：任务一直失败
解决：运行 python scripts/test_connection.py 检查连接
```

---

## 📞 支持和帮助

详见完整方案文档：[[P-001_邀测用户招募自动化方案]]

---

## 📄 许可证

Internal Use Only

---

## ✨ 更新日志

### v1.0.0 (2026-04-16)
- ✨ 初始版本发布
- 📦 包含所有核心模块
- 🔄 完整的定时任务系统
- 📊 实时数据仪表板

---

**Last Updated**: 2026-04-16
**Maintainer**: P-001 Project Team
