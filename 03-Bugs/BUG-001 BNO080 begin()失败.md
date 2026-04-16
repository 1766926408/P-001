---
tags: [Bug, BNO080, SparkFun, I2C, 初始化]
项目: P-001
状态: 已解决
---

# BUG-001 BNO080 begin() 失败

## 现象
SparkFun BNO080 库 `begin()` 返回失败，I2C 初始化无法完成。

## 根本原因
`waitForI2C()` 做**单次检查**时，`softReset()` 内部的 `delay(50)` 太短。
BNO080 硬复位后需要约 800ms 才能响应 I2C。

## 解决方案
将 `softReset()` 中的 `delay(50)` 改为 `delay(800)`。

```cpp
// 修改前
delay(50);
// 修改后
delay(800);
```

## 影响范围
所有使用 SparkFun BNO080 库且调用 `waitForI2C()` 单次检查的工程。

---
*记录日期：2026-04-15*
