# 文档目录

- [README](../README.md) - 项目概述和快速开始

## 用户文档

- [使用指南](usage.md) - 安装、配置和飞行
- [固件概述](firmware.md) - 固件架构和数据流
- [故障排除](troubleshooting.md) - 常见问题解决方案

## 开发文档

- [API 参考](api.md) - 模块和函数详细文档
- [开发指南](development.md) - 贡献代码和二次开发

## 模块文档

每个模块的详细文档可以在源代码文件的文档字符串中找到：

| 模块 | 文件 | 说明 |
|------|------|------|
| main | `main.py` | 主程序入口 |
| vector | `lib/vector.py` | 三维向量数学 |
| quaternion | `lib/quaternion.py` | 四元数旋转 |
| pid | `lib/pid.py` | PID 控制器 |
| lpf | `lib/lpf.py` | 低通滤波器 |
| control | `lib/control.py` | 飞行控制 |
| estimate | `lib/estimate.py` | 姿态估计 |
| imu | `lib/imu.py` | IMU 传感器 |
| motors | `lib/motors.py` | 电机控制 |
| rc | `lib/rc.py` | RC 接收机 |
| wifi | `lib/wifi.py` | Wi-Fi 通信 |
| mavlink | `lib/mavlink.py` | MAVLink 协议 |
| cli | `lib/cli.py` | 命令行界面 |
| parameters | `lib/parameters.py` | 参数管理 |
| log | `lib/log.py` | 飞行日志 |
| led | `lib/led.py` | LED 控制 |
| safety | `lib/safety.py` | 安全保护 |
| util | `lib/util.py` | 工具函数 |

## 外部资源

- [原项目 GitHub](https://github.com/okalachev/flix)
- [MicroPython 官网](https://micropython.org/)
- [QGroundControl](https://qgroundcontrol.com/)
- [MAVLink 协议](https://mavlink.io/)
