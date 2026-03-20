# Flix 版本 0

Flix 版本 0（已过时）：

<img src="img/flix.jpg" width=500 alt="Flix 四旋翼飞行器">

## 组件列表

|类型|部件|图片|数量|
|-|-|-|-|
|微控制器板|ESP32 Mini|<img src="img/esp32.jpg" width=100>|1|
|IMU 和气压计² 板|GY-91（或其他 MPU-9250 板）|<img src="img/gy-91.jpg" width=100>|1|
|四旋翼飞行器机架|K100|<img src="img/frame.jpg" width=100>|1|
|电机|8520 3.7V 有刷电机（**轴 0.8mm！**）|<img src="img/motor.jpeg" width=100>|4|
|螺旋桨|Hubsan 55 mm|<img src="img/prop.jpg" width=100>|4|
|电机 ESC|2.7A 1S 双向微型有刷 ESC|<img src="img/esc.jpg" width=100>|4|
|RC 发射器|KINGKONG TINY X8|<img src="img/kingkong.jpg" width=100>|1|
|RC 接收器|DF500 (SBUS)|<img src="img/rx.jpg" width=100>|1|
|~~SBUS 反相器~~*||<img src="img/inv.jpg" width=100>|~~1~~|
|电池|3.7 Li-Po 850 MaH 60C|||
|电池充电器||<img src="img/charger.jpg" width=100>|1|
|导线、连接器、胶带、...||||

*\* — 不需要，因为 ESP32 支持[软件引脚反相](https://github.com/bolderflight/sbus#inverted-serial)。*

## 原理图

<img src="img/schematics.svg" width=800 alt="Flix 原理图">

您还可以查看用户贡献的[完整电路图变体](https://miro.com/app/board/uXjVN-dTjoo=/?moveToWidget=3458764574482511443&cot=14)。
