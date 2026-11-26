using CommunityToolkit.Mvvm.ComponentModel;
using CPUSetSetter.Config.Models;
using CPUSetSetter.UI.Tabs.Processes;
using System.Diagnostics;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Reflection;
using System.Text.Json;
using System.Windows;


namespace CPUSetSetter.Util
{
    /// <summary>
    /// Check for a new GitHub Release on every app start, and once every 24 hours (for those no-reboot monkeys out there)
    /// </summary>
    public partial class VersionChecker : ObservableObject
    {
        public static VersionChecker Instance { get; } = new();

        // The app version is only set in Releases. During development it will be the default 1.0.0.0
        private static Version DevVersion => new(1, 0, 0, 0);

        [ObservableProperty]
        private bool _newVersionAvailable;

        [ObservableProperty]
        private string _versionCheckState = "尚未检查版本";

        public Version? AppVersion { get; } = Assembly.GetEntryAssembly()?.GetName().Version;

        public string VersionString
        {
            get
            {
                if (AppVersion is not null)
                {
                    if (AppVersion == DevVersion)
                        return "开发版";
                    return $"v{AppVersion}";
                }
                return "未知";
            }
        }

        public VersionChecker() { }

        public void RunVersionChecker()
        {
            if (AppVersion is not null)
            {
                if (AppVersion == DevVersion)
                    VersionCheckState = "版本检查已禁用（开发版）";
                else
                    Task.Run(RunUpdateChecker); // Only run the update checker when this app is properly versioned
            }
        }

        public static void OpenLatestReleasePage()
        {
            Process.Start(new ProcessStartInfo { FileName = "https://github.com/yukaichao-ai/CPUSetSetter_zh/releases/latest", UseShellExecute = true });
        }

        partial void OnNewVersionAvailableChanged(bool value)
        {
            if (!value)
                return;

            WindowLogger.Write("GitHub 上有新版 CPU Set Setter 中文版！");

            if (AppConfig.Instance.ShowUpdatePopup)
            {
                App.Current.Dispatcher.InvokeAsync(() =>
                {
                    MessageBoxResult result = MessageBox.Show(
                        "CPU Set Setter 中文版有新版本！\n" +
                        "是否立即打开发行页面？\n" +
                        "（目前不支持自动更新）\n\n" +
                        "（可在设置选项卡中禁用此提示）",
                        "CPU Set Setter 有可用更新",
                        MessageBoxButton.YesNo,
                        MessageBoxImage.Information);

                    if (result == MessageBoxResult.Yes)
                    {
                        OpenLatestReleasePage();
                    }
                });
            }
        }

        private async Task RunUpdateChecker()
        {
            while (true)
            {
                TimeSpan nextRetry;
                try
                {
                    string latestReleaseTag = await GetLatestReleaseTag();
                    if (latestReleaseTag.StartsWith('v'))
                    {
                        Version latestVersion = new(latestReleaseTag[1..]);
                        if (latestVersion > AppVersion!)
                        {
                            NewVersionAvailable = true;
                            VersionCheckState = $"有新版本可用！ ({latestReleaseTag})";
                            return;
                        }
                        VersionCheckState = "当前已是最新版本";
                        nextRetry = TimeSpan.FromHours(24); // No update available. Check again the next day
                    }
                    else
                    {
                        // A response was received, but not in the "vx.x.x" format like expected
                        VersionCheckState = "无法解析最新版本";
                        return;
                    }
                }
                catch (HttpRequestException)
                {
                    // Failed to reach GitHub, assume internet is down and try again soon
                    VersionCheckState = "版本检查失败";
                    nextRetry = TimeSpan.FromSeconds(60);
                }
                catch (Exception)
                {
                    // Any other exception (probably NoSuccessResponseException), assume GitHub doesn't want a request for a while
                    VersionCheckState = "版本检查失败";
                    nextRetry = TimeSpan.FromHours(24);
                }

                await Task.Delay(nextRetry);
            }
        }

        private static async Task<string> GetLatestReleaseTag()
        {
            using HttpClient client = new();

            // GitHub API requires a User-Agent header
            client.DefaultRequestHeaders.UserAgent.Add(
                new ProductInfoHeaderValue("CPUSetSetterUpdateChecker", "1.0"));

            string url = "https://api.github.com/repos/yukaichao-ai/CPUSetSetter_zh/releases/latest";

            var response = await client.GetAsync(url);
            try
            {
                response.EnsureSuccessStatusCode();
            }
            catch (HttpRequestException)
            {
                throw new NoSuccessResponseException();
            }

            string json = await response.Content.ReadAsStringAsync();

            using var doc = JsonDocument.Parse(json);
            var root = doc.RootElement;

            if (root.TryGetProperty("tag_name", out JsonElement tagElement))
            {
                return tagElement.GetString() ?? throw new NullReferenceException();
            }

            throw new KeyNotFoundException("版本接口返回的数据中缺少 tag_name 字段。");
        }

        private class NoSuccessResponseException : Exception { }
    }
}
