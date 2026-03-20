"""
飞行日志模块

记录飞行过程中的关键数据，用于分析和调试。

记录数据:
- 时间戳
- 角速度 (实际值和目标值)
- 姿态角 (实际值和目标值)
- 推力目标

配置:
- LOG_RATE: 记录频率 (Hz)
- LOG_DURATION: 记录时长 (秒)
- LOG_SIZE: 缓冲区大小 (记录条数)

使用示例:
    from lib import log
    
    # 数据会在解锁后自动记录
    # 在主循环中调用
    log.log_data()
    
    # 打印日志头
    log.print_header()
    
    # 打印日志数据 (CSV 格式)
    log.print_data()
"""

import math
from typing import List
from lib.vector import Vector
from lib.quaternion import Quaternion
from lib.util import Rate

LOG_RATE = 100
LOG_DURATION = 10
LOG_SIZE = LOG_DURATION * LOG_RATE

_log_buffer: List[List[float]] = []
_log_pointer = 0
_period = None

def log_data() -> None:
    global _log_pointer, _period
    
    from lib.control import armed
    import main
    
    if not armed:
        return
    
    if _period is None:
        _period = Rate(LOG_RATE)
    
    if not _period.check(main.t):
        return
    
    from lib.control import rates_target, attitude_target, thrust_target
    from lib.estimate import rates, attitude
    
    attitude_euler = attitude.to_euler()
    attitude_target_euler = attitude_target.to_euler()
    
    entry = [
        main.t,
        rates.x, rates.y, rates.z,
        rates_target.x, rates_target.y, rates_target.z,
        attitude_euler.x, attitude_euler.y, attitude_euler.z,
        attitude_target_euler.x, attitude_target_euler.y, attitude_target_euler.z,
        thrust_target
    ]
    
    if len(_log_buffer) < LOG_SIZE:
        _log_buffer.append(entry)
    else:
        _log_buffer[_log_pointer] = entry
    
    _log_pointer = (_log_pointer + 1) % LOG_SIZE

def print_header() -> None:
    headers = ['t', 'rates.x', 'rates.y', 'rates.z',
               'ratesTarget.x', 'ratesTarget.y', 'ratesTarget.z',
               'attitude.x', 'attitude.y', 'attitude.z',
               'attitudeTarget.x', 'attitudeTarget.y', 'attitudeTarget.z',
               'thrustTarget']
    print(','.join(headers))

def print_data() -> None:
    for entry in _log_buffer:
        if entry[0] == 0:
            continue
        print(','.join(str(v) for v in entry))
