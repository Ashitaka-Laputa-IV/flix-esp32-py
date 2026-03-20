# API 参考

本文档提供 flix-mpy 所有模块的详细 API 参考。

## 目录

- [main 模块](#main-模块)
- [lib.vector 模块](#libvector-模块)
- [lib.quaternion 模块](#libquaternion-模块)
- [lib.pid 模块](#libpid-模块)
- [lib.lpf 模块](#liblpf-模块)
- [lib.control 模块](#libcontrol-模块)
- [lib.estimate 模块](#libestimate-模块)
- [lib.imu 模块](#libimu-模块)
- [lib.motors 模块](#libmotors-模块)
- [lib.rc 模块](#librc-模块)
- [lib.wifi 模块](#libwifi-模块)
- [lib.mavlink 模块](#libmavlink-模块)
- [lib.cli 模块](#libcli-模块)
- [lib.parameters 模块](#libparameters-模块)
- [lib.log 模块](#liblog-模块)
- [lib.led 模块](#libled-模块)
- [lib.safety 模块](#libsafety-模块)
- [lib.util 模块](#libutil-模块)

---

## main 模块

主程序入口和全局状态管理。

### 全局变量

```python
t: float          # 当前时间 (秒)
dt: float         # 时间增量 (秒)
loop_rate: float  # 循环频率 (Hz)

gyro: Vector      # 陀螺仪数据 (rad/s)
acc: Vector       # 加速度计数据 (m/s²)
rates: Vector     # 滤波后角速率 (rad/s)
attitude: Quaternion  # 估计姿态

control_roll: float      # 横滚控制 [-1, 1]
control_pitch: float     # 俯仰控制 [-1, 1]
control_yaw: float       # 偏航控制 [-1, 1]
control_throttle: float  # 油门控制 [0, 1]
control_mode: float      # 模式控制
control_time: float      # 最后控制时间

landed: bool       # 是否已着陆
motors: list[float]  # 电机输出 [0, 1]
```

### 函数

#### `setup()`

初始化所有硬件和软件模块。

```python
import main
main.setup()
```

#### `loop()`

执行主循环单次迭代。

```python
main.loop()
```

#### `run()`

启动飞行器主程序。

```python
main.run()
```

#### `step()`

更新时间变量。

---

## lib.vector 模块

三维向量数学库。

### Vector 类

```python
from lib.vector import Vector

v = Vector(x=0.0, y=0.0, z=0.0)
```

#### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `x` | float | X 分量 |
| `y` | float | Y 分量 |
| `z` | float | Z 分量 |

#### 方法

##### `norm() -> float`

返回向量的欧几里得范数。

```python
v = Vector(3, 4, 0)
print(v.norm())  # 5.0
```

##### `normalize()`

就地归一化向量。

```python
v = Vector(3, 4, 0)
v.normalize()
print(v.x, v.y)  # 0.6, 0.8
```

##### `valid() -> bool`

检查向量是否有效（不含 NaN）。

#### 静态方法

##### `dot(a: Vector, b: Vector) -> float`

计算点积。

```python
v1 = Vector(1, 0, 0)
v2 = Vector(0, 1, 0)
print(Vector.dot(v1, v2))  # 0.0
```

##### `cross(a: Vector, b: Vector) -> Vector`

计算叉积。

```python
v1 = Vector(1, 0, 0)
v2 = Vector(0, 1, 0)
result = Vector.cross(v1, v2)
print(result.z)  # 1.0
```

##### `angle_between(a: Vector, b: Vector) -> float`

计算两向量夹角（弧度）。

##### `rotate(v: Vector, q: Quaternion) -> Vector`

使用四元数旋转向量。

---

## lib.quaternion 模块

四元数旋转库。

### Quaternion 类

```python
from lib.quaternion import Quaternion

q = Quaternion(w=1.0, x=0.0, y=0.0, z=0.0)
```

#### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `w` | float | 标量分量 |
| `x` | float | X 向量分量 |
| `y` | float | Y 向量分量 |
| `z` | float | Z 向量分量 |

#### 方法

##### `norm() -> float`

返回四元数的范数。

##### `normalize()`

就地归一化四元数。

##### `to_euler() -> Vector`

转换为欧拉角（roll, pitch, yaw）。

```python
euler = q.to_euler()
print(f"Roll: {euler.x}, Pitch: {euler.y}, Yaw: {euler.z}")
```

##### `valid() -> bool`

检查四元数是否有效。

#### 静态方法

##### `from_euler(euler: Vector) -> Quaternion`

从欧拉角创建四元数。

```python
from lib.vector import Vector
q = Quaternion.from_euler(Vector(0.1, 0.2, 0.3))
```

##### `from_axis_angle(axis: Vector, angle: float) -> Quaternion`

从轴角创建四元数。

##### `from_rotation_vector(v: Vector) -> Quaternion`

从旋转向量创建四元数。

##### `multiply(q1: Quaternion, q2: Quaternion) -> Quaternion`

四元数乘法（旋转组合）。

##### `rotate(q: Quaternion, v: Quaternion) -> Quaternion`

四元数旋转。

##### `rotate_vector(v: Vector, q: Quaternion) -> Vector`

旋转向量。

---

## lib.pid 模块

PID 控制器。

### PID 类

```python
from lib.pid import PID

pid = PID(p=1.0, i=0.1, d=0.01, windup=1.0)
```

#### 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `p` | float | 0.0 | 比例增益 |
| `i` | float | 0.0 | 积分增益 |
| `d` | float | 0.0 | 微分增益 |
| `windup` | float | 0.0 | 积分限幅 |
| `d_alpha` | float | 1.0 | 微分滤波系数 |
| `dt_max` | float | 0.1 | 最大时间间隔 |

#### 方法

##### `update(error: float, dt: float) -> float`

更新控制器并返回输出。

```python
output = pid.update(error, dt)
```

##### `reset()`

重置控制器状态。

##### `set_d_alpha(alpha: float)`

设置微分滤波系数。

---

## lib.lpf 模块

低通滤波器。

### LowPassFilter 类

```python
from lib.lpf import LowPassFilter

lpf = LowPassFilter(alpha=0.1)
```

#### 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `alpha` | float | 1.0 | 平滑系数 (0-1) |
| `initial` | Vector | None | 初始值 |

#### 方法

##### `update(input: Vector) -> Vector`

更新滤波器并返回滤波后的值。

```python
filtered = lpf.update(raw_vector)
```

### LowPassFilterScalar 类

标量版本的低通滤波器。

```python
from lib.lpf import LowPassFilterScalar

lpf = LowPassFilterScalar(alpha=0.2)
filtered = lpf.update(raw_value)
```

---

## lib.control 模块

飞行控制。

### 常量

```python
RAW = 0    # 原始模式
ACRO = 1   # 特技模式
STAB = 2   # 姿态模式
AUTO = 3   # 自主模式
```

### 全局变量

```python
armed: bool           # 解锁状态
mode: int             # 当前飞行模式
attitude_target: Quaternion  # 目标姿态
rates_target: Vector  # 目标角速率
thrust_target: float  # 目标推力
torque_target: Vector # 目标扭矩
```

### 函数

#### `setup()`

初始化控制模块。

#### `control()`

执行控制循环。

```python
from lib import control
control.control()
```

---

## lib.estimate 模块

姿态估计。

### 全局变量

```python
rates: Vector      # 估计的角速率
attitude: Quaternion  # 估计的姿态
landed: bool       # 是否已着陆
```

### 函数

#### `setup()`

初始化估计模块。

#### `estimate()`

执行姿态估计。

```python
from lib import estimate
estimate.estimate()
```

---

## lib.imu 模块

IMU 传感器驱动。

### 全局变量

```python
gyro: Vector       # 陀螺仪数据 (rad/s)
acc: Vector        # 加速度计数据 (m/s²)
```

### 函数

#### `setup()`

初始化 IMU。

#### `read()`

读取传感器数据。

```python
from lib import imu
imu.read()
print(imu.acc, imu.gyro)
```

#### `calibrate_accel()`

校准加速度计。

---

## lib.motors 模块

电机控制。

### 常量

```python
MOTOR_REAR_LEFT = 0
MOTOR_REAR_RIGHT = 1
MOTOR_FRONT_RIGHT = 2
MOTOR_FRONT_LEFT = 3
```

### 全局变量

```python
motors: list[float]  # 电机输出 [0, 1]
```

### 函数

#### `setup()`

初始化电机。

#### `send()`

发送电机信号。

```python
from lib import motors
motors.motors[0] = 0.5
motors.send()
```

#### `test_motor(index: int, value: float)`

测试单个电机。

#### `active() -> bool`

检查是否有电机活动。

---

## lib.rc 模块

RC 接收机。

### 全局变量

```python
channels: list[int]  # 通道值 [1000, 2000]
```

### 函数

#### `setup()`

初始化 RC。

#### `read() -> bool`

读取 RC 数据，返回是否成功。

```python
from lib import rc
if rc.read():
    print(rc.channels)
```

#### `calibrate()`

校准 RC。

---

## lib.wifi 模块

Wi-Fi 通信。

### 常量

```python
W_DISABLED = 0
W_STATION = 1
W_AP = 2
```

### 函数

#### `setup()`

初始化 Wi-Fi。

#### `send(ip: str, port: int, data: bytes)`

发送 UDP 数据。

#### `receive() -> tuple`

接收 UDP 数据。

```python
data, addr = wifi.receive()
```

---

## lib.mavlink 模块

MAVLink 协议。

### 函数

#### `setup()`

初始化 MAVLink。

#### `process()`

处理 MAVLink 消息。

```python
from lib import mavlink
mavlink.process()
```

---

## lib.cli 模块

命令行界面。

### 函数

#### `setup()`

初始化 CLI。

#### `handle_input()`

处理输入命令。

```python
from lib import cli
cli.handle_input()
```

---

## lib.parameters 模块

参数管理。

### 函数

#### `setup()`

初始化参数系统。

#### `get(name: str) -> float`

获取参数值。

```python
from lib import parameters
value = parameters.get('CTL_R_P')
```

#### `set(name: str, value: float) -> bool`

设置参数值。

```python
parameters.set('CTL_R_P', 0.5)
```

#### `get_names() -> list`

获取所有参数名。

#### `count() -> int`

获取参数数量。

#### `sync()`

同步参数到存储。

#### `reset()`

重置为默认值。

#### `print_all()`

打印所有参数。

---

## lib.log 模块

飞行日志。

### 函数

#### `log_data()`

记录数据。

```python
from lib import log
log.log_data()
```

#### `print_header()`

打印日志头。

#### `print_data()`

打印日志数据。

---

## lib.led 模块

LED 控制。

### 函数

#### `setup()`

初始化 LED。

#### `set_led(on: bool)`

设置 LED 状态。

```python
from lib import led
led.set_led(True)
```

#### `blink()`

闪烁 LED。

---

## lib.safety 模块

安全保护。

### 全局变量

```python
rc_loss_timeout: float  # RC 丢失超时 (秒)
descend_time: float     # 下降时间 (秒)
```

### 函数

#### `failsafe()`

执行安全检查。

```python
from lib import safety
safety.failsafe()
```

---

## lib.util 模块

工具函数。

### 常量

```python
PI = 3.141592653589793
ONE_G = 9.80665  # m/s²
```

### 函数

#### `radians(deg: float) -> float`

角度转弧度。

```python
from lib.util import radians
rad = radians(180)  # PI
```

#### `degrees(rad: float) -> float`

弧度转角度。

#### `constrain(value: float, min_val: float, max_val: float) -> float`

限制值范围。

```python
from lib.util import constrain
value = constrain(1.5, 0, 1)  # 1.0
```

#### `mapf(x: float, in_min: float, in_max: float, out_min: float, out_max: float) -> float`

线性映射。

#### `wrap_angle(angle: float) -> float`

角度归一化到 [-PI, PI]。

### Rate 类

频率控制。

```python
from lib.util import Rate

rate = Rate(100)  # 100 Hz
if rate.check(current_time):
    # 执行任务
    pass
```

#### 方法

##### `check(t: float) -> bool`

检查是否应该执行。
