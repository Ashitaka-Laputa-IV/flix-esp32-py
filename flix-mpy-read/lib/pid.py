"""
PID 控制器模块

实现标准的 PID (比例-积分-微分) 控制器，用于飞行控制。

特性:
- 支积分限幅 (抗积分饱和)
- 微分项低通滤波
- 时间间隔验证

使用示例:
    from lib.pid import PID
    
    pid = PID(p=1.0, i=0.1, d=0.01, windup=1.0)
    
    # 在控制循环中
    output = pid.update(error)
    
    # 重置控制器
    pid.reset()
"""

import math
from typing import Union
from .lpf import LowPassFilterScalar
from .vector import Vector

t = float('nan')

class PID:
    """
    PID 控制器类。
    
    参数:
        p: 比例增益
        i: 积分增益
        d: 微分增益
        windup: 积分限幅值 (防止积分饱和)
        d_alpha: 微分项低通滤波系数 (0-1, 1 表示无滤波)
        dt_max: 最大允许时间间隔 (秒)
    """
    def __init__(self, p: float = 0.0, i: float = 0.0, d: float = 0.0, 
                 windup: float = 0.0, d_alpha: float = 1.0, dt_max: float = 0.1) -> None:
        self.p = p
        self.i = i
        self.d = d
        self.windup = windup
        self.dt_max = dt_max
        
        self.derivative = 0.0
        self.integral = 0.0
        
        self.lpf = LowPassFilterScalar(d_alpha)
        
        self.prev_error = float('nan')
        self.prev_time = float('nan')
    
    def update(self, error: float) -> float:
        global t
        dt = t - self.prev_time
        
        if dt > 0 and dt < self.dt_max:
            self.integral += error * dt
            if not math.isnan(self.prev_error):
                self.derivative = self.lpf.update((error - self.prev_error) / dt)
        else:
            self.integral = 0.0
            self.derivative = 0.0
        
        self.prev_error = error
        self.prev_time = t
        
        i_term = self.i * self.integral
        if self.windup > 0:
            i_term = max(-self.windup, min(self.windup, i_term))
        
        return self.p * error + i_term + self.d * self.derivative
    
    def reset(self) -> None:
        self.prev_error = float('nan')
        self.prev_time = float('nan')
        self.integral = 0.0
        self.derivative = 0.0
        self.lpf.reset()
