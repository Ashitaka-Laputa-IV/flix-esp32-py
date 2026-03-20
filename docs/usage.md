# 使用：构建、设置和飞行

要让 Flix 四旋翼飞行器飞行，您需要构建固件，将其上传到 ESP32 板，并设置飞行器进行飞行。

要获取固件源代码，使用 git 克隆仓库：

```bash
git clone https://github.com/okalachev/flix.git && cd flix
```

初学者可以[下载源代码为 ZIP 压缩包](https://github.com/okalachev/flix/archive/refs/heads/master.zip)。

## 构建固件

您可以使用 **Arduino IDE**（对初学者更容易）或**命令行**来构建和上传固件。

### Arduino IDE（Windows、Linux、macOS）

<img src="img/arduino-ide.png" width="400" alt="在 Arduino IDE 中打开的 Flix 固件">

1. 安装 [Arduino IDE](https://www.arduino.cc/en/software)（推荐版本 2）。
2. *Windows 用户可能需要安装 [Silicon Labs 的 USB 到 UART 桥接驱动程序](https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers)。*
3. 安装 ESP32 核心，版本 3.3.6。请参阅 Espressif 的[官方说明](https://docs.espressif.com/projects/arduino-esp32/en/latest/installing.html#installing-using-arduino-ide)了解如何在 Arduino IDE 中安装 ESP32 核心。
4. 使用[库管理器](https://docs.arduino.cc/software/ide-v2/tutorials/ide-v2-installing-a-library)安装以下库：
   * `FlixPeriph`，最新版本。
   * `MAVLink`，版本 2.0.25。
5. 在 Arduino IDE 中从下载的固件源代码中打开 `flix/flix.ino` 草图。
6. 将 ESP32 板连接到计算机，在 Arduino IDE 中选择正确的板类型（ESP32 Mini 选择 *WEMOS D1 MINI ESP32*）和端口。
7. 使用 Arduino IDE [构建和上传](https://docs.arduino.cc/software/ide-v2/tutorials/getting-started/ide-v2-uploading-a-sketch)固件。

### 命令行（Windows、Linux、macOS）

1. [安装 Arduino CLI](https://arduino.github.io/arduino-cli/installation/)。

   在 Linux 上，这样安装：

   ```bash
   curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | BINDIR=~/.local/bin sh
   ```

2. Windows 用户可能需要安装 [Silicon Labs 的 USB 到 UART 桥接驱动程序](https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers)。
3. 使用 `make` 编译固件。Arduino 依赖项将自动安装：

   ```bash
   make
   ```

   您可以使用以下命令将固件刷写到板：

   ```bash
   make upload
   ```

   您还可以使用以下命令编译固件、上传并启动串口监视：

   ```bash
   make upload monitor
   ```

在 [Makefile](../Makefile) 中查看其他可用的 Make 命令。

> [!TIP]
> 您可以在没有连接 IMU 和其他外设的裸 ESP32 板上测试固件。`flix` Wi-Fi 网络应该出现，包括控制台和 QGroundControl 连接在内的所有基本功能都应该工作。

## 首次飞行前

### 选择 IMU 型号

如果使用与 MPU9250 不同的 IMU 型号，请在 `imu.ino` 中更改 `imu` 变量声明：

```cpp
ICM20948 imu(SPI);  // 对于 ICM-20948
MPU6050 imu(Wire);  // 对于 MPU-6050
```

### 使用 QGroundControl 连接

QGroundControl 是一个地面站软件，可用于监视和控制飞行器。

1. 安装 [QGroundControl](https://docs.qgroundcontrol.com/master/en/qgc-user-guide/getting_started/download_and_install.html)的移动或桌面版本。
2. 为飞行器供电。
3. 将计算机或智能手机连接到出现的 `flix` Wi-Fi 网络（密码：`flixwifi`）。
4. 启动 QGroundControl 应用程序。它应该连接并开始自动显示飞行器的遥测数据。

### 访问控制台

控制台是一个命令行界面（CLI），允许与飞行器交互、更改参数和执行各种操作。有两种访问控制台的方法：使用**串口**或使用**QGroundControl（无线）**。

要使用串口访问控制台：

1. 使用 USB 电缆将 ESP32 板连接到计算机。
2. 在 Arduino IDE 中打开串口监视器（或在命令行中使用 `make monitor`）。
3. 在 Arduino IDE 中，确保波特率设置为 115200。

要使用 QGroundControl 访问控制台：

1. 使用 QGroundControl 应用程序连接到飞行器。
2. 转到 QGroundControl 菜单 ⇒ *Vehicle Setup* ⇒ *Analyze Tools* ⇒ *MAVLink Console*。

<img src="img/cli.png" width="400">

> [!TIP]
> 使用 `help` 命令查看可用命令列表。

### 访问参数

飞行器使用参数进行配置。要访问和修改它们，请转到 QGroundControl 菜单 ⇒ *Vehicle Setup* ⇒ *Parameters*：

<img src="img/parameters.png" width="400">

您还可以使用控制台中的 `p` 命令处理参数。参数名称不区分大小写。

### 定义 IMU 方向

使用参数定义 IMU 板轴相对于飞行器轴的方向：`IMU_ROT_ROLL`、`IMU_ROT_PITCH` 和 `IMU_ROT_YAW`。

飞行器的 *X* 轴指向前方，*Y* 轴指向左侧，*Z* 轴指向上方，支持的 IMU 板的 *X* 轴指向引脚侧，*Z* 轴从组件侧指向上方：

<img src="img/imu-axes.png" width="200">

使用下表为常见 IMU 方向设置参数：

|方向|参数|方向|参数|
|:-:|-|-|-|
|<img src="img/imu-rot-1.png" width="180">|`IMU_ROT_ROLL` = 0<br>`IMU_ROT_PITCH` = 0<br>`IMU_ROT_YAW` = 0    |<img src="img/imu-rot-5.png" width="180">|`IMU_ROT_ROLL` = 3.142<br>`IMU_ROT_PITCH` = 0<br>`IMU_ROT_YAW` = 0|
|<img src="img/imu-rot-2.png" width="180">|`IMU_ROT_ROLL` = 0<br>`IMU_ROT_PITCH` = 0<br>`IMU_ROT_YAW` = 1.571|<img src="img/imu-rot-6.png" width="180">|`IMU_ROT_ROLL` = 3.142<br>`IMU_ROT_PITCH` = 0<br>`IMU_ROT_YAW` = -1.571|
|<img src="img/imu-rot-3.png" width="180">|`IMU_ROT_ROLL` = 0<br>`IMU_ROT_PITCH` = 0<br>`IMU_ROT_YAW` = 3.142|<img src="img/imu-rot-7.png" width="180">|`IMU_ROT_ROLL` = 3.142<br>`IMU_ROT_PITCH` = 0<br>`IMU_ROT_YAW` = 3.142|
|<img src="img/imu-rot-4.png" width="180"><br>☑️ **默认**|<br>`IMU_ROT_ROLL` = 0<br>`IMU_ROT_PITCH` = 0<br>`IMU_ROT_YAW` = -1.571|<img src="img/imu-rot-8.png" width="180">|`IMU_ROT_ROLL` = 3.142<br>`IMU_ROT_PITCH` = 0<br>`IMU_ROT_YAW` = 1.571|

### 校准加速度计

飞行前需要校准加速度计：

1. 使用 QGroundControl（推荐）或串口监视器访问控制台。
2. 在那里输入 `ca` 命令并按照说明操作。

### 设置电机

如果使用非默认电机引脚，请使用参数设置引脚编号：`MOTOR_PIN_FL`、`MOTOR_PIN_FR`、`MOTOR_PIN_RL`、`MOTOR_PIN_RR`（分别对应前左、前右、后左、后右）。

如果使用无刷电机和 ESC：

1. 使用参数设置适当的 PWM：`MOT_PWM_STOP`、`MOT_PWM_MIN` 和 `MOT_PWM_MAX`（1000、1000 和 2000 是典型的）。
2. 使用 `MOT_PWM_FREQ` 参数降低 PWM 频率（400 是典型的）。

重新启动飞行器以应用更改。

> [!CAUTION]
> **配置电机时请卸下螺旋桨！** 如果配置不当，您可能无法停止它们。

### 重要：检查一切是否正常

1. 检查 IMU 是否工作：在控制台中执行 `imu` 命令并检查输出：

   * `status` 字段应为 `OK`。
   * `rate` 字段应约为 1000（Hz）。
   * 当您移动飞行器时，`accel` 和 `gyro` 字段应该改变。
   * `accel bias` 和 `accel scale` 字段应包含校准参数（不是零和一）。
   * `gyro bias` 字段应包含估计的陀螺仪偏置（不是零）。
   * 当飞行器仍在地面时，`landed` 字段应为 `1`，当您将其抬起时应为 `0`。

2. 检查姿态估计：使用 QGroundControl 连接到飞行器，在不同方向旋转飞行器并检查 QGroundControl 中显示的姿态估计是否正确。将您的姿态指示器（在*大垂直*模式下）与视频进行比较：

    <a href="https://youtu.be/yVRN23-GISU"><img width=300 src="https://i3.ytimg.com/vi/yVRN23-GISU/maxresdefault.jpg"></a>

3. 执行电机测试。使用以下命令 **— 运行测试前请卸下螺旋桨！**

   * `mfr` — 旋转前右电机（逆时针）。
   * `mfl` — 旋转前左电机（顺时针）。
   * `mrl` — 旋转后左电机（逆时针）。
   * `mrr` — 旋转后右电机（顺时针）。

   确保旋转方向和螺旋桨类型与下图匹配：

   <img src="img/motors.svg" width=200>

> [!WARNING]
> 从 USB 为飞行器供电时永远不要运行电机，始终使用电池。

## 设置遥控器

有几种控制飞行器飞行的方法：使用**智能手机**（Wi-Fi）、使用**SBUS 遥控器**或使用**USB 遥控器**（Wi-Fi）。

### 使用智能手机控制

1. 在智能手机上安装 [QGroundControl 移动应用程序](https://docs.qgroundcontrol.com/master/en/qgc-user-guide/getting_started/download_and_install.html#android)。
2. 使用电池为飞行器供电。
3. 将智能手机连接到出现的 `flix` Wi-Fi 网络（密码：`flixwifi`）。
4. 打开 QGroundControl 应用程序。它应该连接并开始自动显示飞行器的遥测数据。
5. 转到设置并启用*虚拟摇杆*。*自动居中油门*设置**应该禁用**。
6. 使用虚拟摇杆飞行飞行器！

> [!TIP]
> 使用智能手机飞行时降低 `CTL_TILT_MAX` 参数，使控制不那么敏感。

### 使用遥控器控制

在使用远程 SBUS 连接的遥控器之前，您需要校准它：

1. 使用 QGroundControl（推荐）或串口监视器访问控制台。
2. 输入 `cr` 命令并按照说明操作。
3. 使用遥控器飞行飞行器！

### 使用 USB 遥控器控制

如果您的飞行器没有安装 RC 接收器，您可以使用 USB 遥控器和 QGroundControl 应用程序来飞行它。

1. 在计算机上安装 [QGroundControl](https://docs.qgroundcontrol.com/master/en/qgc-user-guide/getting_started/download_and_install.html)应用程序。
2. 将 USB 遥控器连接到计算机。
3. 为飞行器供电。
4. 将计算机连接到出现的 `flix` Wi-Fi 网络（密码：`flixwifi`）。
5. 启动 QGroundControl 应用程序。它应该连接并开始自动显示飞行器的遥测数据。
6. 转到 QGroundControl 菜单 ⇒ *Vehicle Setup* ⇒ *Joystick*。在那里校准您的 USB 遥控器。
7. 使用 USB 遥控器飞行飞行器！

## 飞行

对于虚拟摇杆和物理摇杆，默认控制方案是左摇杆控制油门和偏航，右摇杆控制俯仰和横滚：

<img src="img/controls.svg" width="300">

### 解锁和锁定

要启动电机，您应该**解锁**飞行器。为此，将左摇杆移动到右下角：

<img src="img/arming.svg" width="150">

之后，电机**将以低速开始旋转**，表示飞行器已解锁并准备好飞行。

完成飞行后，**锁定**飞行器，将左摇杆移动到左下角：

<img src="img/disarming.svg" width="150">

> [!NOTE]
> 如果出现问题，请参阅[故障排除](troubleshooting.md)文章。

### 飞行模式

飞行模式使用遥控器上的模式开关（如果已配置）或使用控制台命令进行更改。主要飞行模式是 *STAB*。

#### STAB

在此模式下，飞行器稳定其姿态（方向）。左摇杆控制油门和偏航率，右摇杆控制俯仰和横滚角度。

> [!IMPORTANT]
> 飞行器不稳定其位置，因此可能会有轻微漂移。飞行员应该手动补偿它。

#### ACRO

在此模式下，飞行员控制角速率。这种控制方法难以飞行，主要用于 FPV 竞赛。

#### RAW

*RAW* 模式禁用所有稳定，飞行员输入直接混合到电机。不涉及 IMU 传感器。此模式仅用于测试和演示目的，基本上飞行器**无法在此模式下飞行**。

#### AUTO

在此模式下，忽略飞行员输入（模式开关除外）。可以使用 [pyflix](../tools/pyflix/) Python 库控制飞行器，或通过修改固件来实现所需行为。

如果飞行员移动控制摇杆，飞行器将切换回 *STAB* 模式。

## Wi-Fi 配置

您可以使用参数和控制台命令配置 Wi-Fi。

Wi-Fi 模式在 QGroundControl 或控制台中使用 `WIFI_MODE` 参数选择：

* `0` — Wi-Fi 禁用。
* `1` — 接入点模式 *(AP)* — 飞行器创建 Wi-Fi 网络。
* `2` — 客户端模式 *(STA)* — 飞行器连接到现有的 Wi-Fi 网络。
* `3` — *ESP-NOW（尚未实现）*。

> [!WARNING]
> 测试表明，客户端模式可能会导致遥控出现**额外延迟**（由于重新传输），因此通常不推荐。

SSID 和密码使用 `ap` 和 `sta` 控制台命令配置：

```
ap <ssid> <password>
sta <ssid> <password>
```

配置接入点模式的示例：

```
ap my-flix-ssid mypassword123
p WIFI_MODE 1
```

禁用 Wi-Fi：

```
p WIFI_MODE 0
```

## 飞行日志

飞行后，您可以无线下载飞行日志进行分析。为此，请在计算机上运行以下命令：

```bash
make log
```

在[日志分析](log.md)文章中查看有关日志分析的更多详细信息。
