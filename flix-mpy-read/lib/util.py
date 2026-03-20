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
- Delay: 延时类

使用示例:
    from lib.util import constrain, radians, Rate
    
    # 限制值范围
    value = constrain(1.5, 0, 1)  # 返回 1
    
    # 角度转换
    rad = radians(180)  # 返回 PI
    
    # 频率控制
    rate = Rate(100)  # 100 Hz
    if rate.check(current_time):
        # 执行 100Hz 的任务
        pass
"""

import math
from typing import Optional

PI = math.pi
ONE_G = 9.80665

def mapf(x: float, in_min: float, in_max: float, out_min: float, out_max: float) -> float:
    """
    线性映射值范围
    
    参数:
        x: 输入值
        in_min: 输入最小值
        in_max: 输入最大值
        out_min: 输出最小值
        out_max: 输出最大值
    
    返回:
        映射后的值
    """
    #(x - in_min) / (in_max - in_min) = (res - out_min) / (out_max - out_min)
    # => res = (x - in_min) / (in_max - in_min) * (out_max - out_min) + out_min
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def invalid(x: float) -> bool:
    """
    判断值是否无效
    
    参数:
        x: 输入值
    
    返回:
        无效返回 True，否则 False
    """
    return not math.isfinite(x)

def valid(x: float) -> bool:
    """
    判断值是否有效
    
    参数:
        x: 输入值
    
    返回:
        有效返回 True，否则 False
    """
    return math.isfinite(x)

def wrap_angle(angle: float) -> float:
    """
    角度归一化到 [-π, π]
    
    参数:
        angle: 输入角度 (弧度)
    
    返回:
        归一化后的角度
    """
    angle = math.fmod(angle, 2 * math.pi)
    if angle > math.pi:
        angle -= 2 * math.pi
    elif angle < -math.pi:
        angle += 2 * math.pi
    return angle

def constrain(value: float, min_val: float, max_val: float) -> float:
    """
    限制值范围
    
    参数:
        value: 输入值
        min_val: 最小值
        max_val: 最大值
    
    返回:
        限制后的值
    """
    return max(min_val, min(max_val, value))

def radians(deg: float) -> float:
    """
    角度转弧度
    
    参数:
        deg: 输入角度 (度)
    
    返回:
        转换后的弧度
    """
    return deg * math.pi / 180.0

def degrees(rad: float) -> float:
    """
    弧度转角度
    
    参数:
        rad: 输入弧度
    
    返回:
        转换后的角度
    """
    return rad * 180.0 / math.pi


class Rate:
    """
    频率控制类
    
    用于控制任务执行频率
    """
    def __init__(self, rate: float) -> None:
        """
        初始化频率控制器
        
        参数:
            rate: 执行频率 (Hz)
        """
        self.rate = rate
        self.last = 0.0
    
    def check(self, current_time: float) -> bool:
        """
        检查是否达到执行频率
        
        参数:
            current_time: 当前时间 (秒)
        
        返回:
            达到频率返回 True，否则 False
        """
        if current_time - self.last >= 1.0 / self.rate:
            self.last = current_time
            return True
        return False
    
    def __bool__(self) -> bool:
        """
        重载布尔运算符
        
        返回:
            达到频率返回 True，否则 False
        """
        from main import t
        return self.check(t)


class Delay:
    """
    延时类
    
    用于实现延时功能
    """
    def __init__(self, delay: float) -> None:
        """
        初始化延时器
        
        参数:
            delay: 延时时间 (秒)
        """
        self.delay = delay
        self.start = float('nan')
    
    def update(self, on: bool, current_time: float) -> bool:
        """
        更新延时状态
        
        参数:
            on: 启动延时标志
            current_time: 当前时间 (秒)
        
        返回:
            延时完成返回 True，否则 False
        """
        if not on:
            self.start = float('nan')
            return False
        elif math.isnan(self.start):
            self.start = current_time
        return current_time - self.start >= self.delay
