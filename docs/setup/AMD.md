# AMD 处理器配置

## Ryzen 9 X3D 的前置设置

本节仅适用于 9950X3D、9900X3D、7950X3D、7900X3D 等 Ryzen 9 X3D 处理器。其他 AMD 处理器可跳过本节。

以下为上游强烈推荐的设置，并非软件运行的硬性要求：

- BIOS：Global C-State Control（全局 C 状态控制）：启用。
- BIOS：X3D Gaming/Turbo Mode（X3D 游戏/加速模式）：禁用，以确保所有核心可用。
- BIOS：CPPC Preferred Cores（CPPC 首选核心）：Driver（驱动程序）或 Frequency（频率），让 Windows 优先使用高频核心，为手动分配的游戏保留大缓存核心。
- Windows 设置 > 游戏 > 游戏模式：关闭。

> [!CAUTION]
> Ryzen 9 X3D 使用 CPU Set Setter 为游戏分配核心时，上游建议始终关闭 Windows 游戏模式，即使 CPPC 设置为 Frequency。游戏模式可能与本工具冲突，导致性能下降甚至游戏崩溃。

## 安装和使用

1. 在[本仓库发行页面](https://github.com/yukaichao-ai/CPUSetSetter_zh/releases)下载可用的安装程序或 ZIP 压缩包，安装或解压后运行。如果尚无中文版发行包，可查看[上游发行页面](https://github.com/SimonvBez/CPUSetSetter/releases/latest)（英文版）。
2. 如有提示，安装 .NET 10 桌面运行时，再次启动软件。
3. 打开「进程」选项卡。
4. 为正在运行的游戏选择 Cache 或 CCD0 掩码。部分处理器或游戏可能更适合 CCD1，建议实测。
5. （可选）为 OBS、iCue、浏览器等后台应用分配另一个 CCD（Freq 或 CCD1）。
6. 设置会自动保存，只要软件运行，下次启动目标程序就会自动应用。
7. （可选）在「核心掩码」选项卡为掩码设置快捷键，无需切出游戏即可切换或清除掩码。
8. （可选）在「设置」中启用「开机自启动」。

> [!NOTE]
> 软件会根据 CPU 自动创建默认掩码，例如 `CCD0`、`CCD1`、`Cache`、`Cache no SMT`、`Freq`、`Freq no SMT`、`All no SMT`。默认掩码名称保留英文以兼容已有配置。
>
> Windows 10 不支持本工具的自动 CCD 检测，需要在「核心掩码」中手动新建并选择对应核心。上游建议使用 Windows 11，参见[性能对比](https://www.youtube.com/watch?v=32lBRYknKgA)。
