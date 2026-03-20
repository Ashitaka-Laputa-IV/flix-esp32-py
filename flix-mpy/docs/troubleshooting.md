# 故障排除

本文档列出了常见问题及其解决方案。

## IMU 问题

### 问题：IMU 无数据

**症状**：
- `imu.acc` 和 `imu.gyro` 始终为零
- 控制台显示 IMU 初始化失败

**解决方案**：

1. 检查 I2C 连接：
```python
from machine import I2C, Pin
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
print(i2c.scan())  # 应显示 0x68 或 0x69
```

2. 检查 IMU 地址：
```python
# MPU9250 默认地址是 0x68
# 如果 AD0 引脚接高电平，地址是 0x69
```

3. 检查电源：
- 确保 IMU 有 3.3V 供电
- 检查 GND 连接

### 问题：姿态估计漂移

**症状**：
- 飞行器静止时姿态持续变化
- 姿态与实际不符

**解决方案**：

1. 校准陀螺仪：
```python
# 将飞行器静止放置
calibrate gyro
```

2. 校准加速度计：
```python
calibrate accel
```

3. 检查 IMU 安装方向参数：
```python
param get IMU_ROT_ROLL
param get IMU_ROT_PITCH
param get IMU_ROT_YAW
```

### 问题：加速度计读数异常

**症状**：
- 加速度计读数过大或过小
- 静止时读数不为 1G

**解决方案**：

1. 重新校准加速度计
2. 检查加速度计比例因子参数：
```python
param get IMU_ACC_SCALE_X
param get IMU_ACC_SCALE_Y
param get IMU_ACC_SCALE_Z
```

---

## RC 问题

### 问题：RC 无信号

**症状**：
- `rc.channels` 全为零
- 无法控制飞行器

**解决方案**：

1. 检查 UART 连接：
```python
from machine import UART
uart = UART(1, baudrate=100000)
print(uart.any())  # 检查是否有数据
```

2. 检查 SBUS 信号：
- 确认接收机已对频
- 检查接收机 LED 状态
- 确认使用的是 SBUS 输出（不是 PWM）

3. 检查 UART 引脚：
```python
# 默认使用 UART1, RX=GPIO16
# 确认接线正确
```

### 问题：RC 通道值异常

**症状**：
- 通道值超出范围
- 通道值不随摇杆变化

**解决方案**：

1. 重新校准 RC：
```python
calibrate rc
```

2. 检查通道映射：
```python
param get RC_ROLL
param get RC_PITCH
param get RC_THROTTLE
param get RC_YAW
```

---

## 电机问题

### 问题：电机不转

**症状**：
- 解锁后电机不转动
- `motor test` 命令无效

**解决方案**：

1. 检查电机引脚配置：
```python
param get MOT_PIN_FL
param get MOT_PIN_FR
param get MOT_PIN_RL
param get MOT_PIN_RR
```

2. 检查 PWM 输出：
```python
from machine import Pin, PWM
pwm = PWM(Pin(27))
pwm.freq(400)
pwm.duty(1000)  # 测试输出
```

3. 检查电调校准：
- 确认电调支持配置的 PWM 频率
- 可能需要单独校准电调

### 问题：电机转向错误

**症状**：
- 电机旋转方向与预期相反

**解决方案**：

1. 交换电机任意两根相线
2. 或在电调设置中反转方向（如果支持）

### 问题：电机抖动

**症状**：
- 电机低速时抖动
- 发出异响

**解决方案**：

1. 提高 PWM 频率：
```python
param set MOT_PWM_FREQ 400
```

2. 检查电调设置
3. 检查电池电压是否充足

---

## Wi-Fi 问题

### 问题：无法连接 Wi-Fi

**症状**：
- 找不到 `flix` 热点
- 无法连接到地面站

**解决方案**：

1. 检查 Wi-Fi 模式：
```python
param get WIFI_MODE  # 应为 1 (AP 模式)
```

2. 检查天线连接
3. 重启 ESP32

### 问题：Wi-Fi 连接延迟高

**症状**：
- 遥控响应慢
- MAVLink 数据延迟

**解决方案**：

1. 减少遥测频率
2. 靠近 Wi-Fi 热点
3. 避免干扰源

---

## MAVLink 问题

### 问题：QGroundControl 无法连接

**症状**：
- QGC 不显示飞行器
- 无遥测数据

**解决方案**：

1. 确认已连接到 `flix` Wi-Fi
2. 检查 UDP 端口：
```python
param get WIFI_LOC_PORT  # 默认 14550
```

3. 检查 QGC 设置中的 UDP 连接

### 问题：参数不显示

**症状**：
- QGC 参数列表为空
- 无法修改参数

**解决方案**：

1. 确保参数已初始化：
```python
from lib import parameters
parameters.setup()
```

2. 检查 params.json 文件

---

## 控制问题

### 问题：飞行器不稳定

**症状**：
- 飞行器震荡
- 无法保持姿态

**解决方案**：

1. 降低 P 增益：
```python
param set CTL_R_P 0.3
param set CTL_P_P 0.3
```

2. 增加 D 增益：
```python
param set CTL_R_D 0.02
param set CTL_P_D 0.02
```

3. 检查重心位置
4. 检查电机安装是否牢固

### 问题：飞行器漂移

**症状**：
- 飞行器向一侧倾斜
- 无法悬停

**解决方案**：

1. 重新校准加速度计
2. 检查 IMU 安装方向
3. 检查电机推力是否均衡
4. 调整 I 增益：
```python
param set CTL_R_I 0.1
param set CTL_P_I 0.1
```

### 问题：无法解锁

**症状**：
- `arm` 命令无效
- 电机不启动

**解决方案**：

1. 检查油门位置：
- 油门必须在最低位置才能解锁

2. 检查安全状态：
```python
from lib import safety
safety.failsafe()
```

3. 检查 IMU 状态：
```python
from lib import estimate
print(estimate.landed)  # 应为 True
```

---

## 系统问题

### 问题：循环频率低

**症状**：
- `loop_rate` 低于 300 Hz
- 系统响应慢

**解决方案**：

1. 减少调试输出
2. 检查是否有阻塞操作
3. 优化代码性能

### 问题：内存不足

**症状**：
- MemoryError
- 系统崩溃

**解决方案**：

1. 检查内存使用：
```python
import gc
print(gc.mem_free())
```

2. 减少日志缓冲区大小
3. 避免在循环中创建对象

### 问题：系统重启

**症状**：
- 飞行中突然重启
- 看门狗超时

**解决方案**：

1. 检查电源稳定性
2. 检查是否有死循环
3. 增加看门狗喂狗频率

---

## 调试工具

### 查看系统状态

```python
import main
print(f"Time: {main.t}")
print(f"Loop rate: {main.loop_rate}")
print(f"Armed: {main.armed}")
```

### 查看传感器数据

```python
from lib import imu, estimate
print(f"Accel: {imu.acc.x}, {imu.acc.y}, {imu.acc.z}")
print(f"Gyro: {imu.gyro.x}, {imu.gyro.y}, {imu.gyro.z}")
print(f"Attitude: {estimate.attitude.to_euler()}")
```

### 查看控制状态

```python
from lib import control
print(f"Mode: {control.mode}")
print(f"Thrust: {control.thrust_target}")
print(f"Torque: {control.torque_target.x}, {control.torque_target.y}, {control.torque_target.z}")
```

### 导出诊断信息

```python
import main
from lib import imu, estimate, control, motors, rc

print("=== System Diagnostics ===")
print(f"Loop rate: {main.loop_rate} Hz")
print(f"Armed: {control.armed}")
print(f"Mode: {control.mode}")
print(f"IMU: acc={imu.acc}, gyro={imu.gyro}")
print(f"Attitude: {estimate.attitude.to_euler()}")
print(f"Motors: {motors.motors}")
print(f"RC: {rc.channels[:4]}")
```

---

## 获取帮助

如果以上方法无法解决问题：

1. 查看项目 GitHub Issues
2. 在社区论坛提问
3. 提交 Bug 报告，包含：
   - 问题描述
   - 复现步骤
   - 系统诊断信息
   - 硬件配置
