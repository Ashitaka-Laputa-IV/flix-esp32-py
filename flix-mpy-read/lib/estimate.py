"""
姿态估计模块

使用 IMU 传感器数据估计飞行器的姿态。

算法:
1. 陀螺仪积分: 使用角速度更新姿态四元数
2. 加速度计校正: 当飞行器静止时，使用重力方向校正姿态漂移

状态:
- rates: 估计的角速度 (rad/s)
- attitude: 估计的姿态四元数
- landed: 是否已着陆 (用于判断是否应用加速度计校正)

使用示例:
    from lib import estimate
    
    # 在主循环中调用
    estimate.estimate()
    
    # 获取当前姿态
    euler = estimate.attitude.to_euler()
    print(f"Roll: {euler.x}, Pitch: {euler.y}, Yaw: {euler.z}")
"""

import math
from lib.vector import Vector
from lib.quaternion import Quaternion
from lib.lpf import LowPassFilter
from lib.util import ONE_G

rates = Vector()
attitude = Quaternion()
landed = False

acc_weight = 0.003
rates_filter = LowPassFilter(0.2)

def estimate() -> None:
    global rates, attitude, landed
    
    import main
    from lib.motors import active
    
    _apply_gyro()
    _apply_acc()

def _apply_gyro() -> None:
    global rates, attitude
    
    import main
    
    rates = rates_filter.update(main.gyro)
    
    rotation = Quaternion.from_rotation_vector(rates * main.dt)
    attitude = Quaternion.rotate(attitude, rotation)
    
    main.rates.x, main.rates.y, main.rates.z = rates.x, rates.y, rates.z

def _apply_acc() -> None:
    global landed, attitude
    
    import main
    from lib.motors import active
    
    acc_norm = main.acc.norm()
    landed = not active() and abs(acc_norm - ONE_G) < ONE_G * 0.1
    main.landed = landed
    
    if not landed:
        return
    
    up = Quaternion.rotate_vector(Vector(0, 0, 1), attitude)
    correction = Vector.rotation_vector_between(main.acc, up) * acc_weight
    
    rot = Quaternion.from_rotation_vector(correction)
    attitude = Quaternion.rotate(attitude, rot)
    
    main.attitude.w, main.attitude.x, main.attitude.y, main.attitude.z = attitude.w, attitude.x, attitude.y, attitude.z
