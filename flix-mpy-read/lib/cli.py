"""
命令行界面模块

提供交互式命令行界面，用于调试和配置。

支持命令:
- help: 显示帮助信息
- arm: 解锁
- disarm: 上锁
- status: 显示系统状态
- param: 参数管理
    - param list: 列出所有参数
    - param get <name>: 获取参数值
    - param set <name> <value>: 设置参数值
    - param save: 保存参数到文件
    - param reset: 重置为默认值
- calibrate: 校准
    - calibrate gyro: 陀螺仪校准
    - calibrate accel: 加速度计校准
- motor: 电机测试
    - motor test <index> <value>: 测试单个电机
    - motor stop: 停止所有电机
- log: 日志管理
    - log start: 开始记录
    - log stop: 停止记录
    - log print: 打印日志数据

使用示例:
    在 REPL 中输入命令:
    >>> param list
    >>> param set CTL_R_P 0.5
    >>> arm
"""

import sys
from typing import List, Optional
from lib.util import Rate

MOTD = """
Welcome to
 _______  __       __  ___   ___
|   ____||  |     |  | \\  \\ /  /
|  |__   |  |     |  |  \\  V  /
|   __|  |  |     |  |   >   <
|  |     |  `----.|  |  /  .  \\
|__|     |_______||__| /__/ \\__\\

Commands:

help - show help
p - show all parameters
p <name> - show parameter
p <name> <value> - set parameter
preset - reset parameters
time - show time info
ps - show pitch/roll/yaw
psq - show attitude quaternion
imu - show IMU data
arm - arm the drone
disarm - disarm the drone
raw/stab/acro/auto - set mode
rc - show RC data
wifi - show Wi-Fi info
ap <ssid> <password> - setup Wi-Fi access point
sta <ssid> <password> - setup Wi-Fi client mode
mot - show motor output
log [dump] - print log header [and data]
cr - calibrate RC
ca - calibrate accel
mfr, mfl, mrr, mrl - test motor (remove props)
sys - show system info
reset - reset drone's state
reboot - reboot the drone
"""

_show_motd = True
_input_buffer = ""

def handle_input() -> None:
    global _show_motd, _input_buffer
    
    if _show_motd:
        print(MOTD)
        _show_motd = False
    
    try:
        from machine import UART
        uart = UART(0)
        while uart.any():
            c = uart.read(1)
            if c:
                c = c.decode('utf-8', errors='ignore')
                if c == '\n':
                    do_command(_input_buffer)
                    _input_buffer = ""
                else:
                    _input_buffer += c
    except:
        pass

def do_command(cmd_str: str, echo: bool = False) -> None:
    parts = cmd_str.strip().split()
    if not parts:
        return
    
    cmd = parts[0].lower()
    args = parts[1:] if len(parts) > 1 else []
    
    if echo:
        print(f"> {cmd_str}")
    
    import main
    from lib import control, estimate
    
    if cmd == "help" or cmd == "motd":
        print(MOTD)
    
    elif cmd == "p":
        from lib import parameters
        if not args:
            parameters.print_all()
        elif len(args) == 1:
            val = parameters.get(args[0])
            print(f"{args[0]} = {val}")
        else:
            if parameters.set(args[0], float(args[1])):
                val = parameters.get(args[0])
                print(f"{args[0]} = {val}")
            else:
                print(f"Parameter not found: {args[0]}")
    
    elif cmd == "preset":
        from lib import parameters
        parameters.reset()
    
    elif cmd == "time":
        print(f"Time: {main.t}")
        print(f"Loop rate: {main.loop_rate}")
        print(f"dt: {main.dt}")
    
    elif cmd == "ps":
        euler = main.attitude.to_euler()
        print(f"roll: {degrees(euler.x)} pitch: {degrees(euler.y)} yaw: {degrees(euler.z)}")
    
    elif cmd == "psq":
        print(f"qw: {main.attitude.w} qx: {main.attitude.x} qy: {main.attitude.y} qz: {main.attitude.z}")
    
    elif cmd == "imu":
        from lib import imu
        print(f"gyro: {main.gyro.x} {main.gyro.y} {main.gyro.z}")
        print(f"acc: {main.acc.x} {main.acc.y} {main.acc.z}")
        print(f"rates: {estimate.rates.x} {estimate.rates.y} {estimate.rates.z}")
        imu.print_calibration()
        print(f"landed: {main.landed}")
    
    elif cmd == "arm":
        control.armed = True
    
    elif cmd == "disarm":
        control.armed = False
    
    elif cmd == "raw":
        control.mode = control.RAW
    
    elif cmd == "stab":
        control.mode = control.STAB
    
    elif cmd == "acro":
        control.mode = control.ACRO
    
    elif cmd == "auto":
        control.mode = control.AUTO
    
    elif cmd == "rc":
        from lib import rc
        print(f"channels: {' '.join(str(c) for c in rc.channels)}")
        print(f"roll: {main.control_roll} pitch: {main.control_pitch} yaw: {main.control_yaw} throttle: {main.control_throttle} mode: {main.control_mode}")
        print(f"time: {main.control_time}")
        print(f"mode: {control.get_mode_name()}")
        print(f"armed: {control.armed}")
    
    elif cmd == "wifi":
        from lib import wifi
        wifi.print_info()
    
    elif cmd == "ap":
        if len(args) >= 2:
            from lib import wifi
            wifi.config(True, args[0], args[1])
    
    elif cmd == "sta":
        if len(args) >= 2:
            from lib import wifi
            wifi.config(False, args[0], args[1])
    
    elif cmd == "mot":
        from lib.motors import motors, MOTOR_FRONT_RIGHT, MOTOR_FRONT_LEFT, MOTOR_REAR_RIGHT, MOTOR_REAR_LEFT
        print(f"front-right {motors[MOTOR_FRONT_RIGHT]} front-left {motors[MOTOR_FRONT_LEFT]} rear-right {motors[MOTOR_REAR_RIGHT]} rear-left {motors[MOTOR_REAR_LEFT]}")
    
    elif cmd == "log":
        from lib import log
        log.print_header()
        if args and args[0] == "dump":
            log.print_data()
    
    elif cmd == "cr":
        from lib import rc
        rc.calibrate()
    
    elif cmd == "ca":
        from lib import imu
        imu.calibrate_accel()
    
    elif cmd == "mfr":
        from lib.motors import test_motor, MOTOR_FRONT_RIGHT
        test_motor(MOTOR_FRONT_RIGHT)
    
    elif cmd == "mfl":
        from lib.motors import test_motor, MOTOR_FRONT_LEFT
        test_motor(MOTOR_FRONT_LEFT)
    
    elif cmd == "mrr":
        from lib.motors import test_motor, MOTOR_REAR_RIGHT
        test_motor(MOTOR_REAR_RIGHT)
    
    elif cmd == "mrl":
        from lib.motors import test_motor, MOTOR_REAR_LEFT
        test_motor(MOTOR_REAR_LEFT)
    
    elif cmd == "sys":
        import gc
        import sys
        print(f"Platform: {sys.platform}")
        print(f"Free heap: {gc.mem_free()}")
        print(f"Allocated: {gc.mem_alloc()}")
    
    elif cmd == "reset":
        main.attitude.w, main.attitude.x, main.attitude.y, main.attitude.z = 1, 0, 0, 0
        from lib.imu import gyro_bias_filter
        gyro_bias_filter.reset()
    
    elif cmd == "reboot":
        import machine
        machine.reset()
    
    else:
        print(f"Invalid command: {cmd}")

def pause(duration: float) -> None:
    import time
    start = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), start) < duration * 1000:
        time.sleep_ms(50)
