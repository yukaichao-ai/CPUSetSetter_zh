# CPU Set Setter 中文版

[![自动构建](https://github.com/yukaichao-ai/CPUSetSetter_zh/actions/workflows/build_preview_from_branch.yml/badge.svg)](https://github.com/yukaichao-ai/CPUSetSetter_zh/actions/workflows/build_preview_from_branch.yml)
[![上游同步](https://github.com/yukaichao-ai/CPUSetSetter_zh/actions/workflows/sync_upstream.yml/badge.svg)](https://github.com/yukaichao-ai/CPUSetSetter_zh/actions/workflows/sync_upstream.yml)

<p align=center>
    <img height="75" src="Images/Logo.png">
</p>

为游戏和应用程序分配合适的 CPU 核心，改善 AMD 多 CCD 和 Intel 混合架构处理器的运行表现。

## 系统要求

- Windows 10 或更高版本
- .NET Desktop Runtime 10（按程序提示安装）

## 功能介绍

Windows 会自动调度任务，但调度结果不一定最优。CPU Set Setter 可以指定游戏和应用程序使用哪些 CPU 核心，免费提供 CPU 集（CPU Sets）设置功能。

### AMD Ryzen 多 CCD 分配

对于双 CCD 处理器，尤其是 Ryzen 9 X3D 系列，可尝试将游戏限制在单个 CCD 上，将直播、渲染等后台任务分配至另一个 CCD，减少资源竞争，而不必停用整个 CCD。

### Intel 性能核心分配

对于第 12 代及更新的混合架构 Intel 处理器，可将游戏分配至性能核心（P-Core），并将后台应用分配至能效核心（E-Core）。

### 软件级限制 SMT / 超线程

通过掩码选择每个物理核心的一个逻辑处理器，可以在不全局关闭 SMT 或超线程的情况下，限制指定程序使用的逻辑处理器。实际性能收益因应用而异。

## 快捷键与自动规则

- 在进程选项卡为运行中的程序选择核心掩码。
- 在核心掩码选项卡创建自定义掩码并设置快捷键。
- 在规则选项卡设置程序规则和路径通配符模板。
- 只要 CPU Set Setter 正在运行，已保存的规则就会自动应用。
- 可通过快捷键在游戏运行时切换掩码，比较实际性能。

## 安装与配置（重要）

- [AMD 处理器配置教程](docs/setup/AMD.md)
- [Intel 处理器配置教程](docs/setup/Intel.md)

[本仓库发行页面](https://github.com/yukaichao-ai/CPUSetSetter_zh/releases)

## 自动构建与上游同步

- 每次向 `main` 提交代码或创建指向 `main` 的 PR，自动构建 Windows x64 版本。可在 [Build Preview](https://github.com/yukaichao-ai/CPUSetSetter_zh/actions/workflows/build_preview_from_branch.yml) 的成功运行页面下载普通版和内置 .NET 10 运行时版，预览包保留 14 天。
- 每天北京时间 **04:17** 检查 `SimonvBez/CPUSetSetter:main`。上游更新先合并到本仓库的同步分支，创建本仓库 PR，并构建该确切提交；没有冲突且构建通过后，自动合入本仓库 `main`。
- 同步方向仅为 **上游 → 本项目**。所有推送、PR 和问题记录都在 `yukaichao-ai/CPUSetSetter_zh`；不会回推上游。合并保留已有中文化，新增英文文本仍需后续翻译。
- 冲突、构建失败或上游工作流修改会暂停自动合入，保留 PR 或生成本仓库跟踪 Issue。
- 推送 `v1.2.3` / `v1.2.3.1` 形式的标签时自动打包并发布 Release；定时同步不会复制或推送上游标签。

手动运行、下载产物及处理冲突的方法见 [自动化维护说明](docs/AUTOMATION.md)。

## 界面截图

以下为上游原版界面截图，中文版本的截图尚未更新。

![](Images/ProcessesTab.png)

![](Images/MasksTab.png)

![](Images/RulesTab.png)

## CPU 集与处理器亲和性的区别

- **处理器亲和性（Affinity）**：较严格的核心限制，部分游戏可能卡死或崩溃。
- **CPU 集（CPU Sets）**：向系统提供较强的调度约束，必要时系统仍可能调整，通常兼容性较好。
- CPU 集设置通常需要较少的进程访问权限，但不保证与所有反作弊程序兼容。

## 上游相关视频

<a href="https://www.youtube.com/watch?v=m3YVDB0Ymi8"><img src="https://img.youtube.com/vi/m3YVDB0Ymi8/hq720.jpg" width="325" alt="免费 CPU 调度工具介绍"/></a>
<a href="https://www.youtube.com/watch?v=jZXNo-Xu1TY"><img src="https://img.youtube.com/vi/jZXNo-Xu1TY/hq720.jpg" width="325" alt="CPU Set Setter 性能测试"/></a>

## 原作者与许可证

本项目为 [SimonvBez/CPUSetSetter](https://github.com/SimonvBez/CPUSetSetter) 的简体中文版本，保留原项目 MIT 许可证及版权声明。

原作者提供免费开源软件，不设置付费专属功能或广告。如希望支持原作者，可通过 [GitHub Sponsors](https://github.com/sponsors/SimonvBez) 或 [PayPal](https://paypal.me/SimonvBez) 自愿捐赠。
