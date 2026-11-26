# 自动构建与上游同步

本项目的自动化由 GitHub Actions 运行。所有写入限定在 `yukaichao-ai/CPUSetSetter_zh`，上游 `SimonvBez/CPUSetSetter` 只用于读取更新。

## 构建与下载

| 工作流 | 触发方式 | 结果 |
| --- | --- | --- |
| [Build Preview](https://github.com/yukaichao-ai/CPUSetSetter_zh/actions/workflows/build_preview_from_branch.yml) | 提交到 `main`、指向 `main` 的 PR、手动运行 | Windows x64 普通版和内置运行时版 |
| [Build and Release](https://github.com/yukaichao-ai/CPUSetSetter_zh/actions/workflows/build_and_release.yml) | 推送 `v*` 标签、手动选择已有标签 | 构建上述 ZIP、安装程序并发布 GitHub Release |
| [Sync Upstream](https://github.com/yukaichao-ai/CPUSetSetter_zh/actions/workflows/sync_upstream.yml) | 每天北京时间 04:17、手动运行、修改同步配置 | 检测、合并、构建并应用上游更新 |

构建统一使用 .NET 10 SDK。到成功运行页面的 **Artifacts** 区域下载构建产物，解压后包含：

- `CPUSetSetter_zh_win-x64.zip`：需要安装 .NET 10 Desktop Runtime 的普通版。
- `CPUSetSetter_zh_win-x64_net10_included.zip`：内置运行时版，无需另行安装 .NET。
- `SOURCE.txt`：实际构建的源码提交链接。
- `SHA256SUMS.txt`：文件 SHA-256 校验值。

ZIP 包附带项目许可证及第三方许可证。预览产物保留 **14 天**；正式发布文件保存在 [Releases](https://github.com/yukaichao-ai/CPUSetSetter_zh/releases)。自动构建验证编译与打包，不等同于在各类 CPU 和游戏上完成运行测试。

### 手动构建

打开 **Actions → Build Preview → Run workflow**，在 `branch_name` 中填写分支、标签或提交 SHA。通常使用 `main`；需要复现历史构建时使用完整提交 SHA。

### 发布正式版本

发布标签必须为 `vX.Y.Z` 或 `vX.Y.Z.N`，例如 `v1.2.3.1`。请为中文发行版选择尚未使用的版本号：

```bash
git tag v1.2.3.1 <要发布的提交SHA>
git push origin v1.2.3.1
```

也可以在 **Build and Release → Run workflow** 中选择已经存在的标签并填写发行说明。工作流构建标签对应的源码；手动指定不存在的标签会失败。发布工作流只有上传 Release 的最后一个作业拥有写权限。

## 上游更新如何合入

1. 获取本项目 `main` 与上游 `main` 的完整提交历史，不同步上游标签。
2. 已包含全部上游提交时结束，不创建空提交或重复 PR。
3. 在 `automation/sync-upstream` 中正常合并本项目和上游的提交。已有人工修复会保留；不使用强制推送覆盖分支。
4. 创建或更新**本仓库**的同步 PR，直接调用 Windows 构建工作流验证候选提交。无需个人访问令牌，也不依赖机器人 PR 自动触发构建。
5. 只有构建成功、产物上传成功、候选分支未被改动且 `main` 能快进到已构建提交时，才合入本项目 `main`。普通推送会拒绝覆盖并行提交。

同步保留 Git 提交历史及未冲突的中文化改动。上游新增的界面文本可能仍是英文，需要继续翻译。同步后的产物在当次 **Sync Upstream** 运行中下载；它已经构建过合入的确切提交，不依赖后续再触发一次 Build Preview。

定时器使用 UTC `17 20 * * *`，对应北京时间次日 04:17。GitHub 的定时执行可能延迟。可随时使用 **Sync Upstream → Run workflow** 立即检查。

## 需要人工处理的情况

| 情况 | 自动化行为 | 处理方式 |
| --- | --- | --- |
| 源码合并冲突 | 撤销此次本地合并，主分支与已有同步分支保持原样，更新同一条跟踪 Issue | 根据 Issue 列出的文件保留中文化并解决冲突 |
| Windows 构建或打包失败 | 保留本仓库同步 PR，不修改 `main` | 修复同步分支后重新运行 Sync Upstream |
| 构建期间 `main` 或同步分支被更新 | 拒绝合入未经验证的提交 | 重新运行 Sync Upstream，合并最新改动后再次构建 |
| 上游修改 `.github/workflows` 或同步脚本 | 更新跟踪 Issue，暂停该批更新 | 人工审核自动化配置并合并；内置令牌不能任意更新工作流文件 |
| 仓库规则禁止自动写入 | 工作流明确失败并保留已有内容 | 检查运行日志与仓库规则，按仓库要求通过 PR 合入 |

手工处理同步 PR 时，请使用 **Create a merge commit**，保留上游提交关系；不要 squash 或 rebase 掉这段历史，否则后续检测可能再次把同一批上游提交列为待同步。

如果冲突发生在创建同步 PR 之前，可以从本项目的 `main` 新建分支，在本地合并上游并解决冲突，再将分支推送到自己的项目并创建 PR。确保 `origin` 指向 `https://github.com/yukaichao-ai/CPUSetSetter_zh.git`；不要向 `upstream` 推送。

## 仓库设置

- GitHub Actions 需启用。
- **Settings → Actions → General → Workflow permissions → Allow GitHub Actions to create and approve pull requests** 需勾选。默认权限可以继续保持只读，具体作业在 YAML 中声明需要的权限。
- **Settings → General → Features → Issues** 需开启，用于记录冲突和需要人工审核的更新。
- 不需要新增 PAT 或其他长期密钥，使用 GitHub 自动提供的 `GITHUB_TOKEN`。
- 如需暂停自动同步，在 Actions 页面选择 **Sync Upstream → Disable workflow**；恢复时选择 **Enable workflow**。

公开仓库连续 60 天没有活动时，GitHub 可能停用定时工作流。恢复维护时请检查工作流是否启用，并手动运行一次。

相关 GitHub 官方说明：[令牌与工作流触发](https://docs.github.com/en/actions/concepts/security/github_token)、[仓库 Actions 权限](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository)、[启用与停用工作流](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/disable-and-enable-workflows)。
