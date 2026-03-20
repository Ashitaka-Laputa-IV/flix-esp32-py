"""
飞行控制模块

实现四轴飞行器的飞行控制逻辑，支持多种飞行模式:
- STAB: 姿态稳定模式 - 飞手控制倾斜角度
- ACRO: 特技模式 - 飞手控制角速度
- RAW: 原始模式 - 直接控制电机扭矩
- AUTO: 自主模式 - 由 MAVLink 控制

控制层级:
1. 姿态控制 -> 输出目标角速度
2. 角速度控制 -> 输出目标扭矩
3. 扭矩混合 -> 输出电机推力

使用示例:
    from lib import control
    
    # 解锁
    control.armed = True
    
    # 设置模式
    control.mode = control.STAB
    
    # 执行控制循环
    control.control()
"""

import math
from lib.vector import Vector
from lib.quaternion import Quaternion
from lib.pid import PID
from lib.util import wrap_angle, constrain, radians

RAW = 0
ACRO = 1
STAB = 2
AUTO = 3

mode = STAB
armed = False

attitude_target = Quaternion()
rates_target = Vector()
rates_extra = Vector()
torque_target = Vector()
thrust_target = 0.0

PITCHRATE_P = 0.05
PITCHRATE_I = 0.2
PITCHRATE_D = 0.001
PITCHRATE_I_LIM = 0.3
ROLLRATE_P = PITCHRATE_P
ROLLRATE_I = PITCHRATE_I
ROLLRATE_D = PITCHRATE_D
ROLLRATE_I_LIM = PITCHRATE_I_LIM
YAWRATE_P = 0.3
YAWRATE_I = 0.0
YAWRATE_D = 0.0
YAWRATE_I_LIM = 0.3
ROLL_P = 6
ROLL_I = 0
ROLL_D = 0
PITCH_P = ROLL_P
PITCH_I = ROLL_I
PITCH_D = ROLL_D
YAW_P = 3
PITCHRATE_MAX = radians(360)
ROLLRATE_MAX = radians(360)
YAWRATE_MAX = radians(300)
TILT_MAX = radians(30)
RATES_D_LPF_ALPHA = 0.2

roll_rate_pid = PID(ROLLRATE_P, ROLLRATE_I, ROLLRATE_D, ROLLRATE_I_LIM, RATES_D_LPF_ALPHA)
pitch_rate_pid = PID(PITCHRATE_P, PITCHRATE_I, PITCHRATE_D, PITCHRATE_I_LIM, RATES_D_LPF_ALPHA)
yaw_rate_pid = PID(YAWRATE_P, YAWRATE_I, YAWRATE_D)
roll_pid = PID(ROLL_P, ROLL_I, ROLL_D)
pitch_pid = PID(PITCH_P, PITCH_I, PITCH_D)
yaw_pid = PID(YAW_P, 0, 0)

max_rate = Vector(ROLLRATE_MAX, PITCHRATE_MAX, YAWRATE_MAX)
tilt_max = TILT_MAX

flight_modes = [STAB, STAB, STAB]

_prev_controls = {'roll': 0.0, 'pitch': 0.0, 'yaw': 0.0, 'throttle': 0.0}

def control():
    _interpret_controls()
    _failsafe()
    _control_attitude()
    _control_rates()
    _control_torque()

def _interpret_controls():
    global mode, armed, thrust_target, rates_target, rates_extra, torque_target
    
    import main
    
    if math.isnan(main.control_mode):
        pass
    elif main.control_mode < 0.25:
        mode = flight_modes[0]
    elif main.control_mode < 0.75:
        mode = flight_modes[1]
    elif main.control_mode > 0.75:
        mode = flight_modes[2]
    
    if mode == AUTO:
        return
    
    if main.control_throttle < 0.05 and main.control_yaw > 0.95:
        armed = True
    if main.control_throttle < 0.05 and main.control_yaw < -0.95:
        armed = False
    
    yaw_input = main.control_yaw
    if abs(yaw_input) < 0.1:
        yaw_input = 0
    
    thrust_target = main.control_throttle
    
    if mode == STAB:
        yaw_target = attitude_target.get_yaw()
        if not armed or math.isnan(yaw_target) or yaw_input != 0:
            yaw_target = main.attitude.get_yaw()
        attitude_target = Quaternion.from_euler(Vector(main.control_roll * tilt_max, main.control_pitch * tilt_max, yaw_target))
        rates_extra = Vector(0, 0, -yaw_input * max_rate.z)
    
    elif mode == ACRO:
        attitude_target.invalidate()
        rates_target.x = main.control_roll * max_rate.x
        rates_target.y = main.control_pitch * max_rate.y
        rates_target.z = -yaw_input * max_rate.z
    
    elif mode == RAW:
        attitude_target.invalidate()
        rates_target.invalidate()
        torque_target.x = main.control_roll * 0.1
        torque_target.y = main.control_pitch * 0.1
        torque_target.z = -yaw_input * 0.1

def _control_attitude():
    global rates_target
    
    import main
    from lib.estimate import attitude
    
    if not armed or attitude_target.invalid() or thrust_target < 0.1:
        return
    
    up = Vector(0, 0, 1)
    up_actual = Quaternion.rotate_vector(up, attitude)
    up_target = Quaternion.rotate_vector(up, attitude_target)
    
    error = Vector.rotation_vector_between(up_target, up_actual)
    
    rates_target.x = roll_pid.update(error.x) + rates_extra.x
    rates_target.y = pitch_pid.update(error.y) + rates_extra.y
    
    yaw_error = wrap_angle(attitude_target.get_yaw() - attitude.get_yaw())
    rates_target.z = yaw_pid.update(yaw_error) + rates_extra.z

def _control_rates():
    global torque_target
    
    import main
    from lib.estimate import rates
    
    if not armed or rates_target.invalid() or thrust_target < 0.1:
        return
    
    error = rates_target - rates
    
    torque_target.x = roll_rate_pid.update(error.x)
    torque_target.y = pitch_rate_pid.update(error.y)
    torque_target.z = yaw_rate_pid.update(error.z)

def _control_torque():
    import main
    from lib.motors import motors, MOTOR_FRONT_LEFT, MOTOR_FRONT_RIGHT, MOTOR_REAR_LEFT, MOTOR_REAR_RIGHT
    
    if not torque_target.valid():
        return
    
    if not armed:
        for i in range(4):
            motors[i] = 0.0
            main.motors[i] = 0.0
        return
    
    if thrust_target < 0.1:
        motors[MOTOR_FRONT_LEFT] = 0.1
        motors[MOTOR_FRONT_RIGHT] = 0.1
        motors[MOTOR_REAR_LEFT] = 0.1
        motors[MOTOR_REAR_RIGHT] = 0.1
        main.motors[MOTOR_FRONT_LEFT] = 0.1
        main.motors[MOTOR_FRONT_RIGHT] = 0.1
        main.motors[MOTOR_REAR_LEFT] = 0.1
        main.motors[MOTOR_REAR_RIGHT] = 0.1
        return
    
    motors[MOTOR_FRONT_LEFT] = thrust_target + torque_target.x - torque_target.y + torque_target.z
    motors[MOTOR_FRONT_RIGHT] = thrust_target - torque_target.x - torque_target.y - torque_target.z
    motors[MOTOR_REAR_LEFT] = thrust_target + torque_target.x + torque_target.y - torque_target.z
    motors[MOTOR_REAR_RIGHT] = thrust_target - torque_target.x + torque_target.y + torque_target.z
    
    for i in range(4):
        motors[i] = constrain(motors[i], 0, 1)
        main.motors[i] = motors[i]

def _failsafe():
    from lib import safety
    safety.failsafe()

def get_mode_name():
    names = {RAW: "RAW", ACRO: "ACRO", STAB: "STAB", AUTO: "AUTO"}
    return names.get(mode, "UNKNOWN")
