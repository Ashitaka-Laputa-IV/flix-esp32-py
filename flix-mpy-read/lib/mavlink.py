"""
MAVLink 通信模块

实现 MAVLink 协议，用于与地面站通信。

支持的消息:
- HEARTBEAT: 心跳信号
- ATTITUDE: 姿态数据
- SET_MODE: 设置飞行模式
- SET_POSITION_TARGET: 设置目标位置/姿态
- COMMAND_LONG: 执行命令 (解锁/上锁)
- RC_CHANNELS_OVERRIDE: RC 通道覆盖

遥测数据:
- 快速遥测 (50Hz): 姿态、角速度
- 慢速遥测 (1Hz): 系统状态、电池等

使用示例:
    from lib import mavlink
    
    # 初始化
    mavlink.setup()
    
    # 处理接收的数据
    mavlink.process()
    
    # 发送心跳
    mavlink.send_heartbeat()
"""

import struct
import time
from typing import Optional
from lib.util import Rate

MAV_TYPE_QUADROTOR = 2
MAV_AUTOPILOT_GENERIC = 0
MAV_MODE_FLAG_SAFETY_ARMED = 128
MAV_MODE_FLAG_MANUAL_INPUT_ENABLED = 64
MAV_MODE_FLAG_STABILIZE_ENABLED = 8
MAV_MODE_FLAG_AUTO_ENABLED = 4
MAV_STATE_STANDBY = 3
MAV_COMP_ID_AUTOPILOT1 = 1
MAV_COMP_ID_MISSION = 190

MAVLINK_STX = 0xFD

MAVLINK_MSG_ID_HEARTBEAT = 0
MAVLINK_MSG_ID_EXTENDED_SYS_STATE = 245
MAVLINK_MSG_ID_ATTITUDE_QUATERNION = 31
MAVLINK_MSG_ID_RC_CHANNELS_RAW = 35
MAVLINK_MSG_ID_ACTUATOR_CONTROL_TARGET = 140
MAVLINK_MSG_ID_SCALED_IMU = 26
MAVLINK_MSG_ID_MANUAL_CONTROL = 69
MAVLINK_MSG_ID_PARAM_REQUEST_LIST = 21
MAVLINK_MSG_ID_PARAM_REQUEST_READ = 20
MAVLINK_MSG_ID_PARAM_SET = 23
MAVLINK_MSG_ID_PARAM_VALUE = 22
MAVLINK_MSG_ID_COMMAND_LONG = 76
MAVLINK_MSG_ID_COMMAND_ACK = 77
MAVLINK_MSG_ID_AUTOPILOT_VERSION = 148
MAVLINK_MSG_ID_SET_ATTITUDE_TARGET = 82
MAVLINK_MSG_ID_SET_ACTUATOR_CONTROL_TARGET = 139
MAVLINK_MSG_ID_SERIAL_CONTROL = 126

MAV_RESULT_ACCEPTED = 0
MAV_RESULT_UNSUPPORTED = 3

MAV_CMD_REQUEST_MESSAGE = 512
MAV_CMD_COMPONENT_ARM_DISARM = 400
MAV_CMD_DO_SET_MODE = 176

MAV_VTOL_STATE_UNDEFINED = 0
MAV_LANDED_STATE_ON_GROUND = 1
MAV_LANDED_STATE_IN_AIR = 2

SERIAL_CONTROL_DEV_SHELL = 7

mavlink_sys_id = 1
mavlink_connected = False
_print_buffer = ""

_rx_buffer = bytearray(280)
_seq = 0
_telemetry_slow = None
_telemetry_fast = None

def process() -> None:
    global _seq, _print_buffer, _telemetry_slow, _telemetry_fast
    
    import main
    from lib import wifi
    
    if _telemetry_slow is None:
        _telemetry_slow = Rate(2)
        _telemetry_fast = Rate(10)
    
    if _telemetry_slow.check(main.t):
        _send_heartbeat()
        
        if not mavlink_connected:
            _receive()
            return
        
        _send_extended_sys_state()
    
    if mavlink_connected and _telemetry_fast.check(main.t):
        _send_attitude_quaternion()
        _send_rc_channels_raw()
        _send_actuator_control_target()
        _send_scaled_imu()
    
    if _print_buffer:
        _send_serial_control(_print_buffer)
        _print_buffer = ""
    
    _receive()

def _send_heartbeat() -> None:
    from lib import control
    
    base_mode = MAV_MODE_FLAG_MANUAL_INPUT_ENABLED
    if control.armed:
        base_mode |= MAV_MODE_FLAG_SAFETY_ARMED
    if control.mode == control.STAB:
        base_mode |= MAV_MODE_FLAG_STABILIZE_ENABLED
    if control.mode == control.AUTO:
        base_mode |= MAV_MODE_FLAG_AUTO_ENABLED
    
    payload = struct.pack('<IBBBBB', 
        0, MAV_TYPE_QUADROTOR, MAV_AUTOPILOT_GENERIC, 
        base_mode, control.mode, MAV_STATE_STANDBY)
    
    _send_message(MAVLINK_MSG_ID_HEARTBEAT, payload)

def _send_extended_sys_state() -> None:
    import main
    from lib.estimate import landed
    
    payload = struct.pack('<BB', MAV_VTOL_STATE_UNDEFINED, 
        MAV_LANDED_STATE_ON_GROUND if landed else MAV_LANDED_STATE_IN_AIR)
    
    _send_message(MAVLINK_MSG_ID_EXTENDED_SYS_STATE, payload)

def _send_attitude_quaternion() -> None:
    import main
    from lib.estimate import attitude, rates
    
    time_ms = int(main.t * 1000)
    payload = struct.pack('<Ifffffff', time_ms,
        attitude.w, attitude.x, -attitude.y, -attitude.z,
        rates.x, -rates.y, -rates.z, 0, 0, 0, 0)
    
    _send_message(MAVLINK_MSG_ID_ATTITUDE_QUATERNION, payload)

def _send_rc_channels_raw() -> None:
    import main
    from lib import rc
    
    if rc.channels[0] == 0:
        return
    
    time_ms = int(main.control_time * 1000)
    payload = struct.pack('<IHHHHHHHHB', time_ms, 0,
        rc.channels[0], rc.channels[1], rc.channels[2], rc.channels[3],
        rc.channels[4], rc.channels[5], rc.channels[6], rc.channels[7], 255)
    
    _send_message(MAVLINK_MSG_ID_RC_CHANNELS_RAW, payload)

def _send_actuator_control_target() -> None:
    import main
    
    time_ms = int(main.t * 1000)
    payload = struct.pack('<IBffffffff', time_ms, 0,
        main.motors[0], main.motors[1], main.motors[2], main.motors[3],
        0, 0, 0, 0)
    
    _send_message(MAVLINK_MSG_ID_ACTUATOR_CONTROL_TARGET, payload)

def _send_scaled_imu() -> None:
    import main
    
    time_ms = int(main.t * 1000)
    payload = struct.pack('<Ihhhhhhhhh', time_ms,
        int(main.acc.x * 1000), int(-main.acc.y * 1000), int(-main.acc.z * 1000),
        int(main.gyro.x * 1000), int(-main.gyro.y * 1000), int(-main.gyro.z * 1000),
        0, 0, 0, 0)
    
    _send_message(MAVLINK_MSG_ID_SCALED_IMU, payload)

def _send_serial_control(text: str) -> None:
    data = text.encode('utf-8')
    offset = 0
    while offset < len(data):
        chunk = data[offset:offset+70]
        payload = struct.pack('<BBBBB', SERIAL_CONTROL_DEV_SHELL,
            0 if offset + 70 >= len(data) else 2, 0, 0, len(chunk))
        payload += chunk + b'\x00' * (70 - len(chunk))
        _send_message(MAVLINK_MSG_ID_SERIAL_CONTROL, payload)
        offset += 70

def _send_message(msg_id: int, payload: bytes) -> None:
    global _seq
    
    from lib import wifi
    
    header = bytes([MAVLINK_STX, len(payload), 0, _seq, mavlink_sys_id, MAV_COMP_ID_AUTOPILOT1, msg_id, 0])
    _seq = (_seq + 1) & 0xFF
    
    crc = _crc16(header[1:] + payload)
    crc = _crc_accumulate(msg_id, crc)
    
    packet = header + payload + struct.pack('<H', crc)
    wifi.send(packet)

def _receive() -> None:
    global mavlink_connected
    
    from lib import wifi
    
    n = wifi.receive(_rx_buffer, 280)
    if n > 0:
        mavlink_connected = True
        _parse(_rx_buffer[:n])

def _parse(data: bytes) -> None:
    i = 0
    while i < len(data):
        if data[i] == MAVLINK_STX:
            if i + 12 > len(data):
                break
            
            msg_len = data[i+1]
            if i + 12 + msg_len > len(data):
                break
            
            msg_id = data[i+7]
            payload = data[i+12:i+12+msg_len]
            
            _handle_message(msg_id, payload)
            i += 12 + msg_len
        else:
            i += 1

def _handle_message(msg_id: int, payload: bytes) -> None:
    if msg_id == MAVLINK_MSG_ID_MANUAL_CONTROL:
        _handle_manual_control(payload)
    elif msg_id == MAVLINK_MSG_ID_PARAM_REQUEST_LIST:
        _handle_param_request_list(payload)
    elif msg_id == MAVLINK_MSG_ID_PARAM_REQUEST_READ:
        _handle_param_request_read(payload)
    elif msg_id == MAVLINK_MSG_ID_PARAM_SET:
        _handle_param_set(payload)
    elif msg_id == MAVLINK_MSG_ID_COMMAND_LONG:
        _handle_command_long(payload)
    elif msg_id == MAVLINK_MSG_ID_SET_ATTITUDE_TARGET:
        _handle_set_attitude_target(payload)
    elif msg_id == MAVLINK_MSG_ID_SET_ACTUATOR_CONTROL_TARGET:
        _handle_set_actuator_control_target(payload)
    elif msg_id == MAVLINK_MSG_ID_SERIAL_CONTROL:
        _handle_serial_control(payload)

def _handle_manual_control(payload: bytes) -> None:
    import main
    
    target, x, y, z, r, buttons = struct.unpack('<HHHHHH', payload[:12])
    
    if target != 0 and target != mavlink_sys_id:
        return
    
    main.control_throttle = z / 1000.0
    main.control_pitch = x / 1000.0
    main.control_roll = y / 1000.0
    main.control_yaw = r / 1000.0
    main.control_mode = float('nan')
    main.control_time = main.t

def _handle_param_request_list(payload: bytes) -> None:
    from lib import parameters
    
    target_system, target_component = struct.unpack('<BB', payload[:2])
    if target_system != 0 and target_system != mavlink_sys_id:
        return
    
    for i, name in enumerate(parameters.get_names()):
        value = parameters.get(name)
        _send_param_value(name, value, i)

def _handle_param_request_read(payload: bytes) -> None:
    from lib import parameters
    
    target_system, target_component, param_index = struct.unpack('<BBh', payload[:4])
    param_id = payload[4:20].rstrip(b'\x00').decode('utf-8')
    
    if target_system != 0 and target_system != mavlink_sys_id:
        return
    
    if param_index >= 0:
        names = parameters.get_names()
        if param_index < len(names):
            name = names[param_index]
            value = parameters.get(name)
        else:
            return
    else:
        value = parameters.get(param_id)
        name = param_id
    
    _send_param_value(name, value, param_index if param_index >= 0 else -1)

def _handle_param_set(payload: bytes) -> None:
    from lib import parameters
    
    target_system, target_component = struct.unpack('<BB', payload[:2])
    param_id = payload[2:18].rstrip(b'\x00').decode('utf-8')
    param_value = struct.unpack('<f', payload[18:22])[0]
    
    if target_system != 0 and target_system != mavlink_sys_id:
        return
    
    if parameters.set(param_id, param_value):
        value = parameters.get(param_id)
        _send_param_value(param_id, value, -1)

def _send_param_value(name: str, value: float, index: int) -> None:
    from lib import parameters
    
    name_bytes = name.encode('utf-8')[:16].ljust(16, b'\x00')
    payload = name_bytes + struct.pack('<ffi', value, 9, parameters.count(), index)
    _send_message(MAVLINK_MSG_ID_PARAM_VALUE, payload)

def _handle_command_long(payload: bytes) -> None:
    target_system, target_component, command = struct.unpack('<BBH', payload[:4])
    params = struct.unpack('<fffff', payload[4:24])
    
    if target_system != 0 and target_system != mavlink_sys_id:
        return
    
    import main
    from lib import control
    
    accepted = False
    
    if command == MAV_CMD_REQUEST_MESSAGE and params[0] == MAVLINK_MSG_ID_AUTOPILOT_VERSION:
        accepted = True
        _send_autopilot_version()
    
    elif command == MAV_CMD_COMPONENT_ARM_DISARM:
        if params[0] == 1 and main.control_throttle > 0.05:
            accepted = False
        else:
            accepted = True
            control.armed = params[0] == 1
    
    elif command == MAV_CMD_DO_SET_MODE:
        mode = int(params[1])
        if mode < 0 or mode > control.AUTO:
            accepted = False
        else:
            accepted = True
            control.mode = mode
    
    _send_command_ack(command, MAV_RESULT_ACCEPTED if accepted else MAV_RESULT_UNSUPPORTED)

def _send_autopilot_version() -> None:
    payload = struct.pack('<IIIIIIIIQQ', 
        0x03, 1, 0, 1, 1, 0, 0, 0, 0, 0)
    _send_message(MAVLINK_MSG_ID_AUTOPILOT_VERSION, payload)

def _send_command_ack(command: int, result: int) -> None:
    payload = struct.pack('<HHBBB', command, result, 0, 0, 0)
    _send_message(MAVLINK_MSG_ID_COMMAND_ACK, payload)

def _handle_set_attitude_target(payload: bytes) -> None:
    from lib import control
    from lib.quaternion import Quaternion
    from lib.vector import Vector
    
    if control.mode != control.AUTO:
        return
    
    target_system, target_component, type_mask = struct.unpack('<BBB', payload[:3])
    q = struct.unpack('<ffff', payload[3:19])
    body_roll_rate, body_pitch_rate, body_yaw_rate, thrust = struct.unpack('<fff', payload[19:31])
    
    if target_system != 0 and target_system != mavlink_sys_id:
        return
    
    control.rates_target.x = body_roll_rate
    control.rates_target.y = -body_pitch_rate
    control.rates_target.z = -body_yaw_rate
    
    control.attitude_target.w = q[0]
    control.attitude_target.x = q[1]
    control.attitude_target.y = -q[2]
    control.attitude_target.z = -q[3]
    
    control.thrust_target = thrust
    control.rates_extra.x = 0
    control.rates_extra.y = 0
    control.rates_extra.z = 0
    
    if type_mask & 0x01:
        control.attitude_target.invalidate()
    
    control.armed = thrust > 0

def _handle_set_actuator_control_target(payload: bytes) -> None:
    from lib import control
    from lib.motors import motors
    import main
    
    if control.mode != control.AUTO:
        return
    
    target_system, target_component = struct.unpack('<BB', payload[:2])
    controls = struct.unpack('<ffffffff', payload[6:38])
    
    if target_system != 0 and target_system != mavlink_sys_id:
        return
    
    for i in range(4):
        motors[i] = controls[i]
        main.motors[i] = controls[i]
    
    control.armed = any(m > 0 for m in motors)

def _handle_serial_control(payload: bytes) -> None:
    device, flags, timeout, baudrate, count = struct.unpack('<BBBBB', payload[:5])
    data = payload[5:75][:count].rstrip(b'\x00').decode('utf-8')
    
    from lib import cli
    cli.do_command(data, echo=True)

def mavlink_print(text: str) -> None:
    global _print_buffer
    _print_buffer += text

CRC_INIT = 0xFFFF
CRC_TABLE = [
    0x0000, 0x1021, 0x2042, 0x3063, 0x4084, 0x50A5, 0x60C6, 0x70E7,
    0x8108, 0x9129, 0xA14A, 0xB16B, 0xC18C, 0xD1AD, 0xE1CE, 0xF1EF
]

def _crc16(data: bytes) -> int:
    crc = CRC_INIT
    for b in data:
        crc = ((crc << 4) & 0xFFFF) ^ CRC_TABLE[((crc >> 12) ^ (b >> 4)) & 0x0F]
        crc = ((crc << 4) & 0xFFFF) ^ CRC_TABLE[((crc >> 12) ^ b) & 0x0F]
    return crc

def _crc_accumulate(msg_id: int, crc: int) -> int:
    return crc ^ (msg_id << 8) ^ (msg_id >> 8)
