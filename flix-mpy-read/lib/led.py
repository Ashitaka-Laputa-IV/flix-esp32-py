"""
LED 指示灯模块

控制 ESP32 内置 LED 用于状态指示。

状态指示:
- 初始化中: 常亮
- 正常运行: 闪烁 (0.5Hz)
- 错误状态: 快速闪烁

使用示例:
    from lib import led
    
    # 初始化
    led.setup()
    
    # 设置状态
    led.set_led(True)   # 点亮
    led.set_led(False)  # 熄灭
    
    # 闪烁 (在主循环中调用)
    led.blink()
"""

from machine import Pin
import time

LED_BUILTIN = 2
_state = False
_pin = None

def setup() -> None:
    global _pin
    _pin = Pin(LED_BUILTIN, Pin.OUT)
    _pin.value(0)

def set_led(on: bool) -> None:
    global _state
    if on == _state:
        return
    _pin.value(1 if on else 0)
    _state = on

def blink() -> None:
    us = time.ticks_us()
    set_led((us // 500000) % 2 == 0)
