"""
IMU 传感器驱动模块

支持 MPU9250 九轴传感器，通过 I2C 接口通信。

功能:
- 读取三轴加速度计和陀螺仪数据
- 传感器校准 (零偏和比例因子)
- 自动陀螺仪零偏估计
- IMU 安装方向旋转

寄存器配置:
- 加速度计量程: ±4G
- 陀螺仪量程: ±2000 DPS
- 数字低通滤波器: 最大带宽

使用示例:
    from lib import imu
    
    # 初始化
    imu.setup()
    
    # 读取数据
    imu.read()
    print(f"Accel: {imu.acc.x}, {imu.acc.y}, {imu.acc.z}")
    print(f"Gyro: {imu.gyro.x}, {imu.gyro.y}, {imu.gyro.z}")
    
    # 校准加速度计
    imu.calibrate_accel()
"""

import math
from machine import Pin, I2C
from lib.vector import Vector
from lib.quaternion import Quaternion
from lib.lpf import LowPassFilter
from lib.util import ONE_G

MPU9250_ADDR = 0x68

PWR_MGMT_1 = 0x6B
GYRO_CONFIG = 0x1B
ACCEL_CONFIG = 0x1C
ACCEL_CONFIG2 = 0x1D
CONFIG = 0x1A
SMPLRT_DIV = 0x19

ACCEL_XOUT_H = 0x3B
GYRO_XOUT_H = 0x43

WHO_AM_I = 0x75

ACCEL_RANGE_2G = 0
ACCEL_RANGE_4G = 1
ACCEL_RANGE_8G = 2
ACCEL_RANGE_16G = 3

GYRO_RANGE_250DPS = 0
GYRO_RANGE_500DPS = 1
GYRO_RANGE_1000DPS = 2
GYRO_RANGE_2000DPS = 3

DLPF_MAX = 7

gyro = Vector()
acc = Vector()
gyro_bias = Vector()
acc_bias = Vector()
acc_scale = Vector(1, 1, 1)

imu_rotation = Vector(0, 0, -math.pi / 2)
gyro_bias_filter = LowPassFilter(0.001)

_i2c = None
_accel_range = ACCEL_RANGE_4G
_gyro_range = GYRO_RANGE_2000DPS
_accel_scale = 8192.0
_gyro_scale = 16.4

_landed_delay_start = float('nan')

def setup():
    global _i2c, _accel_scale, _gyro_scale
    print("Setup IMU")
    
    try:
        _i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
        
        who = _read_byte(WHO_AM_I)
        if who != 0x71:
            print(f"MPU9250 not found, WHO_AM_I: 0x{who:02X}")
            return
        
        _write_byte(PWR_MGMT_1, 0x80)
        import time
        time.sleep_ms(100)
        
        _write_byte(PWR_MGMT_1, 0x01)
        _write_byte(PWR_MGMT_2, 0x00)
        
        configure()
        
        print("IMU initialized")
        
    except Exception as e:
        print(f"IMU setup error: {e}")

def configure():
    global _accel_scale, _gyro_scale
    
    _write_byte(ACCEL_CONFIG, _accel_range << 3)
    _write_byte(GYRO_CONFIG, _gyro_range << 3)
    _write_byte(CONFIG, DLPF_MAX)
    _write_byte(ACCEL_CONFIG2, DLPF_MAX)
    _write_byte(SMPLRT_DIV, 0)
    
    accel_scales = [16384.0, 8192.0, 4096.0, 2048.0]
    gyro_scales = [131.0, 65.5, 32.8, 16.4]
    _accel_scale = accel_scales[_accel_range]
    _gyro_scale = gyro_scales[_gyro_range]

def read():
    global gyro, acc, _landed_delay_start
    
    if _i2c is None:
        return
    
    import main
    
    data = _read_bytes(ACCEL_XOUT_H, 14)
    
    ax = _to_int16(data[0], data[1])
    ay = _to_int16(data[2], data[3])
    az = _to_int16(data[4], data[5])
    
    gx = _to_int16(data[8], data[9])
    gy = _to_int16(data[10], data[11])
    gz = _to_int16(data[12], data[13])
    
    acc_raw = Vector(ax / _accel_scale, ay / _accel_scale, az / _accel_scale)
    gyro_raw = Vector(gx / _gyro_scale, gy / _gyro_scale, gz / _gyro_scale)
    gyro_raw = gyro_raw * (math.pi / 180.0)
    
    acc_val = (acc_raw - acc_bias) / acc_scale
    gyro_val = gyro_raw - gyro_bias
    
    rotation = Quaternion.from_euler(imu_rotation)
    acc_val = Quaternion.rotate_vector(acc_val, rotation.inversed())
    gyro_val = Quaternion.rotate_vector(gyro_val, rotation.inversed())
    
    main.acc.x, main.acc.y, main.acc.z = acc_val.x, acc_val.y, acc_val.z
    main.gyro.x, main.gyro.y, main.gyro.z = gyro_val.x, gyro_val.y, gyro_val.z
    
    acc.x, acc.y, acc.z = acc_val.x, acc_val.y, acc_val.z
    gyro.x, gyro.y, gyro.z = gyro_val.x, gyro_val.y, gyro_val.z
    
    _calibrate_gyro_once()

def _calibrate_gyro_once():
    global gyro_bias, _landed_delay_start
    
    import main
    
    if not main.landed:
        _landed_delay_start = float('nan')
        return
    
    if math.isnan(_landed_delay_start):
        _landed_delay_start = main.t
    
    if main.t - _landed_delay_start >= 2.0:
        gyro_bias = gyro_bias_filter.update(gyro)

def calibrate_accel():
    print("Calibrating accelerometer")
    
    acc_max = Vector(-float('inf'), -float('inf'), -float('inf'))
    acc_min = Vector(float('inf'), float('inf'), float('inf'))
    
    positions = [
        "1/6 Place level [8 sec]",
        "2/6 Place nose up [8 sec]",
        "3/6 Place nose down [8 sec]",
        "4/6 Place on right side [8 sec]",
        "5/6 Place on left side [8 sec]",
        "6/6 Place upside down [8 sec]"
    ]
    
    for pos in positions:
        print(pos)
        import time
        time.sleep(8)
        
        samples = Vector()
        for _ in range(1000):
            read()
            samples += acc
        samples = samples / 1000
        
        acc_max.x = max(acc_max.x, samples.x)
        acc_max.y = max(acc_max.y, samples.y)
        acc_max.z = max(acc_max.z, samples.z)
        acc_min.x = min(acc_min.x, samples.x)
        acc_min.y = min(acc_min.y, samples.y)
        acc_min.z = min(acc_min.z, samples.z)
    
    global acc_scale, acc_bias
    acc_scale = (acc_max - acc_min) / 2 / ONE_G
    acc_bias = (acc_max + acc_min) / 2
    
    print_calibration()

def print_calibration():
    print(f"gyro bias: {gyro_bias.x} {gyro_bias.y} {gyro_bias.z}")
    print(f"accel bias: {acc_bias.x} {acc_bias.y} {acc_bias.z}")
    print(f"accel scale: {acc_scale.x} {acc_scale.y} {acc_scale.z}")

def _read_byte(reg):
    return _i2c.readfrom_mem(MPU9250_ADDR, reg, 1)[0]

def _read_bytes(reg, length):
    return _i2c.readfrom_mem(MPU9250_ADDR, reg, length)

def _write_byte(reg, value):
    _i2c.writeto_mem(MPU9250_ADDR, reg, bytes([value]))

def _to_int16(high, low):
    value = (high << 8) | low
    if value >= 0x8000:
        value -= 0x10000
    return value
