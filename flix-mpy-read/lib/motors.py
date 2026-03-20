"""
电机控制模块

控制四个无刷电机的 PWM 输出。

电机布局 (X 型四轴):
    FL 3   FR 2
      \\ /
       X
      / \\
    RL 0   RR 1

FL = 前左, FR = 前右, RL = 后左, RR = 后右

PWM 配置:
- 频率: 78kHz (适合大多数电调)
- 分辨率: 10 位 (0-1023)
- 输出范围: 0.0 - 1.0 (归一化推力)

使用示例:
    from lib import motors
    
    # 初始化
    motors.setup()
    
    # 设置推力
    motors.motors[0] = 0.5  # 后左电机 50% 推力
    motors.send()
    
    # 测试单个电机
    motors.test_motor(motors.MOTOR_FRONT_LEFT)
"""

from machine import Pin, PWM
from typing import List
from .util import constrain, mapf

MOTOR_REAR_LEFT = 0
MOTOR_REAR_RIGHT = 1
MOTOR_FRONT_RIGHT = 2
MOTOR_FRONT_LEFT = 3

motors: List[float] = [0.0, 0.0, 0.0, 0.0]

motor_pins = [12, 13, 14, 15]
pwm_frequency = 78000
pwm_resolution = 10
pwm_stop = 0
pwm_min = 0
pwm_max = -1

_pwms: List[PWM] = []

def setup() -> None:
    global _pwms
    print("Setup Motors")
    
    _pwms = []
    for pin_num in motor_pins:
        pin = Pin(pin_num)
        pwm = PWM(pin, freq=pwm_frequency, duty=0)
        _pwms.append(pwm)
    
    send()
    print("Motors initialized")

def send() -> None:
    for i, pwm in enumerate(_pwms):
        duty = _get_duty_cycle(motors[i])
        pwm.duty(duty)

def _get_duty_cycle(value: float) -> int:
    value = constrain(value, 0, 1)
    
    if pwm_max >= 0:
        # 映射到 PWM 脉宽范围
        pwm_val = mapf(value, 0, 1, pwm_min, pwm_max)
        # 完全停转时使用停止脉宽
        if value == 0:
            pwm_val = pwm_stop
        # 转换为占空比
        # 1000000 / pwm_frequency = 周期 (微秒)
        # (1 << pwm_resolution) - 1 = 最大占空比计数
        duty = mapf(pwm_val, 0, 1000000 / pwm_frequency, 0, (1 << pwm_resolution) - 1)
        return int(round(duty))
    else:
        # 直接归一化到分辨率范围
        return int(round(value * ((1 << pwm_resolution) - 1)))

def active() -> bool:
    return any(m != 0 for m in motors)

def test_motor(n: int) -> None:
    print(f"Testing motor {n}")
    motors[n] = 1.0
    import time
    time.sleep_ms(50)
    send()
    time.sleep(3)
    motors[n] = 0.0
    send()
    print("Done")
