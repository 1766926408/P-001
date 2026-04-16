---
tags: [Bug, Python, 模块, 导入]
项目: P-002
状态: 已解决
---

# BUG-005 模块导入路径错误

## 现象
直接运行脚本报错：
```
ModuleNotFoundError: No module named 'utils'
```

## 根本原因
直接运行 `.py` 文件时，`sys.path` 不包含项目根目录，相对导入失败。

## 解决方案
改用 **`python3 -m`** 模块路径运行：

```bash
# 错误方式
python3 scripts/imu/imu_arm_sine_record_bno080_stable.py

# 正确方式
python3 -m scripts.imu.imu_arm_sine_record_bno080_stable
```

## 相关问题
- 如果报 `No module named 'rclpy'`：需要先 `source /opt/ros/humble/setup.bash`

---
*记录日期：2026-04-15*
