#!/usr/bin/env python3
"""Prepare an upstream merge in this fork; never write to the upstream repository."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request


REPOSITORY = "yukaichao-ai/CPUSetSetter_zh"
UPSTREAM = "SimonvBez/CPUSetSetter"
BASE_BRANCH = "main"
SYNC_BRANCH = "automation/sync-upstream"
ORIGIN_URL = f"https://github.com/{REPOSITORY}.git"
UPSTREAM_URL = f"https://github.com/{UPSTREAM}.git"
ISSUE_MARKER = "<!-- cpusetsetter-upstream-sync -->"
PR_MARKER = "<!-- cpusetsetter-upstream-pr -->"


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", *args], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    if check and result.returncode:
        raise RuntimeError(f"git {args[0]} 失败：{result.stderr.strip() or result.stdout.strip()}")
    return result


def sha(ref: str) -> str:
    return git("rev-parse", "--verify", f"{ref}^{{commit}}").stdout.strip()


def is_ancestor(older: str, newer: str) -> bool:
    result = git("merge-base", "--is-ancestor", older, newer, check=False)
    if result.returncode not in (0, 1):
        raise RuntimeError(f"无法判断提交关系：{result.stderr.strip()}")
    return result.returncode == 0


def output(name: str, value: str) -> None:
    if "\n" in value or "\r" in value:
        raise ValueError("工作流输出必须是单行文本")
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as stream:
            stream.write(f"{name}={value}\n")


def summary(message: str) -> None:
    print(message)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as stream:
            stream.write(message + "\n\n")


class RepositoryAPI:
    """All API reads and writes are confined to the explicitly named fork."""

    def __init__(self, token: str):
        self.token = token

    def request(self, suffix: str, method: str = "GET", data: dict | None = None):
        if suffix.startswith("/") or "://" in suffix or ".." in suffix:
            raise ValueError("不允许仓库范围之外的 API 路径")
        request = urllib.request.Request(
            f"https://api.github.com/repos/{REPOSITORY}/{suffix}",
            data=json.dumps(data).encode("utf-8") if data is not None else None,
            method=method,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github+json",
                "Content-Type": "application/json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "CPUSetSetter-zh-upstream-sync",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                body = response.read()
                return json.loads(body) if body else None
        except urllib.error.HTTPError as error:
            # Do not log request headers or credentials.
            try:
                message = json.loads(error.read()).get("message", "GitHub API error")
            except (ValueError, AttributeError):
                message = "GitHub API error"
            raise RuntimeError(f"本仓库 GitHub API 返回 HTTP {error.code}：{message}") from None

    def tracking_issue(self):
        page = 1
        while True:
            issues = self.request(f"issues?state=all&per_page=100&page={page}")
            for issue in issues:
                if "pull_request" not in issue and ISSUE_MARKER in (issue.get("body") or ""):
                    return issue
            if len(issues) < 100:
                return None
            page += 1

    def report_problem(self, message: str, base: str, upstream: str) -> None:
        title = "上游同步需要处理"
        body = (
            f"{ISSUE_MARKER}\n\n"
            f"同步方向：`{UPSTREAM}:main` → `{REPOSITORY}:main`。\n\n"
            f"本项目主分支：`{base}`\n\n"
            f"上游提交：https://github.com/{UPSTREAM}/commit/{upstream}\n\n"
            f"{message}\n\n"
            "自动同步已停止，本项目 main 未被本次检测修改。处理后可重新运行 "
            "Actions → Sync Upstream。请保留中文化内容；不要向上游仓库推送。"
        )
        existing = self.tracking_issue()
        if existing:
            # A manually closed, unchanged report stays closed; no daily notification spam.
            if existing.get("body") != body or existing.get("title") != title:
                self.request(
                    f"issues/{existing['number']}", "PATCH",
                    {"title": title, "body": body, "state": "open"},
                )
            url = existing["html_url"]
        else:
            url = self.request("issues", "POST", {"title": title, "body": body})["html_url"]
        summary(f"### 上游同步已停止\n\n{message}\n\n处理记录：{url}")

    def close_resolved_issue(self) -> None:
        issue = self.tracking_issue()
        if issue and issue["state"] == "open":
            self.request(f"issues/{issue['number']}", "PATCH", {"state": "closed"})

    def prepare_pull_request(self, base: str, upstream: str, candidate: str) -> int:
        query = urllib.parse.urlencode({
            "state": "open", "base": BASE_BRANCH,
            "head": f"{REPOSITORY.split('/')[0]}:{SYNC_BRANCH}",
        })
        pulls = self.request(f"pulls?{query}")
        title = "同步上游更新到中文版"
        body = (
            f"{PR_MARKER}\n\n"
            f"将 `{UPSTREAM}:main` 的更新合并到 **本仓库**，保留已有中文化改动。\n\n"
            f"- 上游提交：https://github.com/{UPSTREAM}/commit/{upstream}\n"
            f"- 主分支基线：`{base}`\n"
            f"- 待构建提交：`{candidate}`\n\n"
            "同一轮 Sync Upstream 工作流会构建这个确切提交。构建通过且 main "
            "仍可快进到该提交时，自动合入本仓库 main；构建失败或 main 出现并行更新时，"
            "保留此 PR 等待处理/下一次检查。不会向上游提交 PR 或推送代码。\n\n"
            "如需手工合并，请使用 Create a merge commit，以保留上游提交关系。"
        )
        if pulls:
            pull = pulls[0]
            if pull.get("body") != body or pull["title"] != title:
                self.request(f"pulls/{pull['number']}", "PATCH", {"title": title, "body": body})
        else:
            pull = self.request("pulls", "POST", {
                "base": BASE_BRANCH, "head": SYNC_BRANCH, "title": title, "body": body,
            })
        summary(f"同步 PR（本仓库）：{pull['html_url']}")
        return int(pull["number"])


def workflow_changes(base: str, upstream: str) -> list[str]:
    # Inspect history, not just the final tree: changed-then-reverted workflows matter too.
    result = git(
        "log", "--full-history", "-m", "--format=", "--name-only", f"{base}..{upstream}", "--",
        ".github/workflows", ".github/scripts/sync_upstream.py",
    )
    return sorted(set(line for line in result.stdout.splitlines() if line))


def merge(ref: str) -> list[str]:
    result = git("merge", "--no-ff", "--no-edit", ref, check=False)
    if not result.returncode:
        return []
    conflicts = git("diff", "--name-only", "--diff-filter=U").stdout.splitlines()
    git("merge", "--abort", check=False)
    if not conflicts:
        raise RuntimeError(f"合并失败：{result.stderr.strip() or result.stdout.strip()}")
    return conflicts


def prepare(api: RepositoryAPI) -> None:
    output("should_build", "false")
    if os.environ.get("GITHUB_REPOSITORY") != REPOSITORY:
        raise RuntimeError(f"本工作流只允许在 {REPOSITORY} 中运行")
    if git("status", "--porcelain").stdout.strip():
        raise RuntimeError("工作目录存在未提交改动，停止同步")

    # All fetch/push destinations are fixed, regardless of inherited remote configuration.
    git("remote", "set-url", "origin", ORIGIN_URL)
    if "upstream" not in git("remote").stdout.splitlines():
        git("remote", "add", "upstream", UPSTREAM_URL)
    else:
        git("remote", "set-url", "upstream", UPSTREAM_URL)
    git("remote", "set-url", "--push", "upstream", "DISABLED")
    git("fetch", "--no-tags", "origin", "+refs/heads/main:refs/remotes/origin/main")
    git("fetch", "--no-tags", "upstream", "+refs/heads/main:refs/remotes/upstream/main")
    base = sha("refs/remotes/origin/main")
    upstream = sha("refs/remotes/upstream/main")
    output("base_sha", base)
    output("upstream_sha", upstream)

    if is_ancestor(upstream, base):
        api.close_resolved_issue()
        summary(f"### 已包含全部上游更新\n\n上游：`{upstream}`\n\n本项目：`{base}`\n\n无需创建提交、PR 或构建。")
        return

    changed_workflows = workflow_changes(base, upstream)
    if changed_workflows:
        files = "\n".join(f"- `{path}`" for path in changed_workflows)
        api.report_problem(
            "上游未合入的提交修改了工作流或本项目同步脚本，需要人工审核。"
            "内置 GITHUB_TOKEN 不具备任意修改工作流的权限，因此不会自动推送这一批更新。\n\n"
            + files, base, upstream,
        )
        raise RuntimeError("上游自动化文件更新需要人工审核，未创建同步提交")

    existing = git("ls-remote", "--heads", "origin", f"refs/heads/{SYNC_BRANCH}").stdout.strip()
    start = base
    if existing:
        git("fetch", "--no-tags", "origin", f"+refs/heads/{SYNC_BRANCH}:refs/remotes/origin/{SYNC_BRANCH}")
        branch_sha = sha(f"refs/remotes/origin/{SYNC_BRANCH}")
        if not is_ancestor(branch_sha, base):
            start = branch_sha
    git("checkout", "--detach", start)
    git("config", "user.name", "github-actions[bot]")
    git("config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com")

    for ref, label in ((base, "合并本项目 main 到同步分支"), (upstream, "合并上游到中文版")):
        if is_ancestor(ref, "HEAD"):
            continue
        conflicts = merge(ref)
        if conflicts:
            api.report_problem(
                f"{label}时发生冲突，自动合并已撤销，现有远程分支保持不变。\n\n"
                + "\n".join(f"- `{path}`" for path in conflicts), base, upstream,
            )
            raise RuntimeError("存在合并冲突，请处理跟踪 Issue")

    candidate = sha("HEAD")
    # Ordinary fast-forward push preserves any concurrent or manual branch updates.
    try:
        git("push", ORIGIN_URL, f"{candidate}:refs/heads/{SYNC_BRANCH}")
        pull_number = api.prepare_pull_request(base, upstream, candidate)
    except RuntimeError as error:
        api.report_problem(
            "准备同步 PR 失败。请检查仓库写入规则及 Settings → Actions → General → "
            "Allow GitHub Actions to create and approve pull requests。\n\n"
            f"错误：{error}", base, upstream,
        )
        raise

    issue = api.tracking_issue()
    output("tracking_issue_number", str(issue["number"]) if issue and issue["state"] == "open" else "")
    output("candidate_sha", candidate)
    output("pr_number", str(pull_number))
    output("should_build", "true")
    summary(
        f"### 候选提交已准备\n\n上游：`{upstream}`\n\n待构建：`{candidate}`\n\n"
        "后续只读作业将构建该提交；通过后仅尝试快进本仓库 main。"
    )


def main() -> int:
    try:
        token = os.environ.get("GH_TOKEN")
        if not token:
            raise RuntimeError("缺少 GitHub Actions 内置令牌 GH_TOKEN")
        prepare(RepositoryAPI(token))
        return 0
    except (RuntimeError, OSError) as error:
        # Workflow-command escaping keeps API/git text from injecting annotations.
        escaped = str(error).replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
        print(f"::error::{escaped}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
