using CPUSetSetter.Config.Models;
using CPUSetSetter.UI.Tabs.Processes;
using Microsoft.Win32;
using System.Diagnostics;
using System.Windows;


namespace CPUSetSetter.Platforms
{
    /// <summary>
    /// Windows Game Mode is abysmal to gaming performance when combined with CPU Set Setter.
    /// Warn the user, and encourage them to turn it off, or experiment with it on.
    /// </summary>
    public static class WindowsGameModeWarning
    {
        public static void ShowIfEnabled()
        {
            if (!GameModeEnabled())
                return;

            WindowLogger.Write("警告：Windows 游戏模式已启用，可能严重影响游戏性能和稳定性，" +
                "尤其是在同时使用 CPU Set Setter 时。");

            if (AppConfig.Instance.ShowGameModePopup)
            {
                App.Current.Dispatcher.InvokeAsync(() =>
                {
                    MessageBoxResult result = MessageBox.Show(
                        "Windows 游戏模式当前已启用。\n" +
                        "在 AMD CPU 上，游戏模式已知可能与 CPU Set Setter 冲突，导致帧率下降或游戏崩溃。\n" +
                        "Intel CPU 是否受影响尚不明确，欢迎在 GitHub 上反馈测试结果！\n\n" +
                        "是否打开游戏模式设置页面？\n\n" +
                        "（可在设置选项卡中禁用此提示）",
                        "CPU Set Setter：Windows 游戏模式警告",
                        MessageBoxButton.YesNo,
                        MessageBoxImage.Warning);

                    if (result == MessageBoxResult.Yes)
                    {
                        OpenGameModeSettings();
                    }
                });
            }
        }

        private static bool GameModeEnabled()
        {
            using RegistryKey? gameBarKey = Registry.CurrentUser.OpenSubKey(@"Software\Microsoft\GameBar");
            if (gameBarKey is null)
                return false;

            object? gameModeValue = gameBarKey.GetValue("AutoGameModeEnabled");
            if (gameModeValue is int value)
                return value != 0;

            return false;
        }

        private static void OpenGameModeSettings()
        {
            Process.Start(new ProcessStartInfo { FileName = "ms-settings:gaming-gamemode", UseShellExecute = true });
        }
    }
}
