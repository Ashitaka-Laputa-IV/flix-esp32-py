"""
工具函数模块

提供常用的数学和实用函数。

数学常量:
- PI: 圆周率
- ONE_G: 标准重力加速度 (m/s²)

角度转换:
- radians(deg): 角度转弧度
- degrees(rad): 弧度转角度

数值处理:
- constrain(value, min_val, max_val): 限制值范围
- mapf(x, in_min, in_max, out_min, out_max): 线性映射
- wrap_angle(angle): 角度归一化到 [-PI, PI]

时间工具:
- Rate: 频率控制类

使用示例:
    from lib.util import constrain, radians, Rate
    
    # 限制值范围
    value = constrain(1.5, 0, 1)  # 返回 1
    
    # 角度转换
    rad = radians(180)  # 返回 PI
    
    # 频率控制
    rate = Rate(100)  # 100Hz
    if rate.check(current_time):
        # 执行 100Hz 的任务
        pass
"""

import math

PI = math.pi
ONE_G = 9.80665

def mapf(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def invalid(x):
    return not math.isfinite(x)

def valid(x):
    return math.isfinite(x)

def wrap_angle(angle):
    angle = math.fmod(angle, 2 * math.pi)
    if angle > math.pi:
        angle -= 2 * math.pi
    elif angle < -math.pi:
        angle += 2 * math.pi
    return angle

def constrain(value, min_val, max_val):
    return max(min_val, min(max_val, value))

def radians(deg):
    return deg * math.pi / 180.0

def degrees(rad):
    return rad * 180.0 / math.pi


class Rate:
    def __init__(self, rate):
        self.rate = rate
        self.last = 0.0
    
    def check(self, current_time):
        if current_time - self.last >= 1.0 / self.rate:
            self.last = current_time
            return True
        return False
    
    def __bool__(self):
        from main import t
        return self.check(t)


class Delay:
    def __init__(self, delay):
        self.delay = delay
        self.start = float('nan')
    
    def update(self, on, current_time):
        if not on:
            self.start = float('nan')
            return False
        elif math.isnan(self.start):
            self.start = current_time
        return current_time - self.start >= self.delay
