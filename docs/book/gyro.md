# 陀螺仪

<div class="firmware">
	<strong>固件文件：</strong>
	<a href="https://github.com/okalachev/flix/blob/canonical/flix/imu.ino"><code>imu.ino</code></a> <small>(规范版本)</small>.<br>
	当前版本: <a href="https://github.com/okalachev/flix/blob/master/flix/imu.ino"><code>imu.ino</code></a>.
</div>

没有反馈传感器就不可能维持四旋翼飞行器的稳定飞行。其中最重要的是 **MEMS 陀螺仪**。MEMS 陀螺仪是经典机械陀螺仪的微机电模拟物。

机械陀螺仪由旋转的圆盘组成，该圆盘在空间中保持其方向。由于这种效应，可以确定对象在空间中的方向。

在 MEMS 陀螺仪中没有旋转部件，它放置在一个微小的芯片中。它只能测量对象围绕三个轴的当前角旋转速率：X、Y 和 Z。

|机械陀螺仪|MEMS 陀螺仪|
|-|-|
|<img src="img/gyroscope.jpg" width="300" alt="机械陀螺仪">|<img src="img/mpu9250.jpg" width="100" alt="MEMS 陀螺仪 MPU-9250">|

MEMS 陀螺仪通常集成在惯性模块（IMU）中，其中还包括加速度计和磁力计。IMU 模块通常称为 9 轴传感器，因为它测量：

* 围绕三个轴的角旋转速率（陀螺仪）。
* 围绕三个轴的加速度（加速度计）。
* 围绕三个轴的磁场（磁力计）。

Flix 支持以下 IMU 型号：

* InvenSense MPU-9250。
* InvenSense MPU-6500。
* InvenSense ICM-20948。

> [!NOTE]
> MEMS 陀螺仪测量对象的角旋转速率。

## 连接接口

大多数 IMU 模块通过 I²C 和 SPI 接口连接到微控制器。这两个接口都是*数据总线*，即允许将多个设备连接到一个微控制器。

**I²C 接口**使用两根线来传输数据和时钟信号。通过将设备地址传输到总线来选择用于通信的设备。不同的设备有不同的地址，微控制器可以依次与多个设备通信。

**SPI 接口**使用两根线来传输数据，一根用于时钟信号，另一根用于选择设备。同时，总线上的每个设备都分配一个单独的 GPIO 引脚用于选择。在不同的实现中，此引脚称为 CS/NCS（芯片选择）或 SS（从设备选择）。当设备的 CS 引脚处于活动状态（其上的电压较低）时，该设备被选中用于通信。

在飞行控制器中，IMU 通常通过 SPI 连接，因为它提供明显更高的数据传输速度和更低的延迟。通过 I²C 接口连接 IMU（例如，在微控制器引脚不足的情况下）是可能的，但不推荐。

IMU 通过 SPI 接口连接到 ESP32 微控制器如下所示：

|IMU 板引脚|ESP32 引脚|
|-|-|
|VCC/3V3|3V3|
|GND|GND|
|SCL|IO18|
|SDA *(MOSI)*|IO23|
|SAO/AD0 *(MISO)*|IO19|
|NCS|IO5|

此外，许多 IMU 可以在有新数据时"唤醒"微控制器。为此使用 INT 引脚，该引脚连接到微控制器的任何 GPIO 引脚。使用这种配置，可以使用中断来处理来自 IMU 的新数据，而不是定期轮询传感器。这允许在复杂的控制算法中降低微控制器的负载。

> [!WARNING]
> 在某些 IMU 板上，例如 ICM-20948，缺少稳压器，因此无法将它们连接到提供 5 V 电压的 ESP32 VIN 引脚。仅允许从 3V3 引脚供电。

## 使用陀螺仪

为了与 IMU 交互，包括使用陀螺仪，Flix 使用 *FlixPeriph* 库。该库通过 Arduino IDE 库管理器安装：

<img src="img/flixperiph.png" width="300">

要使用 IMU，使用对应于 IMU 型号的类：`MPU9250`、`MPU6500` 或 `ICM20948`。用于不同 IMU 的类对于基本操作具有统一的接口，因此可以轻松地在不同的 IMU 型号之间切换。MPU-6500 传感器实际上完全兼容 MPU-9250，因此 `MPU9250` 类实际上支持这两种型号。

## 陀螺仪轴的方向

来自陀螺仪的数据是围绕三个轴的角速率：X、Y 和 Z。InvenSense IMU 的这些轴的方向可以通过芯片角落的小点轻松确定。陀螺仪测量的坐标系和旋转方向在图中表示：

<img src="img/imu-axes.svg" width="300" alt="IMU 坐标系">

流行 IMU 板中的坐标系位置：

|GY-91|MPU-92/65|ICM-20948|
|-|-|-|
|<img src="https://github.com/okalachev/flixperiph/raw/refs/heads/master/img/gy91-axes.svg" width="200" alt="GY-91 板坐标系">|<img src="https://github.com/okalachev/flixperiph/raw/refs/heads/master/img/mpu9265-axes.svg" width="200" alt="MPU-9265 板坐标系">|<img src="https://github.com/okalachev/flixperiph/raw/refs/heads/master/img/icm20948-axes.svg" width="200" alt="ICM-20948 板坐标系">|

InvenSense IMU 的磁力计通常是集成在芯片中的单独设备，因此其坐标系可能不同。FlixPeriph 库隐藏了这种差异，并将来自磁力计的数据转换为陀螺仪和加速度计的坐标系。

## 读取数据

FlixPeriph 库的接口符合 Arduino 中采用的风格。要开始使用 IMU，需要创建相应类的对象并调用 `begin()` 方法。IMU 连接的接口（SPI 或 I²C）传递给类构造函数：

```cpp
#include <FlixPeriph.h>
#include <SPI.h>

MPU9250 imu(SPI);

void setup() {
	Serial.begin(115200);
	bool success = imu.begin();
	if (!success) {
		Serial.println("Failed to initialize IMU");
	}
}
```

对于单次读取数据，使用 `read()` 方法。然后通过 `getGyro(x, y, z)` 方法获取来自陀螺仪的数据。此方法将围绕相应轴的角速率（以弧度/秒为单位）写入变量 `x`、`y` 和 `z`。

如果需要保证将读取新数据，可以使用 `waitForData()` 方法。此方法阻塞程序执行，直到 IMU 中出现新数据。`waitForData()` 方法允许将主循环 `loop` 的频率绑定到 IMU 数据更新频率。这便于组织四旋翼飞行器的主控制循环。

用于从陀螺仪读取数据并将其输出到控制台以在 Serial Plotter 中绘制图形的程序如下所示：

```cpp
#include <FlixPeriph.h>
#include <SPI.h>

MPU9250 imu(SPI);

void setup() {
	Serial.begin(115200);
	bool success = imu.begin();
	if (!success) {
		Serial.println("Failed to initialize IMU");
	}
}

void loop() {
	imu.waitForData();

	float gx, gy, gz;
	imu.getGyro(gx, gy, gz);

	Serial.printf("gx:%f gy:%f gz:%f\n", gx, gy, gz);
	delay(50); // 减慢输出
}
```

启动程序后，在 Serial Plotter 中可以看到角速率的图形。例如，当围绕垂直 Z 轴旋转 IMU 时，图形将如下所示：

<img src="img/gyro-plotter.png">

## 陀螺仪配置

在 Flix 代码中，IMU 配置在 `configureIMU` 函数中进行。在此函数中，配置陀螺仪的三个主要参数：测量范围、采样频率和 LPF 滤波器频率。

### 采样频率

大多数 IMU 可以以不同的频率更新数据。在飞行控制器中，通常使用从 500 Hz 到 8 kHz 的更新频率。频率越高，飞行控制的精度越高，但微控制器的负载也越大。

采样频率通过 `setSampleRate()` 方法设置。在 Flix 中使用 1 kHz 的频率：

```cpp
IMU.setRate(IMU.RATE_1KHZ_APPROX);
```

由于并非所有支持的 IMU 都能严格在 1 kHz 的频率下工作，因此在 FlixPeriph 库中存在近似设置采样频率的可能性。例如，对于 ICM-20948 IMU，使用这种设置，实际采样频率将等于 1125 Hz。

FlixPeriph 库中可用的其他采样频率设置：

* `RATE_MIN` — 特定 IMU 的最小频率。
* `RATE_50HZ_APPROX` — 接近 50 Hz 的值。
* `RATE_1KHZ_APPROX` — 接近 1 kHz 的值。
* `RATE_8KHZ_APPROX` — 接近 8 kHz 的值。
* `RATE_MAX` — 特定 IMU 的最大频率。

#### 测量范围

大多数 MEMS 陀螺仪支持多个角速率测量范围。选择较小范围的主要优势是更高的灵敏度。在飞行控制器中，通常选择从 –2000 到 2000 度/秒的最大测量范围，以确保快速机动的可能性。

在 FlixPeriph 库中，陀螺仪的测量范围通过 `setGyroRange()` 方法设置：

```cpp
imu.setGyroRange(imu.GYRO_RANGE_2000DPS);
```

### LPF 滤波器

InvenSense IMU 可以通过低通滤波器（LPF）在硬件级别过滤测量值。Flix 为陀螺仪实现自己的滤波器，以便在支持不同 IMU 时具有更大的灵活性。因此，对于内置 LPF，设置最大截止频率：

```cpp
imu.setDLPF(imu.DLPF_MAX);
```

## 陀螺仪校准

像任何测量设备一样，陀螺仪在测量中引入失真。这些失真的最简单模型将它们分为静态偏移 *(bias)* 和随机噪声 *(noise)*：

\\[ gyro_{xyz}=rates_{xyz}+bias_{xyz}+noise \\]

为了方向估计和飞行器控制子系统的准确工作，必须估计陀螺仪的 *bias* 并在计算中考虑它。为此，在程序启动时进行陀螺仪校准，这在 `calibrateGyro()` 函数中实现。此函数在静止状态下读取陀螺仪数据 1000 次并对其进行平均。获得的值被视为陀螺仪的 *bias*，并从测量值中减去。

用于输出陀螺仪数据并进行校准的程序：

```cpp
#include <FlixPeriph.h>
#include <SPI.h>

MPU9250 imu(SPI);

float gyroBiasX, gyroBiasY, gyroBiasZ; // 陀螺仪 bias

void setup() {
	Serial.begin(115200);
	bool success = imu.begin();
	if (!success) {
		Serial.println("Failed to initialize IMU");
	}
	calibrateGyro();
}

void loop() {
	float gx, gy, gz;
	imu.waitForData();
	imu.getGyro(gx, gy, gz);

	// 消除陀螺仪 bias
	gx -= gyroBiasX;
	gy -= gyroBiasY;
	gz -= gyroBiasZ;

	Serial.printf("gx:%f gy:%f gz:%f\n", gx, gy, gz);
	delay(50); // 减慢输出
}

void calibrateGyro() {
	const int samples = 1000;
	Serial.println("Calibrating gyro, stand still");

	gyroBiasX = 0;
	gyroBiasY = 0;
	gyroBiasZ = 0;

	// 获取 1000 次陀螺仪测量
	for (int i = 0; i < samples; i++) {
		imu.waitForData();
		float gx, gy, gz;
		imu.getGyro(gx, gy, gz);
		gyroBiasX += gx;
		gyroBiasY += gy;
		gyroBiasZ += gz;
	}

	// 平均值
	gyroBiasX = gyroBiasX / samples;
	gyroBiasY = gyroBiasY / samples;
	gyroBiasZ = gyroBiasZ / samples;

	Serial.printf("Gyro bias X: %f\n", gyroBiasX);
	Serial.printf("Gyro bias Y: %f\n", gyroBiasY);
	Serial.printf("Gyro bias Z: %f\n", gyroBiasZ);
}
```

未校准时静止状态下陀螺仪的数据图。可以看到每个轴的静态误差：

<img src="img/gyro-uncalibrated-plotter.png">

校准后静止状态下陀螺仪的数据图：

<img src="img/gyro-calibrated-plotter.png">

校准后的陀螺仪数据与来自加速度计的数据一起进入*状态估计子系统*。

## 其他材料

* [MPU-9250 数据手册](https://invensense.tdk.com/wp-content/uploads/2015/02/PS-MPU-9250A-01-v1.1.pdf)。
* [MPU-6500 数据手册](https://invensense.tdk.com/wp-content/uploads/2020/06/PS-MPU-6500A-01-v1.3.pdf)。
* [ICM-20948 数据手册](https://invensense.tdk.com/wp-content/uploads/2016/06/DS-000189-ICM-20948-v1.3.pdf)。
