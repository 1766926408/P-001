# P-001 源文件自动同步指南

> 自动同步 `d:\work\9-other\motormind\开发计划.md` → Obsidian 镜像

---

## ⚡ 快速开始

### 方式 1：手动运行（推荐新手）

```bash
# 进入 vault 根目录
cd C:\Users\ljyit\Documents\MySecondBrain

# 运行同步脚本
python sync_motormind.py

# 查看详细日志
python sync_motormind.py --verbose

# 仅检查（不修改）
python sync_motormind.py --dry-run
```

### 方式 2：Git Hook 自动同步（推荐开发者）

每次提交代码时自动同步源文件状态：

```bash
# 1. 进入 vault 目录
cd C:\Users\ljyit\Documents\MySecondBrain

# 2. 创建 Git Hook
mkdir -p .git/hooks
cat > .git/hooks/post-commit << 'EOF'
#!/bin/bash
python sync_motormind.py --verbose
EOF

# 3. 给 Hook 添加执行权限（仅 Linux/Mac 需要）
chmod +x .git/hooks/post-commit
```

**之后的工作流**：
```bash
git add .
git commit -m "更新了 P-001 源文件"
# ✅ Hook 自动运行，镜像同步完成
```

### 方式 3：Windows 定时任务（推荐后台自动）

每天自动同步一次：

#### 步骤 1：创建 Batch 脚本
新建 `C:\Users\ljyit\sync_motormind.bat`：

```batch
@echo off
cd /d "C:\Users\ljyit\Documents\MySecondBrain"
python sync_motormind.py --verbose >> sync_log.txt 2>&1
echo Sync completed at %date% %time% >> sync_log.txt
```

#### 步骤 2：添加 Windows 定时任务

**方法 A：GUI（简单）**
```
按 Win+R → taskschd.msc
创建任务：
  - 名称：P-001 Sync Daily
  - 触发器：每天 09:00
  - 操作：运行 C:\Users\ljyit\sync_motormind.bat
```

**方法 B：PowerShell（高级）**
```powershell
# 以管理员身份运行 PowerShell

$trigger = New-ScheduledTaskTrigger -Daily -At 09:00am
$action = New-ScheduledTaskAction -Execute "C:\Users\ljyit\sync_motormind.bat"
$principal = New-ScheduledTaskPrincipal -UserId "ljyit" -RunLevel Highest

Register-ScheduledTask -TaskName "P-001 Sync Daily" `
  -Trigger $trigger -Action $action -Principal $principal
```

---

## 📊 脚本功能

✅ **自动执行**：
- 读取源文件版本号和更新日期
- 更新 Obsidian 镜像的版本信息
- 同步时间戳

✅ **安全机制**：
- `--dry-run` 模式：仅检查，不修改文件
- `--verbose` 模式：详细日志，方便调试
- 失败时自动报错，不覆盖文件

✅ **支持多平台**：
- Windows（Python + Batch）
- Linux/Mac（Python + Bash）
- Git 环境或独立运行

---

## 🔧 故障排查

### 问题 1：找不到源文件
```
❌ 源文件不存在: d:\work\9-other\motormind\开发计划.md
```

**解决**：检查源文件路径是否正确，或修改脚本中的 `SOURCE_FILE` 变量

### 问题 2：Python 未安装
```
'python' is not recognized as an internal or external command
```

**解决**：
- 确保 Python 已安装：`python --version`
- 或使用完整路径：`C:\Python311\python.exe sync_motormind.py`

### 问题 3：权限不足（Git Hook）
```
permission denied: './post-commit'
```

**解决**（仅 Linux/Mac）：
```bash
chmod +x .git/hooks/post-commit
```

---

## 📋 配置自定义

如果源文件路径不同，编辑 `sync_motormind.py`：

```python
# 第 16 行
SOURCE_FILE = r"d:\work\9-other\motormind\开发计划.md"  # 改成你的路径

# 第 17-18 行
OBSIDIAN_VAULT = Path(__file__).parent  # vault 根目录
MIRROR_FILE = OBSIDIAN_VAULT / "01-Projects/MotorMind/P-001 项目地图与开发追踪.md"
```

---

## 🚀 推荐使用方案

| 用户类型 | 推荐方案 | 频率 |
|--------|--------|------|
| **日常开发** | Git Hook | 每次 commit 自动 |
| **周期性检查** | Windows 定时任务 | 每天 09:00 自动 |
| **临时同步** | 手动运行 | 随需 |
| **调试/验证** | `--dry-run 模式` | 运行前检查 |

---

## 📝 日志查看

### 查看同步历史
```bash
# 查看最后一次同步结果
tail sync_log.txt

# 实时监控同步日志
Get-Content sync_log.txt -Wait  # PowerShell
```

### 启用详细日志
```bash
python sync_motormind.py --verbose > detailed_sync.log 2>&1
```

---

## ✨ 后续扩展

这个脚本可以轻松扩展支持：

```python
# 支持多个项目同步
sources = {
    'P-001': ('d:\work\9-other\motormind\开发计划.md', 'P-001 项目地图...'),
    'P-002': ('d:\work\9-other\other\开发计划.md', 'P-002 项目地图...'),
}

for project_id, (source, mirror) in sources.items():
    sync = MotorMindSync(project_id, source, mirror)
    sync.run()
```

---

*最后更新：2026-04-15*
