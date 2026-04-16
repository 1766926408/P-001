---
tags: [项目, IMU, 传感器, 上位机]
---

# IMU 多型号数据采集工具 — 项目地图

## 项目概述
支持 9 款 IMU 传感器的串口实时绘图工具，含 Mahony AHRS 和相对欧拉角计算。

**主程序**：`D:\work\2-IMU\DFR_imu\imu_serial\IMU_plotter_all.py`（当前 v13）

## 支持传感器

| 传感器 | 模式 | 特点 |
|--------|------|------|
| BMI160 / BMI088 / BMI323 | euler_mode | Mahony AHRS，6-DOF，Yaw 漂移 |
| ICM42688 | euler_mode | Mahony AHRS，6-DOF |
| BNO055 / BNO055_v20 | csv_euler_cols | 板载融合，9-DOF |
| BNO080 | csv_euler_cols | 板载融合，9-DOF，Yaw 绝对 |
| DM-IMU-L1 | binary_reader | 二进制协议 |
| FDI-DETA10-A | fdi_reader | 二进制协议 |

## 机器人联调

**机器人 IP**：`192.168.23.22` | 用户：`liberai`
**项目路径**：`/home/liberai/Desktop/Teleop-franka-test`

### 常用命令

```bash
# 传文件到机器人
scp "D:\work\2-IMU\DFR_imu\imu_arm_sine_record_bno080_stable.py" liberai@192.168.23.22:/home/liberai/Desktop/Teleop-franka-test/scripts/imu/

# 机器人上运行（9-DOF）
python3 -m scripts.imu.imu_arm_sine_record_bno080_stable \
    --duration 60 --amplitude 0.04 --freq 0.2 \
    --imu-port /dev/ttyACM0 --save_dir ./calibration_results --min-acc 0
```

## 子笔记

- [[BNO080 联调记录]]
- [[相对欧拉角算法说明]]

---
*模板生成：2026-04-15*
