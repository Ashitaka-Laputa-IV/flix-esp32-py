# 使用指南

本指南将帮助您构建、设置和飞行 Flix-mpy 四轴飞行器。

## 安装 MicroPython

### 1. 下载 MicroPython 固件

从 [MicroPython 官网](https://micropython.org/download/ESP32/) 下载最新的 ESP32 固件。

### 2. 安装 esptool

```bash
pip install esptool
```

### 3. 烧录固件

```bash
esptool.py --chip esp32 --port COM3 erase_flash
esptool.py --chip esp32 --port COM3 write_flash -z 0x1000 esp32-20240105-v1.22.1.bin
```

> **注意**: 将 `COM3` 替换为您的 ESP32 的实际端口。

## 上传代码

### 使用 mpremote

```bash
pip install mpremote
mpremote connect COM3 cp -r main.py lib :
```

### 使用 ampy

```bash
pip install adafruit-ampy
ampy --port COM3 put main.py
ampy --port COM3 put lib
```

### 使用 Thonny IDE

1. 安装 [Thonny IDE](https://thonny.org/)
2. 配置解释器为 MicroPython (ESP32)
3. 打开文件并保存到设备

## 连接到 REPL

### 使用 mpremote

```bash
mpremote connect COM3
```

### 使用串口终端

任何串口终端程序都可以，设置：
- 波特率: 115200
- 数据位: 8
- 停止位: 1
- 校验位: 无

## 启动飞行器

在 REPL 中执行：

```python
import main
main.run()
```

或者将以下内容添加到 `boot.py` 实现自动启动：

```python
import main
main.run()
```

## 命令行界面

在 REPL 中可以使用以下命令：

### 基本命令

| 命令 | 说明 |
|------|------|
| `help` | 显示帮助信息 |
| `arm` | 解锁电机 |
| `disarm` | 上锁电机 |
| `status` | 显示系统状态 |

### 参数命令

| 命令 | 说明 |
|------|------|
| `param list` | 列出所有参数 |
| `param get <name>` | 获取参数值 |
| `param set <name> <value>` | 设置参数值 |
| `param save` | 保存参数到文件 |
| `param reset` | 重置为默认值 |

### 校准命令

| 命令 | 说明 |
|------|------|
| `calibrate gyro` | 陀螺仪校准 |
| `calibrate accel` | 加速度计校准 |

### 电机测试命令

| 命令 | 说明 |
|------|------|
| `motor test <index> <value>` | 测试单个电机 (index: 0-3) |
| `motor stop` | 停止所有电机 |

> **警告**: 测试电机前请务必卸下螺旋桨！

## 参数配置

### 控制参数

```python
# 在 REPL 中设置参数
param set CTL_R_P 0.5
param set CTL_R_I 0.1
param set CTL_R_D 0.01
```

### IMU 参数

```python
# 设置 IMU 安装方向 (弧度)
param set IMU_ROT_ROLL 0
param set IMU_ROT_PITCH 0
param set IMU_ROT_YAW -1.571  # -90 度
```

### 电机参数

```python
# 设置电机引脚
param set MOT_PIN_FL 27
param set MOT_PIN_FR 26
param set MOT_PIN_RL 25
param set MOT_PIN_RR 12

# 设置 PWM 参数
param set MOT_PWM_FREQ 400
param set MOT_PWM_MIN 1000
param set MOT_PWM_MAX 2000
```

### 安全参数

```python
# RC 信号丢失超时 (秒)
param set SF_RC_LOSS_TIME 1.0

# 缓慢下降时间 (秒)
param set SF_DESCEND_TIME 10.0
```

## Wi-Fi 配置

### 查看当前配置

```python
from lib import wifi
print(wifi.get_config())
```

### 配置为接入点模式

飞行器将创建 Wi-Fi 热点：

```python
param set WIFI_MODE 1  # AP 模式
```

默认 SSID: `flix`，密码: `flixwifi`

### 配置为客户端模式

飞行器连接到现有 Wi-Fi：

```python
param set WIFI_MODE 2  # STA 模式
```

需要在代码中配置 SSID 和密码。

## 使用 QGroundControl

1. 安装 [QGroundControl](https://qgroundcontrol.com/)
2. 将设备连接到飞行器的 Wi-Fi 热点
3. 启动 QGroundControl，它将自动连接

### 支持的功能

- 姿态遥测显示
- 飞行模式切换
- 解锁/上锁控制
- 参数配置
- MAVLink 控制台

## 校准流程

### 陀螺仪校准

1. 将飞行器放置在水平表面上
2. 保持静止
3. 执行校准命令：

```python
calibrate gyro
```

校准数据会自动保存。

### 加速度计校准

1. 将飞行器放置在六个不同方向
2. 每个方向保持静止
3. 按照提示操作：

```python
calibrate accel
```

需要的六个方向：
1. 正常水平放置
2. 倒置
3. 左侧朝下
4. 右侧朝下
5. 机头朝下
6. 机尾朝下

## 飞行前检查

### 1. 检查 IMU

```python
from lib import imu
print(f"Accel: {imu.acc.x}, {imu.acc.y}, {imu.acc.z}")
print(f"Gyro: {imu.gyro.x}, {imu.gyro.y}, {imu.gyro.z}")
```

### 2. 检查姿态估计

移动飞行器，观察姿态变化：

```python
from lib import estimate
euler = estimate.attitude.to_euler()
print(f"Roll: {euler.x}, Pitch: {euler.y}, Yaw: {euler.z}")
```

### 3. 检查 RC 输入

```python
from lib import rc
print(f"Channels: {rc.channels}")
```

### 4. 测试电机

```python
# 卸下螺旋桨后执行
motor test 0 0.2  # 测试电机 0，20% 推力
motor stop        # 停止
```

## 飞行模式

### STAB 模式 (推荐新手)

姿态稳定模式，飞手控制倾斜角度：

```python
from lib import control
control.mode = control.STAB
```

### ACRO 模式

特技模式，飞手控制角速度：

```python
control.mode = control.ACRO
```

### 解锁和上锁

```python
# 解锁
control.armed = True

# 上锁
control.armed = False
```

## 故障排除

### IMU 无数据

检查 I2C 连接：
```python
from machine import I2C, Pin
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
print(i2c.scan())  # 应显示 MPU9250 地址 (0x68 或 0x69)
```

### RC 无信号

检查 UART 连接和波特率设置。

### 电机不转

1. 检查 PWM 输出
2. 确认电调已校准
3. 检查电机引脚配置

### Wi-Fi 连接问题

1. 检查 Wi-Fi 模式参数
2. 确认 SSID 和密码正确
3. 重启设备重试
