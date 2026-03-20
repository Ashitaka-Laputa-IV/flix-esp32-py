"""
参数管理模块

提供参数的持久化存储和运行时管理。

功能:
- 参数自动加载和保存
- 参数变更回调
- 默认值管理
- 与各模块参数同步

参数命名规范:
- CTL_*: 控制参数
- IMU_*: IMU 传感器参数
- EST_*: 姿态估计参数
- MOT_*: 电机参数
- RC_*: RC 接收机参数
- WIFI_*: Wi-Fi 参数
- SF_*: 安全参数
- MAV_*: MAVLink 参数

存储位置: params.json 文件

使用示例:
    from lib import parameters
    
    # 初始化
    parameters.setup()
    
    # 获取参数
    value = parameters.get('CTL_R_P')
    
    # 设置参数
    parameters.set('CTL_R_P', 0.5)
    
    # 列出所有参数
    names = parameters.get_names()
    
    # 重置为默认值
    parameters.reset()
"""

import json
from machine import Flash

_params = {}
_cache = {}
_callbacks = {}

_default_params = {}

def setup():
    global _params, _cache
    
    print("Setup parameters")
    
    _init_defaults()
    
    try:
        with open('params.json', 'r') as f:
            _params = json.load(f)
    except:
        _params = {}
    
    for name, value in _default_params.items():
        if name not in _params:
            _params[name] = value
    
    _cache = dict(_params)
    
    _save()

def _init_defaults():
    global _default_params
    
    from .control import roll_rate_pid, pitch_rate_pid, yaw_rate_pid, roll_pid, pitch_pid, yaw_pid, max_rate, tilt_max, flight_modes
    from .imu import gyro_bias_filter, imu_rotation, acc_bias, acc_scale
    from .estimate import acc_weight, rates_filter
    from .motors import motor_pins, pwm_frequency, pwm_resolution, pwm_stop, pwm_min, pwm_max
    from .rc import channel_zero, channel_max, roll_channel, pitch_channel, throttle_channel, yaw_channel, mode_channel
    from .wifi import wifi_mode, udp_local_port, udp_remote_port
    from .safety import rc_loss_timeout, descend_time
    from .mavlink import mavlink_sys_id
    from .wifi import telemetry_slow, telemetry_fast
    
    _default_params = {
        'CTL_R_RATE_P': roll_rate_pid.p,
        'CTL_R_RATE_I': roll_rate_pid.i,
        'CTL_R_RATE_D': roll_rate_pid.d,
        'CTL_R_RATE_WU': roll_rate_pid.windup,
        'CTL_P_RATE_P': pitch_rate_pid.p,
        'CTL_P_RATE_I': pitch_rate_pid.i,
        'CTL_P_RATE_D': pitch_rate_pid.d,
        'CTL_P_RATE_WU': pitch_rate_pid.windup,
        'CTL_Y_RATE_P': yaw_rate_pid.p,
        'CTL_Y_RATE_I': yaw_rate_pid.i,
        'CTL_Y_RATE_D': yaw_rate_pid.d,
        'CTL_R_P': roll_pid.p,
        'CTL_R_I': roll_pid.i,
        'CTL_R_D': roll_pid.d,
        'CTL_P_P': pitch_pid.p,
        'CTL_P_I': pitch_pid.i,
        'CTL_P_D': pitch_pid.d,
        'CTL_Y_P': yaw_pid.p,
        'CTL_P_RATE_MAX': max_rate.y,
        'CTL_R_RATE_MAX': max_rate.x,
        'CTL_Y_RATE_MAX': max_rate.z,
        'CTL_TILT_MAX': tilt_max,
        'CTL_FLT_MODE_0': flight_modes[0],
        'CTL_FLT_MODE_1': flight_modes[1],
        'CTL_FLT_MODE_2': flight_modes[2],
        'IMU_ROT_ROLL': imu_rotation.x,
        'IMU_ROT_PITCH': imu_rotation.y,
        'IMU_ROT_YAW': imu_rotation.z,
        'IMU_ACC_BIAS_X': acc_bias.x,
        'IMU_ACC_BIAS_Y': acc_bias.y,
        'IMU_ACC_BIAS_Z': acc_bias.z,
        'IMU_ACC_SCALE_X': acc_scale.x,
        'IMU_ACC_SCALE_Y': acc_scale.y,
        'IMU_ACC_SCALE_Z': acc_scale.z,
        'IMU_GYRO_BIAS_A': gyro_bias_filter.alpha,
        'EST_ACC_WEIGHT': acc_weight,
        'EST_RATES_LPF_A': rates_filter.alpha,
        'MOT_PIN_FL': motor_pins[3],
        'MOT_PIN_FR': motor_pins[2],
        'MOT_PIN_RL': motor_pins[0],
        'MOT_PIN_RR': motor_pins[1],
        'MOT_PWM_FREQ': pwm_frequency,
        'MOT_PWM_RES': pwm_resolution,
        'MOT_PWM_STOP': pwm_stop,
        'MOT_PWM_MIN': pwm_min,
        'MOT_PWM_MAX': pwm_max,
        'RC_ZERO_0': channel_zero[0],
        'RC_ZERO_1': channel_zero[1],
        'RC_ZERO_2': channel_zero[2],
        'RC_ZERO_3': channel_zero[3],
        'RC_MAX_0': channel_max[0],
        'RC_MAX_1': channel_max[1],
        'RC_MAX_2': channel_max[2],
        'RC_MAX_3': channel_max[3],
        'RC_ROLL': roll_channel,
        'RC_PITCH': pitch_channel,
        'RC_THROTTLE': throttle_channel,
        'RC_YAW': yaw_channel,
        'RC_MODE': mode_channel,
        'WIFI_MODE': wifi_mode,
        'WIFI_LOC_PORT': udp_local_port,
        'WIFI_REM_PORT': udp_remote_port,
        'SF_RC_LOSS_TIME': rc_loss_timeout,
        'SF_DESCEND_TIME': descend_time,
        'MAV_SYS_ID': mavlink_sys_id,
    }

def get(name):
    return _params.get(name, float('nan'))

def set(name, value):
    if name not in _default_params:
        return False
    
    _params[name] = value
    _apply_param(name, value)
    
    if name in _callbacks:
        _callbacks[name]()
    
    return True

def _apply_param(name, value):
    from .control import roll_rate_pid, pitch_rate_pid, yaw_rate_pid, roll_pid, pitch_pid, yaw_pid, max_rate, tilt_max, flight_modes
    from .imu import gyro_bias_filter, imu_rotation, acc_bias, acc_scale
    from .estimate import acc_weight, rates_filter
    from .motors import motor_pins, pwm_frequency, pwm_resolution, pwm_stop, pwm_min, pwm_max
    from .rc import channel_zero, channel_max, roll_channel, pitch_channel, throttle_channel, yaw_channel, mode_channel
    from .wifi import wifi_mode, udp_local_port, udp_remote_port
    from .safety import rc_loss_timeout, descend_time
    from .mavlink import mavlink_sys_id
    
    if name == 'CTL_R_RATE_P': roll_rate_pid.p = value
    elif name == 'CTL_R_RATE_I': roll_rate_pid.i = value
    elif name == 'CTL_R_RATE_D': roll_rate_pid.d = value
    elif name == 'CTL_R_RATE_WU': roll_rate_pid.windup = value
    elif name == 'CTL_P_RATE_P': pitch_rate_pid.p = value
    elif name == 'CTL_P_RATE_I': pitch_rate_pid.i = value
    elif name == 'CTL_P_RATE_D': pitch_rate_pid.d = value
    elif name == 'CTL_P_RATE_WU': pitch_rate_pid.windup = value
    elif name == 'CTL_Y_RATE_P': yaw_rate_pid.p = value
    elif name == 'CTL_Y_RATE_I': yaw_rate_pid.i = value
    elif name == 'CTL_Y_RATE_D': yaw_rate_pid.d = value
    elif name == 'CTL_R_P': roll_pid.p = value
    elif name == 'CTL_R_I': roll_pid.i = value
    elif name == 'CTL_R_D': roll_pid.d = value
    elif name == 'CTL_P_P': pitch_pid.p = value
    elif name == 'CTL_P_I': pitch_pid.i = value
    elif name == 'CTL_P_D': pitch_pid.d = value
    elif name == 'CTL_Y_P': yaw_pid.p = value
    elif name == 'CTL_P_RATE_MAX': max_rate.y = value
    elif name == 'CTL_R_RATE_MAX': max_rate.x = value
    elif name == 'CTL_Y_RATE_MAX': max_rate.z = value
    elif name == 'CTL_TILT_MAX': tilt_max = value
    elif name == 'CTL_FLT_MODE_0': flight_modes[0] = int(value)
    elif name == 'CTL_FLT_MODE_1': flight_modes[1] = int(value)
    elif name == 'CTL_FLT_MODE_2': flight_modes[2] = int(value)
    elif name == 'IMU_ROT_ROLL': imu_rotation.x = value
    elif name == 'IMU_ROT_PITCH': imu_rotation.y = value
    elif name == 'IMU_ROT_YAW': imu_rotation.z = value
    elif name == 'IMU_ACC_BIAS_X': acc_bias.x = value
    elif name == 'IMU_ACC_BIAS_Y': acc_bias.y = value
    elif name == 'IMU_ACC_BIAS_Z': acc_bias.z = value
    elif name == 'IMU_ACC_SCALE_X': acc_scale.x = value
    elif name == 'IMU_ACC_SCALE_Y': acc_scale.y = value
    elif name == 'IMU_ACC_SCALE_Z': acc_scale.z = value
    elif name == 'IMU_GYRO_BIAS_A': gyro_bias_filter.alpha = value
    elif name == 'EST_ACC_WEIGHT': acc_weight = value
    elif name == 'EST_RATES_LPF_A': rates_filter.alpha = value
    elif name == 'MOT_PIN_FL': motor_pins[3] = int(value)
    elif name == 'MOT_PIN_FR': motor_pins[2] = int(value)
    elif name == 'MOT_PIN_RL': motor_pins[0] = int(value)
    elif name == 'MOT_PIN_RR': motor_pins[1] = int(value)
    elif name == 'MOT_PWM_FREQ': pwm_frequency = int(value)
    elif name == 'MOT_PWM_RES': pwm_resolution = int(value)
    elif name == 'MOT_PWM_STOP': pwm_stop = int(value)
    elif name == 'MOT_PWM_MIN': pwm_min = int(value)
    elif name == 'MOT_PWM_MAX': pwm_max = int(value)
    elif name == 'RC_ZERO_0': channel_zero[0] = int(value)
    elif name == 'RC_ZERO_1': channel_zero[1] = int(value)
    elif name == 'RC_ZERO_2': channel_zero[2] = int(value)
    elif name == 'RC_ZERO_3': channel_zero[3] = int(value)
    elif name == 'RC_MAX_0': channel_max[0] = int(value)
    elif name == 'RC_MAX_1': channel_max[1] = int(value)
    elif name == 'RC_MAX_2': channel_max[2] = int(value)
    elif name == 'RC_MAX_3': channel_max[3] = int(value)
    elif name == 'RC_ROLL': roll_channel = int(value)
    elif name == 'RC_PITCH': pitch_channel = int(value)
    elif name == 'RC_THROTTLE': throttle_channel = int(value)
    elif name == 'RC_YAW': yaw_channel = int(value)
    elif name == 'RC_MODE': mode_channel = int(value)
    elif name == 'WIFI_MODE': wifi_mode = int(value)
    elif name == 'WIFI_LOC_PORT': udp_local_port = int(value)
    elif name == 'WIFI_REM_PORT': udp_remote_port = int(value)
    elif name == 'SF_RC_LOSS_TIME': rc_loss_timeout = value
    elif name == 'SF_DESCEND_TIME': descend_time = value
    elif name == 'MAV_SYS_ID': mavlink_sys_id = int(value)

def get_names():
    return list(_default_params.keys())

def count():
    return len(_default_params)

def sync():
    from .motors import active
    from main import t
    from .util import Rate
    
    static = {'rate': Rate(1), 'last_time': 0}
    
    if not static['rate'].check(t):
        return
    
    if active():
        return
    
    changed = False
    for name, value in _params.items():
        if name not in _cache or _cache[name] != value:
            _cache[name] = value
            changed = True
    
    if changed:
        _save()

def _save():
    try:
        with open('params.json', 'w') as f:
            json.dump(_params, f)
    except:
        pass

def print_all():
    for name in get_names():
        print(f"{name} = {get(name)}")

def reset():
    global _params, _cache
    _params = dict(_default_params)
    _cache = dict(_default_params)
    _save()
    import machine
    machine.reset()
