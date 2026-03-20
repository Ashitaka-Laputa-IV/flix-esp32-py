# 固件架构

Flix 固件是一个普通的 Arduino 草图，以单线程风格实现。初始化代码位于 `setup()` 函数中，主循环位于 `loop()` 函数中。草图由几个文件组成，每个文件负责特定的子系统。

<img src="img/dataflow.svg" width=600 alt="固件数据流图">

主循环 `loop()` 以 1000 Hz 的频率工作。子系统之间的数据传输通过全局变量进行：

* `t` *(float)* — 当前步骤时间，*s*。
* `dt` *(float)* — 当前步骤和上一步骤之间的时间增量，*s*。
* `gyro` *(Vector)* — 来自陀螺仪的数据，*rad/s*。
* `acc` *(Vector)* — 来自加速度计的数据，*m/s<sup>2</sup>*。
* `rates` *(Vector)* — 滤波后的角速率，*rad/s*。
* `attitude` *(Quaternion)* — 飞行器方向（位置）的估计。
* `controlRoll`, `controlPitch`, `controlYaw`, `controlThrottle`, `controlMode` *(float)* — 来自飞行员的控制命令，范围 [-1, 1]。
* `motors` *(float[4])* — 电机输出信号，范围 [0, 1]。

## 源文件

固件源文件位于 `flix` 目录中。主要文件：

* [`flix.ino`](https://github.com/okalachev/flix/blob/master/flix/flix.ino) — Arduino 草图主文件。定义一些全局变量和主循环。
* [`imu.ino`](https://github.com/okalachev/flix/blob/master/flix/imu.ino) — 从 IMU 传感器（陀螺仪和加速度计）读取数据，IMU 校准。
* [`rc.ino`](https://github.com/okalachev/flix/blob/master/flix/rc.ino) — 从 RC 接收器读取数据，RC 校准。
* [`estimate.ino`](https://github.com/okalachev/flix/blob/master/flix/estimate.ino) — 飞行器方向估计，互补滤波器。
* [`control.ino`](https://github.com/okalachev/flix/blob/master/flix/control.ino) — 控制子系统，三维两级级联 PID 控制器。
* [`motors.ino`](https://github.com/okalachev/flix/blob/master/flix/motors.ino) — 电机 PWM 输出。
* [`mavlink.ino`](https://github.com/okalachev/flix/blob/master/flix/mavlink.ino) — 通过 MAVLink 协议与 QGroundControl 或 [pyflix](https://github.com/okalachev/flix/tree/master/tools/pyflix) 交互。

辅助文件：

* [`vector.h`](https://github.com/okalachev/flix/blob/master/flix/vector.h), [`quaternion.h`](https://github.com/okalachev/flix/blob/master/flix/quaternion.h) — 向量和四元数库。
* [`pid.h`](https://github.com/okalachev/flix/blob/master/flix/pid.h) — PID 控制器。
* [`lpf.h`](https://github.com/okalachev/flix/blob/master/flix/lpf.h) — 低通滤波器。

### 控制子系统

控制器官的状态在 `interpretControls()` 函数中处理，并转换为**控制命令**，其中包括以下内容：

* `attitudeTarget` *(Quaternion)* — 飞行器的目标方向。
* `ratesTarget` *(Vector)* — 目标角速率，*rad/s*。
* `ratesExtra` *(Vector)* — 附加（前馈）角速率，用于 STAB 模式下的偏航控制，*rad/s*。
* `torqueTarget` *(Vector)* — 目标扭矩，范围 [-1, 1]。
* `thrustTarget` *(float)* — 目标总推力，范围 [0, 1]。

控制命令在 `controlAttitude()`、`controlRates()`、`controlTorque()` 函数中处理。如果其中一个变量的值设置为 `NAN`，则跳过相应的函数。

<img src="img/control.svg" width=300 alt="控制子系统图">

*armed* 状态存储在 `armed` 变量中，当前模式存储在 `mode` 变量中。
