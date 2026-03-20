<!-- markdownlint-disable MD041 -->

<p align="center">
  <img src="docs/img/flix.svg" width=180 alt="Flix logo"><br>
  <b>Flix</b> (<i>flight + X</i>) — 开源 ESP32 四旋翼飞行器，从零开始制作。
</p>

<table>
  <tr>
    <td align=center><strong>版本 1.1</strong> (3D 打印机架)</td>
    <td align=center><strong>版本 0</strong></td>
  </tr>
  <tr>
    <td><img src="docs/img/flix1.1.jpg" width=500 alt="Flix 四旋翼飞行器"></td>
    <td><img src="docs/img/flix.jpg" width=500 alt="Flix 四旋翼飞行器"></td>
  </tr>
</table>

## 特性

* 专为教育和研究而设计。
* 使用通用组件制作。
* 简洁清晰的 Arduino 源代码（固件 <2k 行）。
* 使用 Wi-Fi 和 MAVLink 协议进行连接。
* 使用 USB 游戏手柄、遥控器或智能手机进行控制。
* 无线命令行界面和分析功能。
* 使用 Gazebo 进行精确仿真。
* 用于脚本编写和自动飞行的 Python 库。
* 飞行控制理论与实践教材（[开发中](https://quadcopter.dev)）。
* *位置控制（计划中）*。

## 它真的能飞

查看详细演示视频：https://youtu.be/hT46CZ1CgC4。

<a href="https://youtu.be/hT46CZ1CgC4"><img width=500 src="https://i3.ytimg.com/vi/hT46CZ1CgC4/maxresdefault.jpg"></a>

版本 0 演示视频：https://youtu.be/8GzzIQ3C6DQ。

<a href="https://youtu.be/8GzzIQ3C6DQ"><img width=500 src="https://i3.ytimg.com/vi/8GzzIQ3C6DQ/maxresdefault.jpg"></a>

在教育中的应用（RoboCamp）：https://youtu.be/Wd3yaorjTx0。

<a href="https://youtu.be/Wd3yaorjTx0"><img width=500 src="https://i3.ytimg.com/vi/Wd3yaorjTx0/sddefault.jpg"></a>

查看[用户作品展示](docs/user.md)：

<a href="docs/user.md"><img src="docs/img/user/user.jpg" width=500></a>

## 仿真

仿真器使用 Gazebo 实现，运行原始 Arduino 代码：

<img src="docs/img/simulator1.png" width=500 alt="Flix 仿真器">

## 文档

1. [组装说明](docs/assembly.md)。
2. [使用：构建、设置和飞行](docs/usage.md)。
3. [仿真](gazebo/README.md)。
4. [Python 库](tools/pyflix/README.md)。

其他文章：

* [用户作品展示](docs/user.md)。
* [固件架构概述](docs/firmware.md)。
* [故障排除](docs/troubleshooting.md)。
* [日志分析](docs/log.md)。

## 组件

|类型|部件|图片|数量|
|-|-|:-:|:-:|
|微控制器板|ESP32 Mini|<img src="docs/img/esp32.jpg" width=100>|1|
|IMU（和气压计¹）板|GY‑91, MPU-9265（或其他 MPU‑9250/MPU‑6500 板）<br>ICM20948V2 (ICM‑20948)³<br>GY-521 (MPU-6050)³⁻¹|<img src="docs/img/gy-91.jpg" width=90 align=center><br><img src="docs/img/icm-20948.jpg" width=100><br><img src="docs/img/gy-521.jpg" width=100>|1|
|升压转换器（可选，用于更稳定的电源）|5V 输出|<img src="docs/img/buck-boost.jpg" width=100>|1|
|电机|8520 3.7V 有刷电机。<br>需要确切的 3.7V 电压电机，而不是范围工作电压（3.7V — 6V）。<br>确保电机轴直径和螺旋桨孔直径匹配！|<img src="docs/img/motor.jpeg" width=100>|4|
|螺旋桨|55 mm（或 65 mm）|<img src="docs/img/prop.jpg" width=100>|4|
|MOSFET（晶体管）|100N03A 或[类似产品](https://t.me/opensourcequadcopter/33)|<img src="docs/img/100n03a.jpg" width=100>|4|
|下拉电阻|10 kΩ|<img src="docs/img/resistor10k.jpg" width=100>|4|
|3.7V Li-Po 电池|LW 952540（或任何尺寸兼容的）|<img src="docs/img/battery.jpg" width=100>|1|
|电池连接线|MX2.0 2P 母头|<img src="docs/img/mx.png" width=100>|1|
|Li-Po 电池充电器|任意|<img src="docs/img/charger.jpg" width=100>|1|
|IMU 板安装螺丝|M3x5|<img src="docs/img/screw-m3.jpg" width=100>|2|
|机架组装螺丝|M1.4x5|<img src="docs/img/screw-m1.4.jpg" height=30 align=center>|4|
|机架主体|3D 打印²：[`stl`](docs/assets/flix-frame-1.1.stl) [`step`](docs/assets/flix-frame-1.1.step)<br>推荐设置：层高 0.2 mm，线宽 0.4 mm，填充 100%。|<img src="docs/img/frame1.jpg" width=100>|1|
|机架顶部|3D 打印：[`stl`](docs/assets/esp32-holder.stl) [`step`](docs/assets/esp32-holder.step)|<img src="docs/img/esp32-holder.jpg" width=100>|1|
|IMU 板安装垫圈|3D 打印：[`stl`](docs/assets/washer-m3.stl) [`step`](docs/assets/washer-m3.step)|<img src="docs/img/washer-m3.jpg" width=100>|2|
|控制器（推荐）|CC2500 发射器，如 BetaFPV LiteRadio CC2500（RC 接收器/Wi-Fi）。<br>双摇杆游戏手柄（仅 Wi-Fi）— 查看[推荐的游戏手柄](https://docs.qgroundcontrol.com/master/en/qgc-user-guide/setup_view/joystick.html#supported-joysticks)。<br>其他⁵|<img src="docs/img/betafpv.jpg" width=100><img src="docs/img/logitech.jpg" width=80>|1|
|*RC 接收器（可选）*|*DF500 或其他³*|<img src="docs/img/rx.jpg" width=100>|1|
|导线|推荐 28 AWG|<img src="docs/img/wire-28awg.jpg" width=100>||
|胶带、双面胶||||

*¹ — 气压计暂未使用。*<br>
*² — 此机架针对 GY-91 板优化，如果使用其他板，应修改板安装孔位置。*<br>
*³ — 您也可以使用任何具有 SBUS 接口的发射器-接收器对。*

组装所需工具：

* 3D 打印机。
* 电烙铁。
* 焊锡丝（带助焊剂）。
* 螺丝刀。
* 万用表。

欢迎您修改设计或代码，并创建自己的改进版本。将您的结果发送到[官方 Telegram 群组](https://t.me/opensourcequadcopterchat)，或直接发送给作者（[E-mail](mailto:okalachev@gmail.com)，[Telegram](https://t.me/okalachev)）。

## 原理图

### 简化连接图

<img src="docs/img/schematics1.svg" width=700 alt="Flix 版本 1 原理图">

*（虚线元素为可选）。*

电机连接方案：

<img src="docs/img/mosfet-connection.png" height=400 alt="MOSFET 连接方案">

您可以查看用户贡献的[完整电路图变体](https://miro.com/app/board/uXjVN-dTjoo=/?moveToWidget=3458764612338222067&cot=14)。

### 注意事项

* 使用 Li-Po 电池通过 VCC (+) 和 GND (-) 引脚为 ESP32 Mini 供电。
* 使用 VSPI 将 IMU 板连接到 ESP32 Mini，使用 3.3V 和 GND 引脚为其供电：

  |IMU 引脚|ESP32 引脚|
  |-|-|
  |GND|GND|
  |3.3V|3.3V|
  |SCL *(SCK)*|SVP (GPIO18)|
  |SDA *(MOSI)*|GPIO23|
  |SAO *(MISO)*|GPIO19|
  |NCS|GPIO5|

* 将下拉电阻焊接到 MOSFET。
* 使用 MOSFET 将电机连接到 ESP32 Mini，按照以下方案：

  |电机|位置|方向|螺旋桨类型|电机线|GPIO|
  |-|-|-|-|-|-|
  |电机 0|后左|逆时针|B|黑和白|GPIO12 *(TDI)*|
  |电机 1|后右|顺时针|A|蓝和红|GPIO13 *(TCK)*|
  |电机 2|前右|逆时针|B|黑和白|GPIO14 *(TMS)*|
  |电机 3|前左|顺时针|A|蓝和红|GPIO15 *(TD0)*|

  顺时针电机有蓝红线，对应螺旋桨类型 A（在螺旋桨上标记）。
  逆时针电机有黑白线，对应螺旋桨类型 B。

* 可选地将 RC 接收器连接到 ESP32 的 UART2：

  |接收器引脚|ESP32 引脚|
  |-|-|
  |GND|GND|
  |VIN|VCC（或 3.3V，取决于接收器）|
  |信号 (TX)|GPIO4¹|

*¹ — UART2 RX 引脚在 Arduino ESP32 核心 3.0 中[已更改](https://docs.espressif.com/projects/arduino-esp32/en/latest/migration_guides/2.x_to_3.0.html#id14)为 GPIO4。*

## 资源

* 关于开发飞行器和飞行控制器的 Telegram 频道（俄语）：https://t.me/opensourcequadcopter。
* 官方 Telegram 群组：https://t.me/opensourcequadcopterchat。
* 关于飞行器开发的详细文章（俄语）：https://habr.com/ru/articles/814127/。

## 免责声明

这是一个 DIY 项目，希望您觉得有趣和有用。但是，它不容易组装和设置，并且"按原样"提供，不提供任何保证。不保证它能完美工作，甚至根本不工作。

⚠️ 作者不对因使用本项目而造成的任何损坏、伤害或损失负责。使用风险自负！
