---
tags: [P-001, SQLite, 快速指南]
created: 2026-04-16
---

# 快速切换到 SQLite - 仅需3步（5分钟）

> Google Sheets 打不开？用 SQLite 本地数据库替代，**完全免费，零依赖**

---

## ⚡ 3步快速切换

### Step 1: 修改 main.py（1分钟）

打开 `P-001_代码模板/main.py`，找到这行：

```python
from modules.google_sheet import SheetManager
```

**改为**：

```python
from modules.sqlite_manager import SQLiteManager as SheetManager
```

**就这一行改动！** 其他所有代码都不需要改。

---

### Step 2: 更新环境变量（1分钟）

编辑 `.env` 文件，添加：

```env
# 数据源配置
DATA_SOURCE=sqlite

# SQLite数据库路径
SQLITE_DB_PATH=recruitment.db
```

---

### Step 3: 验证运行（3分钟）

```bash
# 测试连接
python scripts/test_connection.py

# 应该看到：✅ SQLite 连接成功

# 或者直接运行主程序
python main.py
```

**完成！** 🎉

---

## 📊 数据库文件说明

SQLite 会自动在项目根目录创建 `recruitment.db` 文件：

```
auto-recruitment/
├── main.py
├── recruitment.db  ← 这是你的数据库（自动创建）
├── modules/
│   └── sqlite_manager.py
└── ...
```

### 备份数据库

```bash
# 自动备份（每天凌晨02:00自动执行）
# 或手动备份：

# 方式1: 复制文件
cp recruitment.db backups/recruitment_backup.db

# 方式2: 导出为Excel（推荐）
python scripts/export_to_excel.py
```

---

## 🔍 查看和管理数据

### 方案 A: 导出为 Excel 查看（推荐）

```bash
# 自动生成Excel报告
python scripts/export_to_excel.py

# 会生成 recruitment_report.xlsx
# 包含4个Sheet：统计、用户、反馈、邀请
```

### 方案 B: 使用SQLite图形工具查看

下载并安装 SQLite 图形工具（可选）：

**Windows/Mac/Linux 通用**：
1. 下载 [DBeaver Community](https://dbeaver.io/download/)（免费）
2. 打开 `recruitment.db` 文件
3. 实时查看所有表和数据

**或更简单的**：
1. 下载 [SQLiteStudio](https://sqlitestudio.pl/)
2. 打开 `recruitment.db`
3. 点击 "Tables" 查看数据

### 方案 C: 命令行查看（高级）

```bash
# 安装sqlite3命令行工具（Windows/Mac/Linux都有）

# 查看所有用户
sqlite3 recruitment.db "SELECT nickname, source, join_time FROM users;"

# 查看反馈
sqlite3 recruitment.db "SELECT user_name, content FROM feedback;"

# 查询统计
sqlite3 recruitment.db "SELECT COUNT(*) as total_users FROM users;"
```

---

## ⚙️ 常见操作

### 1. 显示仪表板

```bash
python scripts/show_dashboard.py
```

### 2. 导出周报

```bash
python scripts/export_to_excel.py
# 生成 recruitment_report.xlsx
```

### 3. 手动触发任务

```bash
# 计算激励
python scripts/trigger_tasks.py --calculate-rewards

# 生成周报
python scripts/trigger_tasks.py --generate-report

# 备份数据
python scripts/trigger_tasks.py --backup-data
```

### 4. 恢复数据（从备份）

```bash
# 查看备份
ls backups/

# 恢复（复制备份文件）
cp backups/recruitment_20260416_120000.db recruitment.db
```

---

## 🆘 问题排查

### Q: 无法打开数据库？

```
错误：sqlite3.OperationalError: unable to open database file
解决：检查权限
  chmod 666 recruitment.db
```

### Q: 数据导不出来？

```
错误：ModuleNotFoundError: No module named 'pandas'
解决：安装依赖
  pip install pandas openpyxl
```

### Q: 忘记数据在哪？

```
查看：ls recruitment.db
查看备份：ls backups/
查看导出：ls *.xlsx
```

### Q: 要转回Google Sheets怎么办？

```python
# 很简单，就改回来
from modules.google_sheet import SheetManager  # 改回这行

# 所有数据不会丢失，Google Sheets模块会读取之前的云端数据
```

---

## 📈 SQLite vs Google Sheets

| 方面 | SQLite | Google Sheets |
|------|--------|---------------|
| **访问速度** | ⚡ 超快（本地） | 🌐 中等（网络） |
| **无网络依赖** | ✅ 完全本地 | ❌ 需要网络 |
| **在线编辑** | ❌ 需要脚本 | ✅ 直接编辑 |
| **数据安全** | ✅ 完全自己管理 | ⚠️ 云端存储 |
| **备份方便** | ✅ 复制文件 | ✅ 自动云端 |
| **查看数据** | 📊 导出Excel | 📋 直接浏览 |

---

## 💡 推荐用法

### 日常使用：

```bash
# 启动系统
python main.py

# 每周五自动生成报告
# 或手动导出：
python scripts/export_to_excel.py

# 用Excel查看和分享报告
```

### 团队协作（需要共享数据）：

```
选项1: 将Excel定期上传到云盘（阿里云盘、腾讯微云）
选项2: 改用腾讯表格（见 P-001_替代方案对比.md）
```

---

## 🎯 确认清单

- [ ] 修改了 `main.py` 的导入行
- [ ] 更新了 `.env` 文件
- [ ] 运行了 `test_connection.py` 验证
- [ ] 可以看到 `recruitment.db` 文件被创建
- [ ] 可以导出 Excel 报告

✅ 完成！你现在正在使用SQLite了。

---

## 📚 相关文档

- [[P-001_替代方案对比|完整的替代方案对比]]
- [[P-001_邀测用户招募自动化方案|原始自动化方案]]
- [[P-001_快速启动指南|快速启动指南]]

---

## 🚀 下一步

1. **立即切换**：按上面3步修改代码
2. **运行系统**：`python main.py`
3. **查看数据**：`python scripts/show_dashboard.py`
4. **导出报告**：`python scripts/export_to_excel.py`

**就这样，你已经有了一个完全本地、完全自动化的邀测招募系统！** 🎉

