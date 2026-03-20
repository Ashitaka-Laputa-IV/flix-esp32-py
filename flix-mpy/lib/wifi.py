"""
Wi-Fi 通信模块

提供 Wi-Fi 网络连接和 UDP 通信功能。

工作模式:
- STATION: 连接到现有 Wi-Fi 网络
- AP: 创建热点供其他设备连接

功能:
- 自动连接/创建热点
- UDP 数据收发
- 遥测数据广播
- 连接状态监控

使用示例:
    from lib import wifi
    
    # 初始化 (根据参数配置)
    wifi.setup()
    
    # 发送数据
    wifi.send(remote_ip, remote_port, data)
    
    # 接收数据
    data, addr = wifi.receive()
"""

import network
import socket
import struct
import time
from lib.util import Rate

W_DISABLED = 0
W_AP = 1
W_STA = 2

wifi_mode = W_AP
udp_local_port = 14550
udp_remote_port = 14550
udp_remote_ip = "255.255.255.255"

_ap_ssid = "flix"
_ap_password = "flixwifi"
_sta_ssid = ""
_sta_password = ""

_wlan = None
_socket = None
telemetry_slow = None
telemetry_fast = None

def setup():
    global _wlan, _socket, telemetry_slow, telemetry_fast
    
    print("Setup Wi-Fi")
    
    telemetry_slow = Rate(2)
    telemetry_fast = Rate(10)
    
    if wifi_mode == W_AP:
        _wlan = network.WLAN(network.AP_IF)
        _wlan.config(essid=_ap_ssid, password=_ap_password)
        _wlan.active(True)
    elif wifi_mode == W_STA:
        _wlan = network.WLAN(network.STA_IF)
        _wlan.active(True)
        _wlan.connect(_sta_ssid, _sta_password)
    else:
        _wlan = None
        return
    
    _socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    _socket.setblocking(False)
    _socket.bind(('0.0.0.0', udp_local_port))

def send(buf):
    if _socket is None:
        return
    try:
        _socket.sendto(buf, (udp_remote_ip, udp_remote_port))
    except:
        pass

def receive(buf, length):
    if _socket is None:
        return 0
    try:
        data, addr = _socket.recvfrom(length)
        global udp_remote_ip
        udp_remote_ip = addr[0]
        n = min(len(data), length)
        buf[:n] = data[:n]
        return n
    except:
        return 0

def connected():
    if _wlan is None:
        return False
    if wifi_mode == W_AP:
        return True
    return _wlan.isconnected()

def get_ip():
    if _wlan is None:
        return "0.0.0.0"
    if wifi_mode == W_AP:
        return _wlan.ifconfig()[0]
    elif _wlan.isconnected():
        return _wlan.ifconfig()[0]
    return "0.0.0.0"

def print_info():
    if _wlan is None:
        print("Mode: Disabled")
        return
    
    if wifi_mode == W_AP:
        print("Mode: Access Point (AP)")
        print(f"SSID: {_ap_ssid}")
        print(f"IP: {get_ip()}")
    else:
        print("Mode: Client (STA)")
        print(f"Connected: {_wlan.isconnected()}")
        if _wlan.isconnected():
            print(f"SSID: {_sta_ssid}")
            print(f"IP: {get_ip()}")
    
    print(f"Remote IP: {udp_remote_ip}")

def config(ap, ssid, password):
    global _ap_ssid, _ap_password, _sta_ssid, _sta_password, wifi_mode
    
    if ap:
        _ap_ssid = ssid
        _ap_password = password
        wifi_mode = W_AP
    else:
        _sta_ssid = ssid
        _sta_password = password
        wifi_mode = W_STA
    
    print("Reboot to apply new settings")
