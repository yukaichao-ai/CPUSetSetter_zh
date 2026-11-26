# Intel 处理器配置

## 安装和使用

1. 在[本仓库发行页面](https://github.com/yukaichao-ai/CPUSetSetter_zh/releases)下载可用安装程序或 ZIP 压缩包。若尚无中文版发行包，可查看[上游发行页面](https://github.com/SimonvBez/CPUSetSetter/releases/latest)（英文版）。
2. 如有提示，安装 .NET 10 桌面运行时，再次启动软件。
3. 打开「进程」选项卡。
4. 为正在运行的游戏选择 P-Cores（性能核心）掩码。
5. （可选）将 OBS、iCue、浏览器等后台应用分配至 E-Cores（能效核心）。
6. 设置会自动保存，只要软件运行，下次启动目标程序就会自动应用。
7. （可选）在「核心掩码」选项卡为掩码设置快捷键，无需切出游戏即可切换或清除掩码。
8. （可选）在「设置」中启用「开机自启动」。

> [!NOTE]
> 软件会根据 CPU 自动创建默认掩码，例如 `P-Cores`、`P-Cores no HT`、`E-Cores`、`All no HT`。默认掩码名称保留英文以兼容已有配置。
>
> 如果 Intel CPU 没有性能核心与能效核心之分，则仅自动创建 `All no HT` 掩码。
