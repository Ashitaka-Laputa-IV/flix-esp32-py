# 开发指南

本文档介绍如何为 flix-mpy 项目贡献代码和进行二次开发。

## 开发环境设置

### 必需工具

1. **Python 3.x** - 用于运行工具脚本
2. **MicroPython** - 目标运行环境
3. **代码编辑器** - 推荐 VS Code 或 Thonny

### 推荐的 VS Code 扩展

- MicroPico - MicroPython 开发支持
- Python - Python 语言支持

### 克隆仓库

```bash
git clone https://github.com/okalachev/flix.git
cd flix/flix-mpy
```

## 代码风格

### 命名约定

| 类型 | 约定 | 示例 |
|------|------|------|
| 模块 | 小写下划线 | `control.py` |
| 类 | 大驼峰 | `LowPassFilter` |
| 函数 | 小写下划线 | `estimate_attitude()` |
| 变量 | 小写下划线 | `rates_target` |
| 常量 | 大写下划线 | `MOTOR_FRONT_LEFT` |
| 私有变量 | 前置下划线 | `_params` |
| 私有函数 | 前置下划线 | `_apply_param()` |

### 文档字符串

使用三引号文档字符串描述模块和函数：

```python
def control():
    """
    执行飞行控制循环。
    
    包括姿态控制、角速度控制和扭矩混合。
    """
    pass
```

### 导入顺序

1. 标准库
2. 第三方库
3. 本地模块

```python
import math
import time

from machine import Pin, I2C

from lib.vector import Vector
from lib.util import constrain
```

## 模块结构

### 典型模块模板

```python
"""
模块说明文档字符串
"""

# 导入
import math
from lib.vector import Vector

# 常量
MY_CONSTANT = 42

# 全局变量
_my_variable = 0.0

# 公开变量
public_var = None

# 私有函数
def _helper_function():
    pass

# 公开函数
def setup():
    """初始化模块"""
    pass

def main_function():
    """主要功能"""
    pass
```

## 添加新模块

### 1. 创建模块文件

在 `lib/` 目录下创建新文件，例如 `lib/my_module.py`：

```python
"""
我的新模块

模块功能描述。
"""

# 模块代码
_my_state = 0

def setup():
    """初始化"""
    global _my_state
    _my_state = 0

def process():
    """处理函数"""
    pass
```

### 2. 在 main.py 中集成

```python
# 在 setup() 中添加初始化
from lib import my_module
my_module.setup()

# 在 loop() 中添加调用
my_module.process()
```

### 3. 添加参数（如需要）

在 `lib/parameters.py` 中：

```python
# 在 _init_defaults() 中添加
from .my_module import my_param

_default_params = {
    # ...
    'MY_PARAM': my_param,
}

# 在 _apply_param() 中添加
if name == 'MY_PARAM':
    my_module.my_param = value
```

## 添加新命令

在 `lib/cli.py` 中添加新命令：

```python
def do_command(cmd, args):
    # 添加新命令处理
    if cmd == 'mycommand':
        # 处理命令
        print("执行我的命令")
        return
    
    # 现有命令...
```

## 添加新参数

### 1. 在模块中定义参数变量

```python
# lib/my_module.py
my_param = 1.0
```

### 2. 在 parameters.py 中注册

```python
# _init_defaults()
from .my_module import my_param
_default_params['MY_PARAM'] = my_param

# _apply_param()
if name == 'MY_PARAM':
    my_module.my_param = value
```

### 3. 使用参数

```python
from lib import parameters
value = parameters.get('MY_PARAM')
```

## 添加新飞行模式

### 1. 定义模式常量

```python
# lib/control.py
MY_MODE = 4
```

### 2. 实现模式逻辑

```python
def _interpret_controls():
    # 添加新模式处理
    if mode == MY_MODE:
        # 实现控制逻辑
        pass
```

### 3. 添加模式切换

在 `_interpret_controls()` 中处理模式切换。

## 调试技巧

### 使用 REPL 调试

```python
# 在 REPL 中
import main
main.setup()

# 检查状态
print(main.gyro)
print(main.attitude.to_euler())

# 单步执行
main.loop()
```

### 添加调试输出

```python
# 临时调试
print(f"Debug: rates = {rates.x}, {rates.y}, {rates.z}")

# 使用条件输出
DEBUG = True
if DEBUG:
    print(f"Debug info: {value}")
```

### 检查循环频率

```python
import main
print(f"Loop rate: {main.loop_rate} Hz")
```

## 性能优化

### 避免在循环中创建对象

```python
# 不好 - 每次循环创建新对象
def loop():
    v = Vector(0, 0, 0)  # 避免！

# 好 - 重用对象
_v = Vector()  # 模块级变量

def loop():
    _v.x, _v.y, _v.z = 0, 0, 0
```

### 使用 `__slots__`

```python
class MyClass:
    __slots__ = ['x', 'y', 'z']
    def __init__(self):
        self.x = 0
        self.y = 0
        self.z = 0
```

### 延迟导入

```python
# 在函数内导入，减少启动时间
def my_function():
    from lib import heavy_module
    heavy_module.do_something()
```

### 使用频率控制

```python
from lib.util import Rate

# 只在需要时执行
_slow_rate = Rate(10)  # 10 Hz

def loop():
    if _slow_rate.check(main.t):
        # 低频任务
        pass
```

## 测试

### 单元测试

创建测试文件 `test_my_module.py`：

```python
from lib import my_module

def test_setup():
    my_module.setup()
    assert my_module.some_value == 0

def test_function():
    result = my_module.my_function()
    assert result is not None

# 运行测试
test_setup()
test_function()
print("All tests passed!")
```

### 硬件测试

1. 使用 `motor test` 命令测试电机
2. 使用 `imu` 命令检查传感器
3. 使用 `status` 命令查看系统状态

## 发布检查清单

- [ ] 代码风格一致
- [ ] 所有函数有文档字符串
- [ ] 参数已正确注册
- [ ] 新功能有使用说明
- [ ] 测试通过
- [ ] README 已更新

## 贡献指南

1. Fork 仓库
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

### 提交消息格式

```
类型: 简短描述

详细描述（可选）

类型: feat, fix, docs, style, refactor, test, chore
```

示例：
```
feat: 添加 GPS 支持模块

- 实现 NMEA 解析
- 添加位置估计
- 支持 MAVLink GPS 消息
```
