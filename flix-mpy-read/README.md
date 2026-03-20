# Flix-mpy

ESP32 四轴飞行器固件 - MicroPython 实现

## 简介

Flix-mpy 是 [flix](https://github.com/okalachev/flix) 四轴飞行器固件的 MicroPython 移植版本，专为 ESP32 微控制器设计。它提供了完整的飞行控制功能，包括姿态估计、PID 控制、多种飞行模式和支持 MAVLink 协议的地面站通信。

## 功能特性

- **姿态估计**: 基于陀螺仪和加速度计的姿态融合算法
- **PID 控制**: 支持姿态和角速度两级 PID 控制
- **多种飞行模式**:
  - STAB: 姿态稳定模式
  - ACRO: 特技模式
  - RAW: 原始控制模式
  - AUTO: 自主模式
- **传感器支持**: MPU9250 IMU (I2C)
- **RC 接收机**: SBUS 协议 (UART)
- **通信协议**: MAVLink (UDP over Wi-Fi)
- **参数系统**: 持久化参数存储
- **命令行界面**: 交互式调试和配置

## 目录结构

```
flix-mpy/
├── main.py              # 主程序入口
├── lib/
│   ├── __init__.py
│   ├── vector.py        # 三维向量数学库
│   ├── quaternion.py    # 四元数旋转库
│   ├── pid.py           # PID 控制器
│   ├── lpf.py           # 低通滤波器
│   ├── control.py       # 飞行控制逻辑
│   ├── estimate.py      # 姿态估计
│   ├── imu.py           # IMU 传感器驱动
│   ├── motors.py        # 电机 PWM 控制
│   ├── rc.py            # RC 接收机 (SBUS)
│   ├── wifi.py          # Wi-Fi 通信
│   ├── mavlink.py       # MAVLink 协议
│   ├── cli.py           # 命令行界面
│   ├── parameters.py    # 参数存储
│   ├── log.py           # 飞行日志
│   ├── led.py           # LED 控制
│   ├── safety.py        # 安全保护
│   └── util.py          # 工具函数
└── params.json          # 参数配置文件 (运行时生成)
```

## 硬件要求

- **控制器**: ESP32 开发板
- **IMU**: MPU9250 (I2C)
- **RC 接收机**: 支持 SBUS 协议的接收机
- **电调**: 支持 PWM 信号的无刷电调
- **电机**: 四个无刷电机

## 接线说明

### IMU (MPU9250)

| IMU 引脚 | ESP32 引脚 |
| ------ | -------- |
| SDA    | GPIO 21  |
| SCL    | GPIO 22  |
| VCC    | 3.3V     |
| GND    | GND      |

### RC 接收机 (SBUS)

| 接收机引脚 | ESP32 引脚 |
| ----- | -------- |
| SBUS  | GPIO 16  |
| VCC   | 5V       |
| GND   | GND      |

### 电机

| 电机位置    | 默认 GPIO |
| ------- | ------- |
| 前左 (FL) | GPIO 27 |
| 前右 (FR) | GPIO 26 |
| 后左 (RL) | GPIO 25 |
| 后右 (RR) | GPIO 12 |

## 安装

1. 安装 MicroPython 固件到 ESP32
   ```bash
   esptool.py --chip esp32 --port COM3 write_flash -z 0x1000 esp32-20240105-v1.22.1.bin
   ```
2. 上传代码到 ESP32
   ```bash
   mpremote connect COM3 cp -r . :
   ```
3. 连接到 REPL
   ```bash
   mpremote connect COM3
   ```

## 快速开始

```python
import main
main.run()
```

## 命令行界面

在 REPL 中可以使用以下命令:

| 命令                           | 说明     |
| ---------------------------- | ------ |
| `help`                       | 显示帮助信息 |
| `arm`                        | 解锁电机   |
| `disarm`                     | 上锁电机   |
| `status`                     | 显示系统状态 |
| `param list`                 | 列出所有参数 |
| `param get <name>`           | 获取参数值  |
| `param set <name> <value>`   | 设置参数值  |
| `param save`                 | 保存参数   |
| `param reset`                | 重置为默认值 |
| `calibrate gyro`             | 陀螺仪校准  |
| `calibrate accel`            | 加速度计校准 |
| `motor test <index> <value>` | 测试电机   |
| `motor stop`                 | 停止所有电机 |

## 参数配置

### 控制参数 (CTL\_\*)

| 参数名               | 说明            | 默认值 |
| ----------------- | ------------- | --- |
| CTL\_R\_RATE\_P   | 横滚角速度 P 增益    | -   |
| CTL\_R\_RATE\_I   | 横滚角速度 I 增益    | -   |
| CTL\_R\_RATE\_D   | 横滚角速度 D 增益    | -   |
| CTL\_P\_RATE\_P   | 俯仰角速度 P 增益    | -   |
| CTL\_P\_RATE\_I   | 俯仰角速度 I 增益    | -   |
| CTL\_P\_RATE\_D   | 俯仰角速度 D 增益    | -   |
| CTL\_Y\_RATE\_P   | 偏航角速度 P 增益    | -   |
| CTL\_Y\_RATE\_I   | 偏航角速度 I 增益    | -   |
| CTL\_Y\_RATE\_D   | 偏航角速度 D 增益    | -   |
| CTL\_R\_P         | 横滚姿态 P 增益     | -   |
| CTL\_P\_P         | 俯仰姿态 P 增益     | -   |
| CTL\_Y\_P         | 偏航姿态 P 增益     | -   |
| CTL\_TILT\_MAX    | 最大倾斜角度 (度)    | -   |
| CTL\_R\_RATE\_MAX | 最大横滚角速度 (度/秒) | -   |
| CTL\_P\_RATE\_MAX | 最大俯仰角速度 (度/秒) | -   |
| CTL\_Y\_RATE\_MAX | 最大偏航角速度 (度/秒) | -   |

### IMU 参数 (IMU\_\*)

| 参数名                    | 说明          |
| ---------------------- | ----------- |
| IMU\_ROT\_ROLL         | IMU 安装横滚旋转角 |
| IMU\_ROT\_PITCH        | IMU 安装俯仰旋转角 |
| IMU\_ROT\_YAW          | IMU 安装偏航旋转角 |
| IMU\_ACC\_BIAS\_X/Y/Z  | 加速度计零偏      |
| IMU\_ACC\_SCALE\_X/Y/Z | 加速度计比例因子    |

### 安全参数 (SF\_\*)

| 参数名                | 说明            | 默认值  |
| ------------------ | ------------- | ---- |
| SF\_RC\_LOSS\_TIME | RC 信号丢失超时 (秒) | 1.0  |
| SF\_DESCEND\_TIME  | 缓慢下降时间 (秒)    | 10.0 |

## 飞行模式

| 模式   | 说明                    |
| ---- | --------------------- |
| STAB | 姿态稳定模式，飞手控制倾斜角度，适合初学者 |
| ACRO | 特技模式，飞手控制角速度，适合特技飞行   |
| RAW  | 原始模式，直接控制电机扭矩，仅用于调试   |
| AUTO | 自主模式，由 MAVLink 控制     |

## MAVLink 支持

支持与 QGroundControl、Mission Planner 等地面站通信:

- 心跳信号
- 姿态遥测
- 飞行模式切换
- 解锁/上锁命令
- RC 通道覆盖

## 开发调试

### 查看循环频率

```python
import main
print(main.loop_rate)  # 应接近 400Hz
```

### 查看姿态数据

```python
from lib import estimate
euler = estimate.attitude.to_euler()
print(f"Roll: {euler.x}, Pitch: {euler.y}, Yaw: {euler.z}")
```

### 导出飞行日志

```python
from lib import log
log.print_header()
log.print_data()
```

## 注意事项

1. 首次使用前请校准加速度计
2. 调整 PID 参数时请移除螺旋桨
3. 确保电调已正确校准
4. 飞行前检查电机旋转方向

## 许可证

M**IT L**icense

## 作者

Ashitaka-Laputa-IV <laputakar@gmail.com>

## 原始项目

- GitHub: <https://github.com/okalachev/flix>

