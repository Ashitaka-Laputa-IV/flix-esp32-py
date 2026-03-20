"""
低通滤波器模块

提供一阶低通滤波器实现，用于信号平滑。

滤波器公式:
    output = output + alpha * (input - output)

其中 alpha 是平滑系数，取值范围 0-1:
- alpha = 1: 无滤波 (直接通过)
- alpha = 0: 完全滤波 (输出不变)

使用示例:
    from lib.lpf import LowPassFilter, LowPassFilterScalar
    
    # 向量滤波器
    lpf = LowPassFilter(alpha=0.1)
    filtered = lpf.update(raw_vector)
    
    # 标量滤波器
    lpf_scalar = LowPassFilterScalar(alpha=0.2)
    filtered_value = lpf_scalar.update(raw_value)
"""

import math
from .vector import Vector

class LowPassFilter:
    """
    向量低通滤波器。
    
    参数:
        alpha: 平滑系数 (0-1)
        initial: 初始输出值 (默认为零向量)
    """
    def __init__(self, alpha=1.0, initial=None):
        self.alpha = alpha
        if initial is None:
            self.output = Vector()
        else:
            self.output = initial.copy() if hasattr(initial, 'copy') else initial
    
    def update(self, input_val):
        if hasattr(self.output, '__iadd__'):
            self.output += self.alpha * (input_val - self.output)
        else:
            self.output = self.output + self.alpha * (input_val - self.output)
        return self.output
    
    def set_cutoff_frequency(self, cutoff_freq, dt):
        import math
        self.alpha = 1 - math.exp(-2 * math.pi * cutoff_freq * dt)
    
    def reset(self):
        if hasattr(self.output, '__class__'):
            self.output = self.output.__class__()
        else:
            self.output = 0.0


class LowPassFilterScalar:
    def __init__(self, alpha=1.0, initial=0.0):
        self.alpha = alpha
        self.output = initial
    
    def update(self, input_val):
        self.output += self.alpha * (input_val - self.output)
        return self.output
    
    def set_cutoff_frequency(self, cutoff_freq, dt):
        import math
        self.alpha = 1 - math.exp(-2 * math.pi * cutoff_freq * dt)
    
    def reset(self):
        self.output = 0.0
