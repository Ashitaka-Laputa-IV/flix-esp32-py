"""
安全保护模块

实现飞行器的安全保护功能，防止意外事故。

保护功能:
1. RC 信号丢失保护
   - 超过 rc_loss_timeout 秒未收到 RC 信号
   - 自动切换到 AUTO 模式并缓慢下降

2. 自动模式退出保护
   - 检测到飞手输入时自动退出 AUTO 模式
   - 防止自动飞行时飞手无法接管

参数:
- rc_loss_timeout: RC 信号丢失超时时间 (秒)
- descend_time: 缓慢下降时间 (秒)

使用示例:
    from lib import safety
    
    # 在主循环中调用
    safety.failsafe()
"""

import math
from lib.control import mode, STAB, AUTO, armed, attitude_target, thrust_target

rc_loss_timeout = 1.0
descend_time = 10.0

_prev_controls = {'roll': 0.0, 'pitch': 0.0, 'yaw': 0.0, 'throttle': 0.0}

def failsafe():
    _rc_loss_failsafe()
    _auto_failsafe()

def _rc_loss_failsafe():
    import main
    from lib.control import armed
    
    if not armed:
        return
    
    if main.t - main.control_time > rc_loss_timeout:
        _descend()

def _descend():
    from lib import control
    import main
    
    control.mode = AUTO
    control.attitude_target.w, control.attitude_target.x, control.attitude_target.y, control.attitude_target.z = 1, 0, 0, 0
    control.thrust_target -= main.dt / descend_time
    
    if control.thrust_target < 0:
        control.thrust_target = 0
        control.armed = False

def _auto_failsafe():
    global _prev_controls
    from lib import control
    import main
    
    if (_prev_controls['roll'] != main.control_roll or 
        _prev_controls['pitch'] != main.control_pitch or 
        _prev_controls['yaw'] != main.control_yaw or 
        abs(_prev_controls['throttle'] - main.control_throttle) > 0.05):
        
        if control.mode == AUTO:
            control.mode = STAB
    
    _prev_controls['roll'] = main.control_roll
    _prev_controls['pitch'] = main.control_pitch
    _prev_controls['yaw'] = main.control_yaw
    _prev_controls['throttle'] = main.control_throttle
