"""
RC 接收机模块

支持 SBUS 协议的 RC 接收机，通过 UART 接口通信。

SBUS 协议:
- 波特率: 100000 bps
- 数据位: 8 位
- 校验位: 偶校验
- 停止位: 2 位
- 帧长度: 25 字节
- 通道数: 16 个 (11 位分辨率)

通道映射:
- roll_channel: 横滚控制通道
- pitch_channel: 俯仰控制通道
- yaw_channel: 偏航控制通道
- throttle_channel: 油门控制通道
- mode_channel: 模式切换通道

使用示例:
    from lib import rc
    
    # 初始化
    rc.setup()
    
    # 读取数据
    if rc.read():
        print(f"Roll: {rc.channels[0]}")
    
    # 校准
    rc.calibrate()
"""

import struct
from typing import List, Tuple
from machine import UART, Pin
from lib.util import mapf

SBUS_HEADER = 0x0F
SBUS_FOOTER = 0x00

channels: List[int] = [0] * 16
channel_zero: List[int] = [0] * 16
channel_max: List[int] = [0] * 16

roll_channel = -1
pitch_channel = -1
throttle_channel = -1
yaw_channel = -1
mode_channel = -1

_uart = None

def setup() -> None:
    global _uart
    print("Setup RC")
    _uart = UART(2, baudrate=100000, bits=8, parity=0, stop=2, rx=16, tx=17)

def read() -> bool:
    import main
    
    if _uart is None:
        return False
    
    if _uart.any() >= 25:
        data = _uart.read(25)
        if data and len(data) == 25:
            if data[0] == SBUS_HEADER and data[24] == SBUS_FOOTER:
                _parse_channels(data)
                _normalize()
                main.control_time = main.t
                return True
    
    return False

def _parse_channels(data: bytes) -> None:
    global channels
    
    channels[0] = (data[1] | data[2] << 8) & 0x07FF
    channels[1] = (data[2] >> 3 | data[3] << 5) & 0x07FF
    channels[2] = (data[3] >> 6 | data[4] << 2 | data[5] << 10) & 0x07FF
    channels[3] = (data[5] >> 1 | data[6] << 7) & 0x07FF
    channels[4] = (data[6] >> 4 | data[7] << 4) & 0x07FF
    channels[5] = (data[7] >> 7 | data[8] << 1 | data[9] << 9) & 0x07FF
    channels[6] = (data[9] >> 2 | data[10] << 6) & 0x07FF
    channels[7] = (data[10] >> 5 | data[11] << 3) & 0x07FF
    channels[8] = (data[12] | data[13] << 8) & 0x07FF
    channels[9] = (data[13] >> 3 | data[14] << 5) & 0x07FF
    channels[10] = (data[14] >> 6 | data[15] << 2 | data[16] << 10) & 0x07FF
    channels[11] = (data[16] >> 1 | data[17] << 7) & 0x07FF
    channels[12] = (data[17] >> 4 | data[18] << 4) & 0x07FF
    channels[13] = (data[18] >> 7 | data[19] << 1 | data[20] << 9) & 0x07FF
    channels[14] = (data[20] >> 2 | data[21] << 6) & 0x07FF
    channels[15] = (data[21] >> 5 | data[22] << 3) & 0x07FF

def _normalize() -> None:
    import main
    
    controls = [0.0] * 16
    for i in range(16):
        if channel_zero[i] != channel_max[i]:
            controls[i] = mapf(channels[i], channel_zero[i], channel_max[i], 0, 1)
        else:
            controls[i] = 0.5
    
    main.control_roll = controls[roll_channel] if roll_channel >= 0 else 0.0
    main.control_pitch = controls[pitch_channel] if pitch_channel >= 0 else 0.0
    main.control_yaw = controls[yaw_channel] if yaw_channel >= 0 else 0.0
    main.control_throttle = controls[throttle_channel] if throttle_channel >= 0 else 0.0
    main.control_mode = controls[mode_channel] if mode_channel >= 0 else float('nan')

def calibrate() -> None:
    print("1/8 Calibrating RC: put all switches to default positions [3 sec]")
    _pause(3)
    
    zero = _read_channels_avg()
    
    print("2/8 Move sticks [3 sec]")
    _pause(3)
    center = _read_channels_avg()
    
    print("3/8 Move sticks [3 sec]")
    _pause(3)
    
    print("4/8 Move sticks [3 sec]")
    _pause(3)
    max_vals = _read_channels_avg()
    
    _calibrate_channel('roll', zero, max_vals)
    _calibrate_channel('yaw', center, max_vals)
    _calibrate_channel('pitch', zero, max_vals)
    _calibrate_channel('throttle', zero, max_vals)
    
    print("8/8 Put mode switch to max [3 sec]")
    _pause(3)
    mode_max = _read_channels_avg()
    _calibrate_channel('mode', zero, mode_max)
    
    print_calibration()

def _read_channels_avg() -> List[float]:
    global channels
    avg = [0.0] * 16
    for _ in range(30):
        read()
        for i in range(16):
            avg[i] += channels[i]
    return [v / 30 for v in avg]

def _calibrate_channel(name: str, before: List[float], after: List[float]) -> None:
    global roll_channel, pitch_channel, throttle_channel, yaw_channel, mode_channel
    global channel_zero, channel_max
    
    ch = -1
    max_diff = 0
    for i in range(16):
        diff = abs(after[i] - before[i])
        if diff > max_diff:
            max_diff = diff
            ch = i
    
    if ch >= 0 and max_diff > 10:
        if name == 'roll':
            roll_channel = ch
        elif name == 'pitch':
            pitch_channel = ch
        elif name == 'throttle':
            throttle_channel = ch
        elif name == 'yaw':
            yaw_channel = ch
        elif name == 'mode':
            mode_channel = ch
        
        channel_zero[ch] = int(before[ch])
        channel_max[ch] = int(after[ch])

def _pause(duration: float) -> None:
    import time
    start = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), start) < duration * 1000:
        time.sleep_ms(50)

def print_calibration() -> None:
    print("Control   Ch     Zero   Max")
    print(f"Roll      {roll_channel:7d}{channel_zero[roll_channel] if roll_channel >= 0 else 0:7d}{channel_max[roll_channel] if roll_channel >= 0 else 0:7d}")
    print(f"Pitch     {pitch_channel:7d}{channel_zero[pitch_channel] if pitch_channel >= 0 else 0:7d}{channel_max[pitch_channel] if pitch_channel >= 0 else 0:7d}")
    print(f"Yaw       {yaw_channel:7d}{channel_zero[yaw_channel] if yaw_channel >= 0 else 0:7d}{channel_max[yaw_channel] if yaw_channel >= 0 else 0:7d}")
    print(f"Throttle  {throttle_channel:7d}{channel_zero[throttle_channel] if throttle_channel >= 0 else 0:7d}{channel_max[throttle_channel] if throttle_channel >= 0 else 0:7d}")
    print(f"Mode      {mode_channel:7d}{channel_zero[mode_channel] if mode_channel >= 0 else 0:7d}{channel_max[mode_channel] if mode_channel >= 0 else 0:7d}")
