"""
Flix-mpy: ESP32 四轴飞行器固件 - MicroPython 实现

这是 flix 四轴飞行器固件的 MicroPython 移植版本。
支持姿态稳定 (STAB)、特技 (ACRO)、原始控制 (RAW) 和自主 (AUTO) 飞行模式。

模块结构:
- main.py: 主程序入口和全局状态
- lib/vector.py: 三维向量数学库
- lib/quaternion.py: 四元数旋转库
- lib/pid.py: PID 控制器
- lib/lpf.py: 低通滤波器
- lib/control.py: 飞行控制逻辑
- lib/estimate.py: 姿态估计
- lib/imu.py: IMU 传感器驱动 (MPU9250)
- lib/motors.py: 电机 PWM 控制
- lib/rc.py: RC 接收机 (SBUS)
- lib/wifi.py: Wi-Fi 通信
- lib/mavlink.py: MAVLink 协议
- lib/cli.py: 命令行界面
- lib/parameters.py: 参数存储
- lib/log.py: 飞行日志
- lib/led.py: LED 控制
- lib/safety.py: 安全保护

使用方法:
    import main
    main.run()  # 启动主循环

作者: Oleg Kalachev <okalachev@gmail.com>
仓库: https://github.com/okalachev/flix
"""

import math
import time

t = float('nan')
dt = 0.0
loop_rate = 0.0

gyro = None
acc = None
rates = None
attitude = None

control_roll = 0.0
control_pitch = 0.0
control_yaw = 0.0
control_throttle = 0.0
control_mode = float('nan')
control_time = float('nan')

landed = False
motors = [0.0, 0.0, 0.0, 0.0]

_initialized = False

def _init_globals():
    """初始化全局变量对象 (Vector 和 Quaternion 实例)"""
    global gyro, acc, rates, attitude
    from lib.vector import Vector
    from lib.quaternion import Quaternion
    
    gyro = Vector()
    acc = Vector()
    rates = Vector()
    attitude = Quaternion()

def setup():
    """
    初始化所有硬件和软件模块。
    
    初始化顺序:
    1. 全局变量对象
    2. LED 指示灯
    3. 参数系统
    4. 电机 PWM
    5. Wi-Fi 网络
    6. IMU 传感器
    7. RC 接收机
    """
    global _initialized
    
    _init_globals()
    
    print("Initializing flix-mpy")
    
    from lib import led
    led.setup()
    led.set_led(True)
    
    from lib import parameters
    parameters.setup()
    
    from lib import motors
    motors.setup()
    
    from lib import wifi
    wifi.setup()
    
    from lib import imu
    imu.setup()
    
    from lib import rc
    rc.setup()
    
    led.set_led(False)
    
    _initialized = True
    print("Initializing complete")

def step():
    """
    更新时间变量。
    
    计算:
    - t: 当前时间 (秒)
    - dt: 与上一步的时间间隔 (秒)
    - loop_rate: 循环频率 (Hz)
    """
    global t, dt, loop_rate
    
    now = time.ticks_us() / 1000000.0
    dt = now - t if not math.isnan(t) else 0.0
    t = now
    
    _compute_loop_rate()

def _compute_loop_rate():
    """计算主循环频率 (每秒更新一次)"""
    global loop_rate
    
    static = {'window_start': 0.0, 'count': 0}
    static['count'] += 1
    
    if t - static['window_start'] >= 1.0:
        loop_rate = static['count']
        static['window_start'] = t
        static['count'] = 0

def loop():
    """
    主循环单次迭代。
    
    执行顺序:
    1. 读取 IMU 传感器数据
    2. 更新时间
    3. 读取 RC 接收机输入
    4. 估计姿态
    5. 执行飞行控制
    6. 发送电机 PWM 信号
    7. 处理命令行输入
    8. 处理 MAVLink 通信
    9. 记录飞行日志
    10. 同步参数到存储
    """
    from lib import imu, rc, estimate, control, motors, cli, mavlink, log, parameters
    
    imu.read()
    step()
    rc.read()
    estimate.estimate()
    control.control()
    motors.send()
    cli.handle_input()
    mavlink.process()
    log.log_data()
    parameters.sync()

def run():
    """
    启动飞行器主程序。
    
    调用 setup() 初始化后进入无限主循环。
    捕获 KeyboardInterrupt 优雅退出，其他异常则重启设备。
    """
    setup()
    while True:
        loop()
