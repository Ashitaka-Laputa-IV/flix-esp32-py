# 日志分析

Flix 四旋翼飞行器使用 RAM 存储飞行日志数据。默认日志容量为 100 Hz 下 10 秒。此配置可以在 `log.ino` 文件中调整。

要执行日志分析，您需要下载飞行日志。为此，请确保您通过 Wi-Fi 连接到飞行器并运行以下命令：

```bash
make log
```

日志存储在 `tools/log/*.csv` 文件中。

## 分析

### PlotJuggler

日志分析的推荐工具是 PlotJuggler。

<img src="img/plotjuggler.png" width="500">

1. 使用[官方说明](https://github.com/facontidavide/PlotJuggler?tab=readme-ov-file#installation)安装 PlotJuggler。

2. 运行 PlotJuggler 并将下载的日志文件拖放到那里。选择 `t` 列用作 X 轴。

   您可以使用以下命令打开最近下载的文件：

   ```bash
   make plot
   ```

   您可以使用一个命令同时执行日志下载和运行 PlotJuggler：

   ```bash
   make log plot
   ```

### FlightPlot

FlightPlot 是一个用于分析 [ULog 格式](https://docs.px4.io/main/en/dev_log/ulog_file_format.html)日志的强大工具。此格式用于 PX4 和 ArduPilot 飞行软件。

<img src="img/flightplot.png" width="500">

1. [安装 FlightPlot](https://github.com/PX4/FlightPlot)。
2. Flix 仓库包含一个将 CSV 日志转换为 ULog 格式的工具。使用[说明](../tools/csv_to_ulog/README.md)构建工具并转换您要分析的日志。
3. 运行 FlightPlot 并将转换后的 ULog 文件拖放到那里。

### Foxglove Studio

Foxglove 是一个用于可视化和分析机器人数据的工具，具有非常丰富的功能。它可以导入各种格式，但主要关注自己的格式，称为 [MCAP](https://mcap.dev)。

<img src="img/foxglove.png" width="500">

1. 从[官方网站](https://foxglove.dev/download)安装 Foxglove Studio。

2. Flix 仓库包含一个将 CSV 日志转换为 MCAP 格式的工具。首先，安装其依赖项：

   ```bash
   cd tools
   pip install -r requirements.txt
   ```

3. 转换您要分析的日志：

   ```bash
   csv_to_mcap.py log_file.csv
   ```

4. 使用*打开本地文件*命令在 Foxglove Studio 中打开日志。
