# 组装指南

焊接好的组件（[原理图变体](https://miro.com/app/board/uXjVN-dTjoo=/?moveToWidget=3458764612338222067&cot=14)）：

<img src="img/assembly/1.jpg" width=600>

<br>使用双面胶将 ESP32 固定到机架顶部（ESP32 支架）：

<img src="img/assembly/2.jpg" width=600>

<br>使用两个垫圈将 IMU 板用螺丝固定到机架上：

<img src="img/assembly/3.jpg" width=600>

<br>如图所示使用 M3x5 螺丝固定 IMU：

<img src="img/assembly/4.jpg" width=600>

<br>安装电机，使用胶带将 MOSFET 固定到机架上：

<img src="img/assembly/5.jpg" width=600>

<br>使用 M1.4x5 螺丝将 ESP32 支架固定到机架上：

<img src="img/assembly/6.jpg" width=600>

<br>组装完成的飞行器：

<img src="img/assembly/7.jpg" width=600>

## 电机方向

> [!WARNING]
> 上面的飞行器是早期版本，它的电机方向方案是**相反的**。照片仅用于说明一般的组装过程。

使用标准电机方向方案：

<img src="img/motors.svg" width=200>

电机连接表：

|电机|位置|方向|螺旋桨类型|电机线|GPIO|
|-|-|-|-|-|-|
|电机 0|后左|逆时针|B|黑和白|GPIO12 *(TDI)*|
|电机 1|后右|顺时针|A|蓝和红|GPIO13 *(TCK)*|
|电机 2|前右|逆时针|B|黑和白|GPIO14 *(TMS)*|
|电机 3|前左|顺时针|A|蓝和红|GPIO15 *(TD0)*|

## 电机紧固

电机应该安装得非常紧 — 任何振动都可能导致姿态估计不良和飞行不稳定。如果电机松动，使用小块胶带将它们牢固固定，如下图所示：

<img src="img/motor-tape.jpg" width=600>
