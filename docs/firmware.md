# 固件概述

固件是一个常规的 Arduino 草图，它遵循经典的 Arduino 单线程设计。初始化代码在 `setup()` 函数中，主循环在 `loop()` 函数中。草图包括几个文件，每个文件负责特定的子系统。

## 数据流

<img src="img/dataflow.svg" width=600 alt="固件数据流图">

主循环以 1000 Hz 运行。数据流通过全局变量进行，包括：

* `t` *(float)* — 当前步骤时间，*s*。
* `dt` *(float)* — 当前步骤和上一步骤之间的时间增量，*s*。
* `gyro` *(Vector)* — 来自陀螺仪的数据，*rad/s*。
* `acc` *(Vector)* — 来自加速度计的加速度数据，*m/s<sup>2</sup>*。
* `rates` *(Vector)* — 滤波后的角速率，*rad/s*。
* `attitude` *(Quaternion)* — 飞行器的估计姿态（方向）。
* `controlRoll`, `controlPitch`, `controlYaw`, `controlThrottle`, `controlMode` *(float)* — 飞行员控制输入，范围 [-1, 1]。
* `motors` *(float[4])* — 电机输出，范围 [0, 1]。

## 源文件

固件源文件位于 `flix` 目录中。

* [`flix.ino`](../flix/flix.ino) — Arduino 草图主文件，入口点。包括一些全局变量定义和主循环。
* [`imu.ino`](../flix/imu.ino) — 从 IMU 传感器（陀螺仪和加速度计）读取数据，IMU 校准。
* [`rc.ino`](../flix/rc.ino) — 从 RC 接收器读取数据，RC 校准。
* [`estimate.ino`](../flix/estimate.ino) — 姿态估计，互补滤波器。
* [`control.ino`](../flix/control.ino) — 控制子系统，三维两级级联 PID 控制器。
* [`motors.ino`](../flix/motors.ino) — PWM 电机输出控制。
* [`mavlink.ino`](../flix/mavlink.ino) — 通过 MAVLink 协议与 QGroundControl 或 [pyflix](../tools/pyflix) 交互。
* [`cli.ino`](../flix/cli.ino) — 串口和 MAVLink 控制台。

实用程序文件：

* [`vector.h`](../flix/vector.h), [`quaternion.h`](../flix/quaternion.h) — 向量和四元数库。
* [`pid.h`](../flix/pid.h) — 通用 PID 控制器。
* [`lpf.h`](../flix/lpf.h) — 通用低通滤波器。

### 控制子系统

飞行员输入在 `interpretControls()` 中解释，然后转换为**控制命令**，其中包括以下内容：

* `attitudeTarget` *(Quaternion)* — 飞行器的目标姿态。
* `ratesTarget` *(Vector)* — 目标角速率，*rad/s*。
* `ratesExtra` *(Vector)* — 附加（前馈）角速率，用于 STAB 模式下的偏航率控制，*rad/s*。
* `torqueTarget` *(Vector)* — 目标扭矩，范围 [-1, 1]。
* `thrustTarget` *(float)* — 集体电机推力目标，范围 [0, 1]。

控制命令在 `controlAttitude()`、`controlRates()`、`controlTorque()` 函数中处理。如果相应的控制目标设置为 `NAN`，则可以跳过每个函数。

<img src="img/control.svg" width=300 alt="控制子系统图">

解锁状态存储在 `armed` 变量中，当前模式存储在 `mode` 变量中。

### 控制台

要写入控制台，使用 `print()` 函数。此函数将数据发送到串口控制台和 MAVLink 控制台（可以在 QGroundControl 中无线访问）。该函数支持格式化：

```cpp
print("Test value: %.2f\n", testValue);
```

要添加控制台命令，请修改 `cli.ino` 文件中的 `doCommand()` 函数。

> [!IMPORTANT]
> 避免在飞行命令中使用延迟，这会**导致**飞行器崩溃！（设计是单线程的。）
>
> 对于地面命令，使用 `pause()` 函数而不是 `delay()`。此函数允许以 MAVLink 连接继续工作的方式暂停。

## 构建固件

请参阅 [usage.md](usage.md) 中的构建说明。
