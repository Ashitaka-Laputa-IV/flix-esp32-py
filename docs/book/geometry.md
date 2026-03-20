# 向量、四元数

在四旋翼飞行器控制算法中，广泛使用了几何（和代数）对象，如**向量**和**四元数**。它们可以简化数学计算并提高代码的可读性。在本章中，我们将专门介绍 Flix 四旋翼飞行器控制算法中使用的几何对象，重点放在它们的实际使用方面。

## 坐标系

### 坐标轴

要在三维空间中处理对象，必须定义*坐标系*。众所周知，坐标系由三个相互垂直的轴定义，这些轴表示为 *X*、*Y* 和 *Z*。这些轴的表示顺序取决于我们选择的坐标系 — *左手*或*右手*：

|左手坐标系|右手坐标系|
|-----------------------|------------------------|
|<img src="img/left-axes.svg" alt="左手坐标系" width="200">|<img src="img/right-axes.svg" alt="右手坐标系" width="200">|

在 Flix 中，所有数学计算都使用**右手坐标系**，这是机器人和航空领域的标准。

此外，还需要选择轴的方向 — 在 Flix 中，它们按照 [REP-103](https://www.ros.org/reps/rep-0103.html) 标准选择。对于在与飞行器机身相关的移动坐标系中定义的量，采用 <abbr title="Forward Left Up">FLU</abbr> 顺序：

* X 轴 — 指向**前方**；
* Y 轴 — 指向**左侧**；
* Z 轴 — 指向**上方**。

对于在*世界*坐标系中定义的量（相对于空间中的固定点）— <abbr title="East North Up">ENU</abbr>：

* X 轴 — 指向**东方**（条件）；
* Y 轴 — 指向**北方**（条件）；
* Z 轴 — 指向**上方**。

> [!NOTE]
> 对于 ENU 系统，只有轴的相对方向很重要。如果可用磁力计，则使用实际的东方和北方，但如果没有 — 则使用任意选择的。

角度和角速率根据数学规则定义：如果朝向坐标原点看，值逆时针增加。坐标系的一般视图：

<img src="img/axes-rotation.svg" alt="坐标系" width="200">

> [!TIP]
> 坐标轴 <i>X</i>、<i>Y</i> 和 <i>Z</i> 通常分别用红色、绿色和蓝色表示。可以通过缩写 <abbr title="Red Green Blue">RGB</abbr> 来记住这一点。

## 向量

<div class="firmware">
	<strong>固件文件：</strong>
	<a href="https://github.com/okalachev/flix/blob/master/flix/vector.h"><code>vector.h</code></a>.<br>
</div>

**向量**是一个简单的几何对象，包含三个值，对应于 *X*、*Y* 和 *Z* 坐标。这些值称为*向量分量*。向量可以描述空间中的点、方向或旋转轴、速度、加速度、角速率和其他物理量。在 Flix 中，向量由 `vector.h` 库中的 `Vector` 对象表示：

```cpp
Vector v(1, 2, 3);
v.x = 5;
v.y = 10;
v.z = 15;
```

> [!TIP]
> 不应混淆几何向量 — <code>vector</code> 和 C++ 标准库中的动态数组 — <code>std::vector</code>。

在固件中，例如，以向量形式表示：

* `acc` 来自加速度计的固有加速度。
* `gyro` — 来自陀螺仪的角速率。
* `rates` — 计算出的飞行器角速率。
* `accBias`, `accScale`, `gyroBias` — IMU 校准参数。

### 向量运算

**向量长度**使用勾股定理计算；在固件中使用 `norm()` 方法：

```cpp
Vector v(3, 4, 5);
float length = v.norm(); // 7.071
```

任何向量都可以使用 `normalize()` 方法转换为**单位向量**（保持方向，但使长度等于 1）：

```cpp
Vector v(3, 4, 5);
v.normalize(); // 0.424, 0.566, 0.707
```

**加法和减法**通过简单的逐分量加法和减法实现。几何上，向量的和表示连接第一个向量起点和第二个向量终点的向量。向量的差表示连接第一个向量终点和第二个向量终点的向量。这便于计算相对位置、总速度和解决其他任务。在代码中，这些操作直观易懂：

```cpp
Vector a(1, 2, 3);
Vector b(4, 5, 6);
Vector sum = a + b; // 5, 7, 9
Vector diff = a - b; // -3, -3, -3
```

**乘以数字** `n` 的操作将向量的长度增加（或减少）`n` 倍（保持方向）：

```cpp
Vector a(1, 2, 3);
Vector b = a * 2; // 2, 4, 6
```

在某些情况下，**逐分量乘法**（或除法）向量很有用。例如，用于将校准系数应用于 IMU 数据。在不同的库中，此操作以不同的方式表示，但在 `vector.h` 库中使用简单的 `*` 和 `/` 符号：

```cpp
acc = acc / accScale;
```

可以使用静态方法 `Vector::angleBetween()` 找到**向量之间的角度**：

```cpp
Vector a(1, 0, 0);
Vector b(0, 1, 0);
float angle = Vector::angleBetween(a, b); // 1.57 (90 度)
```

#### 点积

向量的点积 *(dot product)* 是两个向量的长度与它们之间角度余弦的乘积。在数学中，它用 `·` 符号或向量的连续书写表示。直观上，点积的结果显示两个向量*同向*的程度。

在 Flix 中使用静态方法 `Vector::dot()`：

```cpp
Vector a(1, 2, 3);
Vector b(4, 5, 6);
float dotProduct = Vector::dot(a, b); // 32
```

点积运算可以帮助，例如，计算一个向量在另一个向量上的投影。

#### 叉积

叉积 *(cross product)* 允许找到垂直于其他两个向量的向量。在数学中，它用 `×` 符号表示，在固件中使用静态方法 `Vector::cross()`：

```cpp
Vector a(1, 2, 3);
Vector b(4, 5, 6);
Vector crossProduct = Vector::cross(a, b); // -3, 6, -3
```

## 四元数

### 三维空间中的方向

与位置和速度不同，三维空间中的方向没有适用于所有情况的通用表示方法。根据任务，方向可以表示为*欧拉角*、*旋转矩阵*、*旋转向量*或*四元数*。让我们考虑飞行固件中使用的方向表示方法。

### 欧拉角

**欧拉角** — *横滚*、*俯仰*和*偏航* — 是对人类来说最"自然"的方向表示方法。它们描述了围绕三个坐标轴的对象的连续旋转。

在固件中，欧拉角保存在普通的 `Vector` 对象中（虽然严格来说不是向量）：

* 横滚角 *(roll)* — `vector.x`。
* 俯仰角 *(pitch)* — `vector.y`。
* 偏航角 *(yaw)* — `vector.z`。

欧拉角的特点：

1. 欧拉角取决于旋转的应用顺序，即存在 6 种类型的欧拉角。Flix 中（以及整个机器人技术中）采用的旋转顺序是偏航、俯仰、横滚（ZYX）。
2. 对于某些方向，欧拉角"退化"。因此，如果对象"严格向下看"，则偏航角和横滚角变得无法区分。这种情况称为*万向节锁* — 失去一个自由度。

由于这些特点，对于欧拉角，不存在用于方向的最基本任务的通用公式，例如将一个旋转（方向）应用于另一个、计算方向之间的差异等。因此，欧拉角主要用于用户界面，但很少用于数学计算。

> [!IMPORTANT]
> 对于欧拉角，不存在用于方向的最基本操作的通用公式。

### 轴角

除了欧拉角，三维空间中的任何方向都可以表示为围绕某个轴旋转某个角度。在几何学中，这被证明为**欧拉旋转定理**。在这种表示中，方向由两个量定义：

* **旋转轴** *(axis)* — 定义旋转轴的单位向量。
* **旋转角度** *(angle* 或 *θ)* — 对象需要围绕该轴旋转的角度。

在 Flix 中，旋转轴由 `Vector` 对象表示，旋转角度由弧度类型的 `float` 数字表示：

```cpp
// 围绕轴 (1, 2, 3) 旋转 45 度
Vector axis(1, 2, 3);
float angle = radians(45);
```

这种方法比欧拉角更便于计算，但仍然不是最优的。

### 旋转向量

如果将向量 *axis* 乘以旋转角度 *θ*，则得到**旋转向量** *(rotation vector)*。该向量在飞行器方向控制算法中起着重要作用。

旋转向量具有一个了不起的属性：如果对象的角速率（在自身坐标系中）在每个时刻都与该向量的分量匹配，则在单位时间内对象将到达该向量指定的方向。此属性允许使用旋转向量通过控制角速率来控制对象的方向。

> [!IMPORTANT]
> 要在单位时间内到达指定方向，对象的固有角速率必须等于旋转向量的分量。

在 Flix 中，旋转向量以 `Vector` 对象的形式表示：

```cpp
// 围绕轴 (1, 2, 3) 旋转 45 度
Vector rotation = radians(45) * Vector(1, 2, 3);
```

### 四元数

<div class="firmware">
	<strong>固件文件：</strong>
	<a href="https://github.com/okalachev/flix/blob/master/flix/quaternion.h"><code>quaternion.h</code></a>.<br>
</div>

旋转向量很方便，但使用**四元数**更方便。在 Flix 中，四元数由 `quaternion.h` 库中的 `Quaternion` 对象表示。四元数由四个值组成：*w*、*x*、*y*、*z*，并根据旋转轴向量 *(axis)* 和旋转角度 *(θ)* 按以下公式计算：

\\[ q = \left( \begin{array}{c} w \\\\ x \\\\ y \\\\ z \end{array} \right) = \left( \begin{array}{c} \cos\left(\frac{\theta}{2}\right) \\\\ axis\_x \cdot \sin\left(\frac{\theta}{2}\right) \\\\ axis\_y \cdot \sin\left(\frac{\theta}{2}\right) \\\\ axis\_z \cdot \sin\left(\frac{\theta}{2}\right) \end{array} \right) \\]

在实践中，事实证明，**正是这种表示方法最便于数学计算**。

让我们在交互式可视化中说明四元数和上述方向表示方法。使用滑块更改旋转角度 *θ*（旋转轴是常数），并研究对象方向、旋转向量和四元数如何变化：

<div id="rotation-diagram" class="diagram">
	<p>
		<label class="angle" for="angle-range"></label>
		<input type="range" name="angle" id="angle-range" min="0" max="360" value="0" step="1">
	</p>
	<p class="axis"></p>
	<p class="rotation-vector"></p>
	<p class="quaternion"></p>
	<p class="euler"></p>
</div>

<script type="importmap">
{
	"imports": {
		"three": "https://cdn.jsdelivr.net/npm/three@0.176.0/build/three.module.js",
		"three/addons/": "https://cdn.jsdelivr.net/npm/three@0.176.0/examples/jsm/"
	}
}
</script>
<script type="module" src="js/rotation.js"></script>

> [!IMPORTANT]
> 在控制算法的背景下，四元数是旋转向量的针对计算优化的类似物。

四元数是算法中最常用的方向表示方法。此外，四元数在数论和代数中具有很大意义，作为复数概念的扩展，但从实际角度考虑旋转方面超出了此描述的范围。

在固件中，例如，以四元数形式表示：

* `attitude` — 四旋翼飞行器的当前方向。
* `attitudeTarget` — 四旋翼飞行器的目标方向。

### 四元数运算

四元数直接从其四个分量创建：

```cpp
// 表示零（初始）方向的四元数
Quaternion q(1, 0, 0, 0);
```

可以从旋转轴和旋转角度、旋转向量或欧拉角创建四元数：

```cpp
Quaternion q1 = Quaternion::fromAxisAngle(axis, angle);
Quaternion q2 = Quaternion::fromRotationVector(rotation);
Quaternion q3 = Quaternion::fromEuler(Vector(roll, pitch, yaw));
```

反之亦然：

```cpp
q1.toAxisAngle(axis, angle);
Vector rotation = q2.toRotationVector();
Vector euler = q3.toEuler();
```

可以计算两个普通向量之间的旋转：

```cpp
Quaternion q = Quaternion::fromBetweenVectors(v1, v2); // 以四元数形式
Vector rotation = Vector::rotationVectorBetween(v1, v2); // 以旋转向量形式
```

用于处理偏航欧拉角的快捷方式（便于飞行控制算法）：

```cpp
float yaw = q.getYaw();
q.setYaw(yaw);
```

#### 应用旋转
