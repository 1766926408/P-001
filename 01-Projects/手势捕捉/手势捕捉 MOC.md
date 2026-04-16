---
tags: [项目, 手势捕捉, BNO080, ESP32-S3]
---

# 手势捕捉固件 — 项目地图

## 项目概述
多路 IMU（BNO080 + BMI088）手势数据采集系统，ESP32-S3 双核架构。

**固件路径**：`D:\work\2-IMU\IMU_Tools\firmware_hand\BNO080_HAND_ESP32S3-自研`
**上位机**：`D:\work\2-IMU\DFR_imu\imu_serial\hand_gesture_plotter.py` (v3.6)

## 硬件配置

| 总线 | GPIO | 多路器 | 传感器 | 通道 |
|------|------|--------|--------|------|
| I2C_NUM_0 (Bus A) | GPIO8/9 | TCA_BNO (0x70) | BNO080 | CH0-7 |
| I2C_NUM_1 (Bus B) | GPIO4/5 | TCA1 (0x70) | BMI088 | CH8-15 |

**帧格式**：magic=0xAA58，179B 混合帧（v4.0）

## 开发板映射

| 工程目录 | 开发板 |
|---------|--------|
| BNO080_HAND_ESP32S3-自研 | ESP32-S3-DevKitC-1 |
| NanoESP32 | Arduino Nano ESP32 |

## 通道映射文件

`channel_map.json`（ch 0-15，ch8-15 = BMI088 虚拟通道）

## 子笔记

- [[手势捕捉 Bug 记录]]

---
*模板生成：2026-04-15*
